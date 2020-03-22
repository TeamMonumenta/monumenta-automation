#![allow(non_snake_case)]

use std::fs::File;
use std::collections::HashMap;
use std::io::{Read};

use nbt;

#[derive(Debug)]
struct Scoreboard {
    filepath: String,
    DataVersion: i32,
    objectives: HashMap<String, Objective>,
}

#[derive(Debug)]
struct Score {
    Score: i32,
    Locked: bool,
}

#[derive(Debug)]
struct Objective {
    RenderType: String,
    DisplayName: String,
    CriteriaName: String,
    data: HashMap<String, Score>,
}

/* TODO: This really needs to return some kind of error string instead of panic'ing */
impl Scoreboard {
    fn load(filepath: &str) -> Result<Scoreboard, String> {
        let mut file = File::open(filepath).unwrap();
        let mut contents = Vec::new();
        file.read_to_end(&mut contents).unwrap();
        let mut src = std::io::Cursor::new(&contents[..]);
        let blob = nbt::Blob::from_gzip_reader(&mut src).unwrap();

        let DataVersion: i32 = if let Some(nbt::Value::Int(DataVersion)) = blob.get("DataVersion") { *DataVersion } else { panic!("Scoreboard missing DataVersion") };

        let mut scoreboard = Scoreboard{filepath: filepath.to_string(), DataVersion: DataVersion, objectives: HashMap::new()};

        if let Some(nbt::Value::Compound(data)) = blob.get("data") {
            if let Some(nbt::Value::List(objectives)) = data.get("Objectives") {
                for objectives_entry in objectives.iter() {
                    if let nbt::Value::Compound(objective) = objectives_entry {
                        let Name: String = if let Some(nbt::Value::String(Name)) = objective.get("Name") { Name.to_string() } else { panic!("Objective missing Name") };

                        let new_objective = Objective {
                            CriteriaName: if let Some(nbt::Value::String(CriteriaName)) = objective.get("CriteriaName") { CriteriaName.to_string() } else { panic!("Objective missing CriteriaName") },
                            DisplayName: if let Some(nbt::Value::String(DisplayName)) = objective.get("DisplayName") { DisplayName.to_string() } else { panic!("Objective missing DisplayName") },
                            RenderType: if let Some(nbt::Value::String(RenderType)) = objective.get("RenderType") { RenderType.to_string() } else { panic!("Objective missing RenderType") },
                            data: HashMap::new(),
                        };

                        scoreboard.objectives.insert(Name, new_objective);
                    }
                }
            } else {
                panic!("Scoreboard data missing Objectives");
            }
            if let Some(nbt::Value::List(PlayerScores)) = data.get("PlayerScores") {
                for player_score_entry in PlayerScores.iter() {
                    if let nbt::Value::Compound(score) = player_score_entry {
                        let Name: String = if let Some(nbt::Value::String(Name)) = score.get("Name") { Name.to_string() } else { panic!("Score missing Name") };
                        let Objective: String = if let Some(nbt::Value::String(Objective)) = score.get("Objective") { Objective.to_string() } else { panic!("Score missing Objective") };
                        let Score: i32 = if let Some(nbt::Value::Int(Score)) = score.get("Score") { *Score } else { panic!("Score missing Score") };
                        let Locked: bool = if let Some(nbt::Value::Byte(Locked)) = score.get("Locked") { *Locked != 0 } else { panic!("Score missing Locked") };

                        scoreboard.set_score(Name, Objective, Score{ Score: Score, Locked: Locked })?;
                    }
                }
            } else {
                panic!("Scoreboard data missing PlayerScores");
            }
            /* TODO: Also load Teams, DisplaySlots */
        } else {
            panic!("Scoreboard data missing data");
        }

        Ok(scoreboard)
    }

    fn set_score(&mut self, Name: String, Objective: String, Score: Score) -> Result<(), String> {
        if let Some(Objective) = self.objectives.get_mut(&Objective) {
            Objective.data.insert(Name, Score);
        } else {
            panic!("Can't insert score into missing objective {}", Objective);
        }

        Ok(())
    }
}

use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::fs::File;
use std::collections::HashMap;
use std::io::{Read};

use nbt;

#[derive(Debug)]
pub struct Scoreboard {
    filepath: String,
    data_version: i32, // DataVersion
    pub objectives: HashMap<String, Objective>,
}

#[derive(Debug)]
pub struct Score {
    pub score: i32, // Score
    pub locked: bool, // Locked
}

#[derive(Debug)]
pub struct Objective {
    pub render_type: String, // RenderType
    pub display_name: String, // DisplayName
    pub criteria_name: String, // CriteriaName
    pub data: HashMap<String, Score>,
}

impl Scoreboard {
    pub fn load(filepath: &str) -> BoxResult<Scoreboard> {
        let mut file = File::open(filepath).unwrap();
        let mut contents = Vec::new();
        file.read_to_end(&mut contents).unwrap();
        let mut src = std::io::Cursor::new(&contents[..]);
        let blob = nbt::Blob::from_gzip_reader(&mut src).unwrap();

        let data_version: i32 = if let Some(nbt::Value::Int(data_version)) = blob.get("DataVersion") { *data_version } else { bail!("Scoreboard missing DataVersion") };

        let mut scoreboard = Scoreboard{filepath: filepath.to_string(), data_version: data_version, objectives: HashMap::new()};

        if let Some(nbt::Value::Compound(data)) = blob.get("data") {
            if let Some(nbt::Value::List(objectives)) = data.get("Objectives") {
                for objectives_entry in objectives.iter() {
                    if let nbt::Value::Compound(objective) = objectives_entry {
                        let name: String = if let Some(nbt::Value::String(name)) = objective.get("Name") { name.to_string() } else { bail!("Objective missing Name") };

                        let new_objective = Objective {
                            criteria_name: if let Some(nbt::Value::String(criteria_name)) = objective.get("CriteriaName") { criteria_name.to_string() } else { bail!("Objective missing CriteriaName") },
                            display_name: if let Some(nbt::Value::String(display_name)) = objective.get("DisplayName") { display_name.to_string() } else { bail!("Objective missing DisplayName") },
                            render_type: if let Some(nbt::Value::String(render_type)) = objective.get("RenderType") { render_type.to_string() } else { bail!("Objective missing RenderType") },
                            data: HashMap::new(),
                        };

                        scoreboard.objectives.insert(name, new_objective);
                    }
                }
            } else {
                bail!("Scoreboard data missing Objectives");
            }
            if let Some(nbt::Value::List(player_scores)) = data.get("PlayerScores") {
                for player_score_entry in player_scores.iter() {
                    if let nbt::Value::Compound(score_compound) = player_score_entry {
                        let name: String = if let Some(nbt::Value::String(name)) = score_compound.get("Name") { name.to_string() } else { bail!("Score missing Name") };
                        let objective: String = if let Some(nbt::Value::String(objective)) = score_compound.get("Objective") { objective.to_string() } else { bail!("Score missing Objective") };
                        let score: i32 = if let Some(nbt::Value::Int(score)) = score_compound.get("Score") { *score } else { bail!("Score missing Score") };
                        let locked: bool = if let Some(nbt::Value::Byte(locked)) = score_compound.get("Locked") { *locked != 0 } else { bail!("Score missing Locked") };

                        scoreboard.set_score(name, objective, Score{ score: score, locked: locked })?;
                    }
                }
            } else {
                bail!("Scoreboard data missing PlayerScores");
            }
            /* TODO: Also load Teams, DisplaySlots */
        } else {
            bail!("Scoreboard data missing data");
        }

        Ok(scoreboard)
    }

    fn set_score(&mut self, name: String, objective: String, score: Score) -> Result<(), String> {
        if let Some(objective) = self.objectives.get_mut(&objective) {
            objective.data.insert(name, score);
        } else {
            panic!("Can't insert score into missing objective {}", objective);
        }

        Ok(())
    }
}

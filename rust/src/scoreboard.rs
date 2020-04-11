use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::fs::File;
use std::collections::HashMap;
use std::collections::HashSet;
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

pub struct ScoreboardCollection {
    pub scoreboards: HashMap<String, Scoreboard>,
    objectives: HashSet<String>,
}

impl ScoreboardCollection {
    pub fn new() -> ScoreboardCollection {
        ScoreboardCollection{ scoreboards: HashMap::new(), objectives: HashSet::new() }
    }

    pub fn add_scoreboard(&mut self, filepath: &str) -> BoxResult<()> {
        let scoreboard = Scoreboard::load(filepath)?;

        for objective_name in scoreboard.objectives.keys() {
            self.objectives.insert(objective_name.to_string());
        }

        self.scoreboards.insert(filepath.to_string(), scoreboard);

        Ok(())
    }

    pub fn objectives(&self) -> &HashSet<String> {
        &self.objectives
    }

    pub fn get_objective_usage(&self) -> HashMap<String, f64> {
        /*
         * Iterate over all scoreboards and accumulate the nonzero_count and total_entries for each
         * objective
         *
         * key = objective name
         * val = (nonzero_count, total_entries)
         */
        let mut counts: HashMap<String, (i32, i32)> = HashMap::new();

        for (_, scoreboard) in self.scoreboards.iter() {
            for (objective_name, objective) in scoreboard.objectives.iter() {
                let mut nonzero_count = 0;
                let mut total_entries = 0;

                /* Retrieve stored values from the hash table if they are present */
                if let Some((stored_nonzero_count, stored_total_entries)) = counts.get(objective_name) {
                    nonzero_count = *stored_nonzero_count;
                    total_entries = *stored_total_entries;
                }

                for (_, score) in objective.data.iter() {
                    total_entries += 1;
                    if score.score != 0 {
                        nonzero_count += 1
                    }
                }

                /*
                 * This avoids 0/0 later. Just assume each objective had at least one item in it that
                 * was 0
                 */
                if total_entries == 0 {
                    total_entries = 1;
                }

                counts.insert(objective_name.to_string(), (nonzero_count, total_entries));
            }
        }

        counts.iter().map(|(objective_name, (nonzero_count, total_entries))| (objective_name.to_string(), *nonzero_count as f64 / *total_entries as f64)).collect()
    }

    pub fn get_objective_usage_sorted(&self) -> Vec<(String, f64)> {

        /* Create a vector from the hash table data and sort it by value */
        let mut count_vec: Vec<(String, f64)> = self.get_objective_usage().iter().map(|(a, b)| (a.clone(), b.clone())).collect();
        count_vec.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

        count_vec
    }
}

impl Scoreboard {
    pub fn load(filepath: &str) -> BoxResult<Scoreboard> {
        let mut file = File::open(filepath)?;
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

    pub fn set_score(&mut self, name: String, objective: String, score: Score) -> Result<(), String> {
        if let Some(objective) = self.objectives.get_mut(&objective) {
            objective.data.insert(name, score);
        } else {
            panic!("Can't insert score into missing objective {}", objective);
        }

        Ok(())
    }

    pub fn get_player_scores(&self, player_name: &str) -> HashMap<String, i32> {
        let mut data: HashMap<String, i32> = HashMap::new();

        for (objective_name, objective) in self.objectives.iter() {
            if let Some(score) = objective.data.get(player_name) {
                data.insert(objective_name.to_string(), score.score);
            }
        }

        data
    }
}

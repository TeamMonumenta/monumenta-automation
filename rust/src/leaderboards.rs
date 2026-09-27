use std::{collections::HashSet, fs::File, io};

use serde::Deserialize;
use walkdir::WalkDir;

#[derive(Deserialize)]
pub struct LeaderboardConfig {
    pub objective: String,
    pub plain_display_name: String,
    pub category: Option<String>,
    pub release: Option<String>,
}

pub fn load_configs(dir: &str) -> anyhow::Result<Vec<LeaderboardConfig>> {
    let mut res: Vec<LeaderboardConfig> = Vec::new();
    let mut seen: HashSet<String> = HashSet::new();

    for entry in WalkDir::new(dir) {
        let entry = entry?;

        if entry.file_type().is_file() && entry.path().extension().is_some_and(|ext| ext == "json") {
            let file = File::open(entry.path())?;
            let cfg: LeaderboardConfig = serde_json::from_reader(io::BufReader::new(file))?;

            // Skip duplicate entries (there shouldn't be any, but just in case)
            if seen.contains(&cfg.objective) {
                continue;
            }

            seen.insert(cfg.objective.clone());

            res.push(cfg);
        }
    }

    return Ok(res);
}

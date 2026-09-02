use anyhow::{self, bail};

use std::{fs::File, io::Read};

#[derive(Clone)]
pub struct Stats(serde_json::Map<String, serde_json::Value>);

impl Stats {
    pub fn load_from_file(file: &mut File) -> anyhow::Result<Stats> {
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;

        Stats::load_from_string(&contents)
    }

    pub fn load_from_string(data: &str) -> anyhow::Result<Stats> {
        if let Ok(serde_json::Value::Object(stats)) = serde_json::from_str(data) {
            Ok(Stats(stats))
        } else {
            bail!("Failed to parse stats data as JSON object");
        }
    }

    pub fn to_string(&self) -> String {
        serde_json::to_string(&self.0).unwrap()
    }

    pub fn to_string_pretty(&self) -> String {
        serde_json::to_string_pretty(&self.0).unwrap()
    }
}

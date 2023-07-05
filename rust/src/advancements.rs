use anyhow::{self, bail};
use std::fs::File;
use std::io::Read;

type BoxResult<T> = Result<T, anyhow::Error>;

#[derive(Clone)]
pub struct Advancements(serde_json::Map<String, serde_json::Value>);

impl Advancements {
    pub fn load_from_file(file: &mut File) -> BoxResult<Advancements> {
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;

        Advancements::load_from_string(&contents)
    }

    pub fn load_from_string(data: &str) -> BoxResult<Advancements> {
        if let Ok(serde_json::Value::Object(advancements)) = serde_json::from_str(data) {
            Ok(Advancements(advancements))
        } else {
            bail!("Failed to parse advancements data as JSON object");
        }
    }

    pub fn to_string(&self) -> String {
        serde_json::to_string(&self.0).unwrap()
    }

    pub fn to_string_pretty(&self) -> String {
        serde_json::to_string_pretty(&self.0).unwrap()
    }
}

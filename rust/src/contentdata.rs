use anyhow::{self, bail};

#[derive(Clone)]
pub struct ContentData(serde_json::Map<String, serde_json::Value>);

impl ContentData {
    pub fn new() -> ContentData {
        let mut result: ContentData = ContentData{0:serde_json::map::Map::new()};
        result.0.insert("id".to_string(), "".into());
        result
    }

    pub fn load_from_string(data: &str) -> anyhow::Result<ContentData> {
        if let Ok(serde_json::Value::Object(contentData)) = serde_json::from_str(data) {
            Ok(ContentData(contentData))
        } else {
            bail!("Failed to parse content data as JSON object");
        }
    }

    pub fn get_id(&self) -> String {
        if let Some(id) = (&self.0).get("id") {
            return match id {
                serde_json::Value::String(id) => (*id).clone(),
                _ => "".to_string(),
            }
        } else {
            return "".to_string();
        }
    }

    pub fn set_id(&mut self, new_id: &str) {
        &self.0.clear();
        &self.0.insert("id".to_string(), new_id.into());
    }

    pub fn to_string(&self) -> String {
        serde_json::to_string(&self.0).unwrap()
    }

    pub fn to_string_pretty(&self) -> String {
        serde_json::to_string_pretty(&self.0).unwrap()
    }
}

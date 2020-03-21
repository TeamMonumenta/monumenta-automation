
use std::fmt;
use walkdir::WalkDir;
use std::fs;
use std::collections::HashMap;


#[derive(PartialEq, Eq, Hash)]
struct NamespacedKey {
    namespace: String,
    key: String,
}

impl NamespacedKey {
    fn from_path(path: &str) -> Option<NamespacedKey> {
        let path = path.trim_start_matches("/");

        if path.starts_with("data") {
            let path = path.trim_start_matches("data").trim_start_matches("/");

            let split: Vec<&str> = path.splitn(2, "/").collect();
            if split.len() == 2 {
                let namespace = split[0];
                let key = split[1];

                if key.ends_with(".json") && key.starts_with("advancements") {
                    return Some(NamespacedKey{namespace: namespace.to_string(), key: key.trim_start_matches("advancements/").trim_end_matches(".json").to_string()});
                } else if key.ends_with(".mcfunction") && key.starts_with("functions") {
                    return Some(NamespacedKey{namespace: namespace.to_string(), key: key.trim_start_matches("functions/").trim_end_matches(".mcfunction").to_string()});
                }
            }
        }

        None
    }

    fn from_str(path: &str) -> Option<NamespacedKey> {
        let split: Vec<&str> = path.splitn(2, ":").collect();
        if split.len() == 2 {
            return Some(NamespacedKey{namespace: split[0].to_string(), key: split[1].to_string()});
        }

        None
    }
}

impl fmt::Display for NamespacedKey {
    fn fmt(&self, f: &mut fmt::Formatter) -> std::result::Result<(), std::fmt::Error> {
        write!(f, "{}:{}", self.namespace, self.key)
    }
}

impl fmt::Debug for NamespacedKey {
    fn fmt(&self, f: &mut fmt::Formatter) -> std::result::Result<(), std::fmt::Error> {
        write!(f, "{}:{}", self.namespace, self.key)
    }
}

#[derive(Debug)]
struct Advancement {
    path: String,
    parent: Option<NamespacedKey>,
    children: Vec<*mut NamespacedItem>,
    used: bool,
    data: serde_json::value::Value
}

#[derive(Debug)]
struct Function {
    path: String,
    children: Vec<*mut NamespacedItem>,
    used: bool,
    data: String
}

#[derive(Debug)]
enum NamespacedItem {
    Advancement(Advancement),
    Function(Function)
}

fn get_function<'c>(advancement: &'c serde_json::Value) -> Option<NamespacedKey> {
    if let Some(serde_json::Value::Object(rewards)) = advancement.get("rewards") {
        if let Some(serde_json::Value::String(function)) = rewards.get("function") {
            return NamespacedKey::from_str(function);
        }
    }
    None
}

fn load_file(path: String,
             datapacks_path: &str) -> Option<(NamespacedKey, NamespacedItem)> {

    if let Ok(file) = fs::read_to_string(&path) {
        if path.ends_with(".json") {
            let json: serde_json::Value = serde_json::from_str(&file).expect(&format!("Failed to parse file as json: {}", file));

            if let Some(namespace) = NamespacedKey::from_path(path.trim_start_matches(datapacks_path)) {
                return Some((namespace, NamespacedItem::Advancement(Advancement{ path: path, parent: None, children: vec!(), used: false, data: json })))
            }
        } else if path.ends_with(".mcfunction") {
            if let Some(namespace) = NamespacedKey::from_path(path.trim_start_matches(datapacks_path)) {
                return Some((namespace, NamespacedItem::Function(Function{ path: path, children: vec!(), used: false, data: file })))
            }
        }
    } else {
        println!("Warning: Failed to open file: {}", &path);
    }

    None
}

fn main() {
    let dir = "/home/bmarohn/home/datapacks/region_1";

    let mut advancements: HashMap<NamespacedKey, NamespacedItem> = HashMap::new();
    let mut functions: HashMap<NamespacedKey, NamespacedItem> = HashMap::new();

    /* Load files into the advancements/functions maps */
    for entry in WalkDir::new(dir).follow_links(true) {
        if let Ok(entry) = entry {
            if entry.path().is_file() {
                if let Some((namespace, item)) = load_file(entry.path().to_str().unwrap().to_string(), dir) {
                    match item {
                        /* TODO: Handle overlaps from different datapacks ? */
                        NamespacedItem::Advancement(_) => { advancements.insert(namespace, item); }
                        NamespacedItem::Function(_) => { functions.insert(namespace, item); }
                    };
                }
            }
        }
    }

    println!("\n");

    /* Create reference links for advancements */
    for (_key, val) in advancements.iter_mut() {
        if let NamespacedItem::Advancement(advancement) = val {
            /* Link to parent advancement - mostly just interesting, not actually used */
            if let Some(serde_json::Value::String(parent)) = advancement.data.get("parent") {
                advancement.parent = NamespacedKey::from_str(parent);
            }

            /* Link to function */
            if let Some(run_func) = get_function(&advancement.data) {
                if let Some(function) = functions.get_mut(&run_func) {
                    let raw_function: *mut _ = &mut *function;
                    advancement.children.push(raw_function);
                }
            }

            /* Mark as used by default unless it has an impossible trigger */
            advancement.used = true;
            if let Some(serde_json::Value::Object(criteria)) = advancement.data.get("criteria") {
                for (_c_key, c_value) in criteria.iter() {
                    if let Some(serde_json::Value::String(trigger)) = c_value.get("trigger") {
                        if trigger == "minecraft:impossible" {
                            advancement.used = false;
                        }
                    }
                }
            }
        }
    }

    /* Create reference links for functions */
    for (_, val) in functions.iter_mut() {
        if let NamespacedItem::Function(function) = val {
            for line in function.data.lines() {


            }
            /* Need to handle function and schedule function */
        }
    }
}

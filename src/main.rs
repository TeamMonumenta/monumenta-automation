#[macro_use] extern crate log;
#[macro_use] extern crate lazy_static;

use std::env;
use std::fmt;
use walkdir::WalkDir;
use std::fs;
use std::collections::HashMap;
use regex::Regex;
use simplelog::*;

#[derive(PartialEq, Eq, Hash, Clone)]
enum NamespaceType {
    Advancement,
    Function
}

#[derive(PartialEq, Eq, Hash, Clone)]
struct NamespacedKey {
    key_type: NamespaceType,
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
                    return Some(NamespacedKey{key_type: NamespaceType::Advancement, namespace: namespace.to_string(), key: key.trim_start_matches("advancements/").trim_end_matches(".json").to_string()});
                } else if key.ends_with(".mcfunction") && key.starts_with("functions") {
                    return Some(NamespacedKey{key_type: NamespaceType::Function, namespace: namespace.to_string(), key: key.trim_start_matches("functions/").trim_end_matches(".mcfunction").to_string()});
                }
            }
        } else {
            error!("Error: Datapack does not contain 'data' subfolder!");
            panic!()
        }

        None
    }

    fn from_str(path: &str, key_type: NamespaceType) -> Option<NamespacedKey> {
        let split: Vec<&str> = path.splitn(2, ":").collect();
        if split.len() == 2 {
            return Some(NamespacedKey{key_type: key_type, namespace: split[0].to_string(), key: split[1].to_string()});
        }

        None
    }
}

impl fmt::Display for NamespacedKey {
    fn fmt(&self, f: &mut fmt::Formatter) -> std::result::Result<(), std::fmt::Error> {
        match self.key_type {
            NamespaceType::Advancement => write!(f, "advancement({}:{})", self.namespace, self.key),
            NamespaceType::Function => write!(f, "function({}:{})", self.namespace, self.key)
        }
    }
}

impl fmt::Debug for NamespacedKey {
    fn fmt(&self, f: &mut fmt::Formatter) -> std::result::Result<(), std::fmt::Error> {
        match self.key_type {
            NamespaceType::Advancement => write!(f, "advancement({}:{})", self.namespace, self.key),
            NamespaceType::Function => write!(f, "function({}:{})", self.namespace, self.key)
        }
    }
}

#[derive(Debug)]
struct Advancement {
    path: String,
    parent: Option<NamespacedKey>,
    children: Vec<NamespacedKey>,
    used: bool,
    data: serde_json::value::Value
}

#[derive(Debug)]
struct Function {
    path: String,
    children: Vec<NamespacedKey>,
    used: bool,
    data: String
}

#[derive(Debug)]
enum NamespacedItem {
    Advancement(Advancement),
    Function(Function)
}

impl NamespacedItem {
    fn get_children(&self) -> &Vec<NamespacedKey> {
        match self {
            NamespacedItem::Advancement(advancement) => &advancement.children,
            NamespacedItem::Function(function) => &function.children,
        }
    }

    fn get_path(&self) -> &str {
        match self {
            NamespacedItem::Advancement(advancement) => &advancement.path,
            NamespacedItem::Function(function) => &function.path,
        }
    }

    fn is_used(&self) -> bool {
        match self {
            NamespacedItem::Advancement(advancement) => advancement.used,
            NamespacedItem::Function(function) => function.used,
        }
    }

    fn set_used(&mut self, val: bool) {
        match self {
            NamespacedItem::Advancement(advancement) => advancement.used = val,
            NamespacedItem::Function(function) => function.used = val,
        }
    }
}

fn get_function<'c>(advancement: &'c serde_json::Value) -> Option<NamespacedKey> {
    if let Some(serde_json::Value::Object(rewards)) = advancement.get("rewards") {
        if let Some(serde_json::Value::String(function)) = rewards.get("function") {
            return NamespacedKey::from_str(function, NamespaceType::Function);
        }
    }
    None
}

fn load_file(path: String,
             datapacks_path: &str) -> Option<(NamespacedKey, NamespacedItem)> {

    if let Ok(file) = fs::read_to_string(&path) {
        if path.ends_with(".json") {
            if let Ok(json) = serde_json::from_str(&file) {
                if let Some(namespace) = NamespacedKey::from_path(path.trim_start_matches(datapacks_path)) {
                    return Some((namespace, NamespacedItem::Advancement(Advancement{ path: path, parent: None, children: vec!(), used: false, data: json })))
                }
            } else {
                warn!("Failed to parse file as json: {}", path);
            }
        } else if path.ends_with(".mcfunction") {
            if let Some(namespace) = NamespacedKey::from_path(path.trim_start_matches(datapacks_path)) {
                return Some((namespace, NamespacedItem::Function(Function{ path: path, children: vec!(), used: false, data: file })))
            }
        }
    } else {
        warn!("Failed to read file as string: {}", &path);
    }

    None
}

fn load_datapack(items: &mut HashMap<NamespacedKey, NamespacedItem>,
                 pending: &mut Vec<NamespacedKey>,
                 dir: &str) {
    lazy_static! {
        static ref RE_FUNC: Regex = Regex::new(r"function [a-z][^ :]*:[a-z][^ :]*").unwrap();
        static ref RE_ADV: Regex = Regex::new(r"advancement (grant|revoke) .* (everything|from|only|through|until) [a-z][^ :]*:[a-z][^ :]*").unwrap();
        static ref RE_ADV_ONLY: Regex = Regex::new(r" only [a-z][^ :]*:[a-z][^ :]*").unwrap();
    }

    /* Load files into the advancements/functions maps */
    for entry in WalkDir::new(dir).follow_links(true) {
        if let Ok(entry) = entry {
            if entry.path().is_file() {
                if let Some((namespace, item)) = load_file(entry.path().to_str().unwrap().to_string(), dir) {
                    /* TODO: Handle overlaps from different datapacks ? */
                    items.insert(namespace, item);
                }
            }
        }
    }

    /* Create links between the various files */
    for (key, val) in items.iter_mut() {
        match val {
            NamespacedItem::Advancement(advancement) => {
                /* Create reference links for advancements */

                /* Link to parent advancement - mostly just interesting, not actually used */
                if let Some(serde_json::Value::String(parent)) = advancement.data.get("parent") {
                    advancement.parent = NamespacedKey::from_str(parent, NamespaceType::Advancement);
                }

                /* Link to function */
                if let Some(run_func) = get_function(&advancement.data) {
                    advancement.children.push(run_func);
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

                if advancement.used {
                    /* Advancement is used - push it and its children to the pending list */
                    pending.push(key.clone());
                    pending.extend(advancement.children.iter().cloned());
                }
            }
            NamespacedItem::Function(function) => {
                /* Create reference links for functions */
                for line in function.data.lines() {

                    /* Link functions to the other functions they call */
                    /* Schedule function and function both have the same syntax, so one match will do */
                    if let Some(func_match) = RE_FUNC.find(line) {
                        if let Some(key) = NamespacedKey::from_str(func_match.as_str().trim_start_matches("function "), NamespaceType::Function) {
                            function.children.push(key);
                        }
                    }

                    /* Link functions to advancements */
                    if let Some(adv_match) = RE_ADV.find(line) {
                        if let Some(adv_only_match) = RE_ADV_ONLY.find(adv_match.as_str()) {
                            if let Some(key) = NamespacedKey::from_str(adv_only_match.as_str().trim_start_matches(" only "), NamespaceType::Advancement) {
                                function.children.push(key);
                            }
                        } else {
                            warn!("No support for advancement command {}", adv_match.as_str());
                        }
                    }
                }
            }
        }
    }



}

fn main() {
    CombinedLogger::init(
        vec![
            TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed).unwrap(),
        ]
    ).unwrap();

    /* A map of all of the advancements and functions that have been loaded */
    let mut items: HashMap<NamespacedKey, NamespacedItem> = HashMap::new();

    /* A list of all the namespaced keys that are used but have not yet had their children processed */
    let mut pending: Vec<NamespacedKey> = Vec::new();

    /* Load all the arguments as datapacks */
    let mut args: Vec<String> = env::args().collect();

    if args.len() <= 1 {
        error!("Usage: {} path/to/datapack path/to/other_datapack ...", args.get(0).unwrap());
        return
    }

    args.remove(0);
    while let Some(arg) = args.pop() {
        load_datapack(&mut items, &mut pending, &arg);
    }

    /* Iterate through the pending list and mark things as used */
    while pending.len() > 0 {
        let key = pending.pop().unwrap();
        if let Some(map_value) = items.get_mut(&key) {
            /*
             * Only do work on nodes not marked as used. If a node is already
             * marked as used, it has either already had its children marked
             * or it is in the pending list
             */
            if !map_value.is_used() {
                map_value.set_used(true);
                /* Copy the children into the pending list */
                pending.extend(map_value.get_children().iter().cloned());
            }
        } else {
            warn!("Missing item {}", key);
        }
    }

    println!("\nUsed:");

    for (_, val) in items.iter() {
        if val.is_used() {
            println!("{}", val.get_path());
        }
    }

}

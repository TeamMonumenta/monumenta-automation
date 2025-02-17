use monumenta::scoreboard::Scoreboard;
use monumenta::scoreboard::ScoreboardCollection;

use anyhow::{self, bail};
use lazy_static::lazy_static;
use log::{info, error, warn};
use regex::Regex;
use simplelog::*;
use walkdir::WalkDir;

use std::{
    collections::HashMap,
    env,
    fmt,
    fs
};

#[derive(PartialEq, Eq, Hash, Clone)]
enum NamespaceType {
    Advancement,
    Function,
    Quest,
    Command,
}

#[derive(PartialEq, Eq, Hash, Clone)]
struct NamespacedKey {
    key_type: NamespaceType,
    namespace: String,
    key: String,
}

impl NamespacedKey {
    fn from_path(path: &str) -> anyhow::Result<NamespacedKey> {
        let path = path.trim_start_matches("/");

        if path.starts_with("data") {
            /* Assume it is a datapack entry */
            let path = path.trim_start_matches("data").trim_start_matches("/");

            let split: Vec<&str> = path.splitn(2, "/").collect();
            if split.len() == 2 {
                let namespace = split[0];
                let key = split[1];

                if key.ends_with(".json") && key.starts_with("advancements") {
                    return Ok(NamespacedKey{key_type: NamespaceType::Advancement, namespace: namespace.to_string(), key: key.trim_start_matches("advancements/").trim_end_matches(".json").to_string()});
                } else if key.ends_with(".mcfunction") && key.starts_with("functions") {
                    return Ok(NamespacedKey{key_type: NamespaceType::Function, namespace: namespace.to_string(), key: key.trim_start_matches("functions/").trim_end_matches(".mcfunction").to_string()});
                }
            }
        } else if path.ends_with(".json") {
            /* Assume it is a quest */
            let split: Vec<&str> = path.splitn(2, "/").collect();
            if split.len() == 2 {
                let namespace = split[0];
                let key = split[1];

                if key.ends_with(".json") {
                    return Ok(NamespacedKey{key_type: NamespaceType::Quest, namespace: namespace.to_string(), key: key.trim_end_matches(".json").to_string()});
                }
            }
        }
        bail!("Failed to convert path {} to NamespacedKey", path);
    }

    fn from_str(path: &str, key_type: NamespaceType) -> anyhow::Result<NamespacedKey> {
        let split: Vec<&str> = path.splitn(2, ":").collect();
        if split.len() == 2 {
            return Ok(NamespacedKey{key_type: key_type, namespace: split[0].to_string(), key: split[1].to_string()});
        }
        bail!("Failed to split string {} on ':'", path);
    }

    fn from_command(world: &str, coords: &str) -> NamespacedKey {
        NamespacedKey{ key_type: NamespaceType::Command, namespace: world.to_string(), key: coords.to_string() }
    }
}

impl fmt::Display for NamespacedKey {
    fn fmt(&self, f: &mut fmt::Formatter) -> std::result::Result<(), std::fmt::Error> {
        match self.key_type {
            NamespaceType::Advancement => write!(f, "advancement({}:{})", self.namespace, self.key),
            NamespaceType::Function => write!(f, "function({}:{})", self.namespace, self.key),
            NamespaceType::Quest => write!(f, "quest({}:{})", self.namespace, self.key),
            NamespaceType::Command => write!(f, "command({}:{})", self.namespace, self.key),
        }
    }
}

impl fmt::Debug for NamespacedKey {
    fn fmt(&self, f: &mut fmt::Formatter) -> std::result::Result<(), std::fmt::Error> {
        match self.key_type {
            NamespaceType::Advancement => write!(f, "advancement({}:{})", self.namespace, self.key),
            NamespaceType::Function => write!(f, "function({}:{})", self.namespace, self.key),
            NamespaceType::Quest => write!(f, "quest({}:{})", self.namespace, self.key),
            NamespaceType::Command => write!(f, "command({}:{})", self.namespace, self.key),
        }
    }
}

#[derive(Debug)]
struct Advancement {
    path: Vec<String>,
    children: Vec<NamespacedKey>,
    used: bool,
    data: Vec<String>,
    json_data: Vec<serde_json::value::Value>,
}

#[derive(Debug)]
struct Function {
    path: Vec<String>,
    children: Vec<NamespacedKey>,
    used: bool,
    data: Vec<String>,
}

#[derive(Debug)]
struct Quest {
    path: Vec<String>,
    children: Vec<NamespacedKey>,
    used: bool, /* TODO: Currently always true! */
    data: Vec<String>,
    json_data: serde_json::value::Value,
}

#[derive(Debug)]
struct Command {
    path: Vec<String>,
    children: Vec<NamespacedKey>,
    data: Vec<String>, /* Commands can be at the same location if in a chest */
}

#[derive(Debug)]
enum NamespacedItem {
    Advancement(Advancement),
    Function(Function),
    Quest(Quest),
    Command(Command),
}

impl NamespacedItem {
    fn get_children(&self) -> &Vec<NamespacedKey> {
        match self {
            NamespacedItem::Advancement(advancement) => &advancement.children,
            NamespacedItem::Function(function) => &function.children,
            NamespacedItem::Quest(quest) => &quest.children,
            NamespacedItem::Command(command) => &command.children,
        }
    }

    fn add_variant(&mut self, variant: NamespacedItem) {
        match self {
            NamespacedItem::Advancement(inner) => {
                if let NamespacedItem::Advancement(var_inner) = variant {
                    inner.path.extend(var_inner.path.iter().cloned());
                    inner.data.extend(var_inner.data.iter().cloned());
                    inner.json_data.extend(var_inner.json_data.iter().cloned());
                } else {
                    panic!("Advancement and other with same namespace!");
                }
            }
            NamespacedItem::Function(inner) => {
                if let NamespacedItem::Function(var_inner) = variant {
                    inner.path.extend(var_inner.path.iter().cloned());
                    inner.data.extend(var_inner.data.iter().cloned());
                } else {
                    panic!("Function and other with same namespace!");
                }
            }
            inner @ NamespacedItem::Quest(_) => {
                panic!("Conflicting quests found! {:?} and {:?}", inner.get_paths(), variant.get_paths());
            }
            NamespacedItem::Command(inner) => {
                if let NamespacedItem::Command(var_inner) = variant {
                    inner.path.extend(var_inner.path.iter().cloned());
                    inner.data.extend(var_inner.data.iter().cloned());
                } else {
                    panic!("Command and other with same namespace!");
                }
            }
        }
    }

    fn get_paths(&self) -> &Vec<String> {
        match self {
            NamespacedItem::Advancement(advancement) => &advancement.path,
            NamespacedItem::Function(function) => &function.path,
            NamespacedItem::Quest(quest) => &quest.path,
            NamespacedItem::Command(command) => &command.path,
        }
    }

    fn get_data(&self) -> &Vec<String> {
        match self {
            NamespacedItem::Advancement(advancement) => &advancement.data,
            NamespacedItem::Function(function) => &function.data,
            NamespacedItem::Quest(quest) => &quest.data,
            NamespacedItem::Command(command) => &command.data,
        }
    }

    fn is_used(&self) -> bool {
        match self {
            NamespacedItem::Advancement(advancement) => advancement.used,
            NamespacedItem::Function(function) => function.used,
            NamespacedItem::Quest(quest) => quest.used,
            NamespacedItem::Command(_) => true,
        }
    }

    fn set_used(&mut self, val: bool) {
        match self {
            NamespacedItem::Advancement(advancement) => advancement.used = val,
            NamespacedItem::Function(function) => function.used = val,
            NamespacedItem::Quest(quest) => quest.used = val,
            NamespacedItem::Command(_) => (),
        }
    }
}

fn get_function<'c>(advancement: &'c serde_json::Value) -> Option<NamespacedKey> {
    if let Some(serde_json::Value::Object(rewards)) = advancement.get("rewards") {
        if let Some(serde_json::Value::String(function)) = rewards.get("function") {
            if let Ok(ns_key) = NamespacedKey::from_str(function, NamespaceType::Function) {
                return Some(ns_key);
            } else {
                warn!("Advancement contains unparseable reward function {}", function);
            }
        }
    }
    None
}

fn load_datapack_file(path: String, datapacks_path: &str) -> anyhow::Result<Option<(NamespacedKey, NamespacedItem)>> {
    if path.ends_with(".json") | path.ends_with(".mcfunction") {
        let file = fs::read_to_string(&path)?;
        if path.ends_with(".json") {
            if let Ok(json) = serde_json::from_str(&file) {
                if let Ok(namespace) = NamespacedKey::from_path(path.trim_start_matches(datapacks_path)) {
                    return Ok(Some((namespace, NamespacedItem::Advancement(Advancement{ path: vec!(path), children: vec!(), used: false, data: vec!(file), json_data: vec!(json) }))))
                } else {
                    /* Suppress warnings about intentionally failing objects */
                    if !path.contains("loot_tables") && !path.contains("recipes") && !path.contains("/tags/") {
                        warn!("Failed to create namespaced key for: {}", path);
                    }
                }
            } else {
                warn!("Failed to parse file as json: {}", path);
            }
        } else if path.ends_with(".mcfunction") {
            if let Ok(namespace) = NamespacedKey::from_path(path.trim_start_matches(datapacks_path)) {
                return Ok(Some((namespace, NamespacedItem::Function(Function{ path: vec!(path), children: vec!(), used: false, data: vec!(file) }))))
            } else {
                warn!("Failed to create namespaced key for: {}", path);
            }
        }
    }

    Ok(None)
}

fn load_quests(items: &mut HashMap<NamespacedKey, NamespacedItem>, dir: &str) -> anyhow::Result<()> {
    for entry in WalkDir::new(dir).follow_links(true) {
        if let Ok(entry) = entry {
            let path = entry.path().to_str().unwrap();
            if entry.path().is_file() && path.ends_with(".json") {
                let file = fs::read_to_string(&path)?;
                if let Ok(json @ serde_json::value::Value::Object(_)) = serde_json::from_str(&file) {
                    if let Ok(namespace) = NamespacedKey::from_path(path.trim_start_matches(dir)) {
                        items.insert(namespace, NamespacedItem::Quest(Quest{ path: vec!(path.to_string()), children: vec!(), used: false, data: vec!(file), json_data: json }));
                    } else {
                        warn!("Failed to create namespaced key for: {}", path);
                    }
                } else {
                    bail!("Failed to parse file as json object: {}", path);
                }
            }
        }
    }
    Ok(())
}

fn load_datapack(items: &mut HashMap<NamespacedKey, NamespacedItem>, dir: &str) -> anyhow::Result<()> {
    for entry in WalkDir::new(dir).follow_links(true) {
        if let Ok(entry) = entry {
            if entry.path().is_file() {
                if let Some((namespace, item)) = load_datapack_file(entry.path().to_str().unwrap().to_string(), dir)? {
                    /*
                     * If an existing item already exists with this path, add it as a variant to
                     * the existing node
                     */
                    if let Some(existing) = items.get_mut(&namespace) {
                        existing.add_variant(item);
                    } else {
                        items.insert(namespace, item);
                    }
                }
            }
        }
    }
    Ok(())
}

fn link_quest_file_recursive(path: &str, children: &mut Vec<NamespacedKey>, value: &serde_json::value::Value) {
    match value {
        serde_json::value::Value::Array(array) => {
            for item in array.iter() {
                link_quest_file_recursive(path, children, item);
            }
        }
        serde_json::value::Value::Object(obj) => {
            for (key, value) in obj.iter() {
                if key == "command" {
                    if let serde_json::value::Value::String(command) = value {
                        if let Some(key) = get_command_target_namespacedkey(command) {
                            children.push(key);
                        }
                    }
                } else if key == "function" {
                    if let serde_json::value::Value::String(function) = value {
                        if let Ok(key) = NamespacedKey::from_str(function, NamespaceType::Function) {
                            children.push(key);
                        } else {
                            warn!("Quest file contains unparseable function '{}': {}", function, path);
                        }
                    }
                } else {
                    link_quest_file_recursive(path, children, value);
                }
            }
        }
        _ => ()
    }
}

fn load_commands_file(items: &mut HashMap<NamespacedKey, NamespacedItem>, path: &str) -> anyhow::Result<()> {
    let file = fs::read_to_string(&path)?;
    if let Ok(json) = serde_json::from_str(&file) {
        if let serde_json::value::Value::Array(array) = json {
            for item in array.iter() {
                if let serde_json::value::Value::Object(obj) = item {
                    if let Some(serde_json::value::Value::String(command)) = obj.get("command") {
                        if let Some(serde_json::value::Value::Array(pos)) = obj.get("pos") {
                            if let Some(serde_json::value::Value::Number(x)) = pos.get(0) {
                                if let Some(serde_json::value::Value::Number(y)) = pos.get(1) {
                                    if let Some(serde_json::value::Value::Number(z)) = pos.get(2) {
                                        let namespace = NamespacedKey::from_command(path, &format!("{} {} {}", x, y, z));
                                        let val = NamespacedItem::Command(Command{ path: vec!(namespace.to_string()), children: vec!(), data: vec!(command.to_string()) });
                                        if let Some(existing) = items.get_mut(&namespace) {
                                            existing.add_variant(val);
                                        } else {
                                            items.insert(namespace, val);
                                        }
                                    } else {
                                        warn!("Invalid commands json pos: {}", path);
                                    }
                                } else {
                                    warn!("Invalid commands json pos: {}", path);
                                }
                            } else {
                                warn!("Invalid commands json pos: {}", path);
                            }
                        } else {
                            warn!("Commands json entry missing 'pos': {}", path);
                        }
                    } else {
                        warn!("Commands json entry missing 'command': {}", path);
                    }
                } else {
                    warn!("Failed to parse commands json entry as object: {}", path);
                }
            }
        } else {
            warn!("Failed to parse file as json: {}", path);
        }
    } else {
        warn!("Failed to parse file as json: {}", path);
    }
    Ok(())
}

fn get_command_target_namespacedkey(command: &str) -> Option<NamespacedKey> {
    lazy_static! {
        static ref RE_FUNC: Regex = Regex::new(r"function [a-z][^ :]*:[a-z][^ :]*").unwrap();
        static ref RE_ADV: Regex = Regex::new(r"advancement (grant|revoke) .* (everything|from|only|through|until) [a-z][^ :]*:[a-z][^ :]*").unwrap();
        static ref RE_ADV_ONLY: Regex = Regex::new(r" only [a-z][^ :]*:[a-z][^ :]*").unwrap();
    }

    /* Link functions to the other functions they call */
    /* Schedule function and function both have the same syntax, so one match will do */
    if let Some(func_match) = RE_FUNC.find(command) {
        let function = func_match.as_str().trim_start_matches("function ");
        if let Ok(key) = NamespacedKey::from_str(function, NamespaceType::Function) {
            return Some(key);
        } else {
            warn!("Command contains unparseable function {}", function);
        }
    }

    /* Link functions to advancements */
    if let Some(adv_match) = RE_ADV.find(command) {
        if let Some(adv_only_match) = RE_ADV_ONLY.find(adv_match.as_str()) {
            let advancement = adv_only_match.as_str().trim_start_matches(" only ");
            if let Ok(key) = NamespacedKey::from_str(advancement, NamespaceType::Advancement) {
                return Some(key);
            } else {
                warn!("Command contains unparseable advancement {}", advancement);
            }
        } else {
            info!("No support for advancement command {}", adv_match.as_str());
        }
    }

    None
}

fn create_links(items: &mut HashMap<NamespacedKey, NamespacedItem>) {

    /* Create links between the various files */
    for (_, val) in items.iter_mut() {
        match val {
            NamespacedItem::Advancement(advancement) => {
                /* Create reference links for advancements */

                /* Link to parent advancement as dependency */
                /* TODO: Is this needed? */
                if let Some(serde_json::Value::String(parent)) = advancement.json_data.get(0).unwrap().get("parent") {
                    if let Ok(key) = NamespacedKey::from_str(parent, NamespaceType::Advancement) {
                        advancement.children.push(key);
                    } else {
                        warn!("Advancement contains unparseable parent {}", parent);
                    }
                }

                /* Link to function */
                for data in advancement.json_data.iter() {
                    if let Some(run_func) = get_function(&data) {
                        advancement.children.push(run_func);
                    }
                }

                /* Mark as used if any non-impossible triggers exist */
                advancement.used = false;
                for data in advancement.json_data.iter() {
                    if let Some(serde_json::Value::Object(criteria)) = data.get("criteria") {
                        for (_c_key, c_value) in criteria.iter() {
                            if let Some(trigger_compound) = c_value.get("trigger") {
                                if let serde_json::Value::String(trigger) = trigger_compound {
                                    if trigger != "minecraft:impossible" {
                                        /* Has a string trigger that is not impossible -> used */
                                        advancement.used = true;
                                    }
                                } else {
                                    /* Has a non-string trigger -> used */
                                    advancement.used = true;
                                }
                            }
                        }
                    }
                }
            }
            NamespacedItem::Function(function) => {
                /* Create reference links for functions */
                for data in function.data.iter() {
                    for line in data.lines() {
                        if !line.trim().starts_with("#") {
                            if let Some(key) = get_command_target_namespacedkey(line) {
                                function.children.push(key);
                            }
                        }
                    }
                }
            }
            NamespacedItem::Quest(quest) => {
                /* TODO: Quest is always used */
                quest.used = true;
                link_quest_file_recursive(&quest.path.get(0).unwrap(), &mut quest.children, &quest.json_data);
            }
            NamespacedItem::Command(command) => {
                for data in command.data.iter() {
                    if let Some(key) = get_command_target_namespacedkey(data) {
                        command.children.push(key);
                    }
                }
            }
        }
    }
}

fn find_unused_scoreboards(scoreboards: &ScoreboardCollection, items: &HashMap<NamespacedKey, NamespacedItem>) -> anyhow::Result<()> {
    let mut used_objectives: HashMap<&String, Vec<&NamespacedKey>> = HashMap::new();

    for objective in scoreboards.objectives() {
        for (key, val) in items.iter() {
            'outer: for data in val.get_data() {
                for line in data.lines() {
                    if !line.trim().starts_with("#") && line.contains(objective) {
                        used_objectives.entry(objective).or_insert(vec!()).push(key);
                        break 'outer;
                    }
                }
            }
        }
    }

    let scoreboard_usage = scoreboards.get_objective_usage_sorted();
    let mut unused_objectives: Vec<&(String, f64)> = scoreboard_usage.iter().filter(|(objective, _)| !used_objectives.contains_key(objective)).collect();
    unused_objectives.sort_by(|(a1, a2), (b1, b2)| if a2 == b2 { a1.partial_cmp(b1).unwrap() } else { a2.partial_cmp(b2).unwrap() });

    println!("\n\n\nUnused Objectives (not used by any datapacks/quests/commands) : % of entities with nonzero score");
    for (objective, percentage) in unused_objectives.iter() {
        println!("{0: <20}{1}", objective, percentage);
    }
    println!("\nTotal unused objectives (not used by any datapacks/quests/commands) : {}", unused_objectives.len());

    println!("\n\n\nLow usage objectives (low usage but referenced somewhere) : % of entities with nonzero score");
    let mut low_usage = 0;
    for (objective, percentage) in scoreboard_usage {
        if percentage <= 0.01f64 {
            if let Some(used_locs) = used_objectives.get(&objective) {
                low_usage += 1;
                println!("{0: <20}{1}", objective, percentage);
                if used_locs.len() <= 5 {
                    for loc in used_locs {
                        println!("  {}", loc);
                    }
                } else {
                    println!("  <{} locations>", used_locs.len());
                }
            }
        }
    }
    println!("\nTotal low usage objectives (low usage but referenced somewhere) : {}", low_usage);

    Ok(())
}

const DATAPACKS_ARG: &str = "--datapacks";
const COMMANDS_ARG: &str = "--commands";
const QUESTS_ARG: &str = "--quests";
const SCOREBOARDS_ARG: &str = "--scoreboards";
const REDIS_SCOREBOARDS_ARG: &str = "--redis-scoreboards";

fn usage() {
    error!("Usage: find_unused_components -- --type1 file1 file2 ... --type2 file1 ... ...");
    error!("   Where --type is one of {} {} {} {} {}", DATAPACKS_ARG, COMMANDS_ARG, QUESTS_ARG, SCOREBOARDS_ARG, REDIS_SCOREBOARDS_ARG);
}

fn main() -> anyhow::Result<()> {
    let mut multiple = vec![];
    multiple.push(TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed, ColorChoice::Auto) as Box<dyn SharedLogger>);
    CombinedLogger::init(multiple).unwrap();

    /* A map of all of the advancements and functions that have been loaded */
    let mut items: HashMap<NamespacedKey, NamespacedItem> = HashMap::new();

    /* Load all the arguments as datapacks */
    let mut args: Vec<String> = env::args().collect();

    if args.len() <= 1 {
        usage();
        return Ok(());
    }

    let mut scoreboards = ScoreboardCollection::new();

    /* Basically an argument state machine */
    let mut separator = "";

    args.remove(0);
    while args.len() > 0 {
        match &args.remove(0)[..] {
            DATAPACKS_ARG => {
                info!("Loading datapacks...");
                separator = DATAPACKS_ARG;
            },
            COMMANDS_ARG => {
                info!("Loading commands...");
                separator = COMMANDS_ARG;
            },
            QUESTS_ARG => {
                info!("Loading quests...");
                separator = QUESTS_ARG;
            },
            SCOREBOARDS_ARG => {
                info!("Loading scoreboards...");
                separator = SCOREBOARDS_ARG;
            },
            REDIS_SCOREBOARDS_ARG => {
                info!("Loading redis scoreboards...");
                separator = REDIS_SCOREBOARDS_ARG;
            },
            arg => {
                if separator == DATAPACKS_ARG {
                    info!("Loading datapack {}", arg);
                    load_datapack(&mut items, arg)?;
                } else if separator == COMMANDS_ARG {
                    info!("Loading commands {}", arg);
                    load_commands_file(&mut items, arg)?;
                } else if separator == QUESTS_ARG {
                    info!("Loading quests {}", arg);
                    load_quests(&mut items, arg)?;
                } else if separator == SCOREBOARDS_ARG {
                    info!("Loading scoreboard {}", arg);
                    scoreboards.add_scoreboard(arg)?;
                } else if separator == REDIS_SCOREBOARDS_ARG {
                    info!("Loading redis scoreboard for domain {}", arg);
                    let client = redis::Client::open("redis://127.0.0.1/")?;
                    let mut con : redis::Connection = client.get_connection()?;
                    let scoreboard = Scoreboard::load_redis(&arg, &mut con)?;
                    scoreboards.add_existing_scoreboard(scoreboard)?;
                } else {
                    error!("Got unexpected argument: {}", arg);
                    usage();
                    return Ok(());
                }
            }
        }
    }

    create_links(&mut items);

    /*
     * Load all the things that are used into the pending list, which contains items that are
     * children of used items but have not yet been processed / marked as used
     *
     * Also include the paths where those items are used from
     */
    let mut pending: Vec<(NamespacedKey, Vec<String>)> = Vec::new();
    for (_, value) in items.iter() {
        if value.is_used() {
            for child_key in value.get_children().iter() {
                pending.push((child_key.clone(), value.get_paths().clone()));
            }
        }
    }

    /*
     * Store a map of all the keys that are referenced by used items but don't actually
     * exist. This maps to a list of all the places these things are used from
     */
    let mut missing: HashMap<NamespacedKey, Vec<String>> = HashMap::new();

    /* Iterate through the pending list and mark things as used */
    while pending.len() > 0 {
        let (key, paths) = pending.pop().unwrap();
        if let Some(map_value) = items.get_mut(&key) {
            /*
             * Only do work on nodes not marked as used. If a node is already
             * marked as used, it has either already had its children marked
             * or it is in the pending list
             */
            if !map_value.is_used() {
                map_value.set_used(true);
                /* Copy the children into the pending list */
                for child_key in map_value.get_children().iter() {
                    pending.push((child_key.clone(), map_value.get_paths().clone()));
                }
            }
        } else {
            missing.entry(key).or_insert(vec!()).extend(paths);
        }
    }

    println!("\n\n\nMissing items that are referenced by used files:");
    for (key, paths) in missing.iter_mut() {
        paths.sort_by(|a, b| b.partial_cmp(a).unwrap());
        println!("{}", key);
        for path in paths {
            println!("  {}", path);
        }
    }

    /* Collect all unused items to a vector */
    let unused_items: Vec<&NamespacedItem> = items.iter().map(| (_, val) | val).filter(| val | !val.is_used()).collect();
    let mut unused_paths: Vec<&String> = Vec::new();
    for item in unused_items {
        unused_paths.extend(item.get_paths().iter());
    }
    unused_paths.sort_by(|a, b| b.partial_cmp(a).unwrap());

    println!("\n\n\nUnused Files:");
    for path in unused_paths.iter() {
        println!("{}", path);
    }
    println!("\nFound {} unused files", unused_paths.len());

    find_unused_scoreboards(&scoreboards, &items)?;

    Ok(())
}

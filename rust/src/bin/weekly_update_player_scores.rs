#[macro_use] extern crate simple_error;

use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use chrono::prelude::*;
use rayon::prelude::*;
use std::env;
use std::path::Path;
use std::collections::HashMap;
use std::collections::HashSet;
use simplelog::*;
use uuid::Uuid;
use std::fs;
use serde_json::json;

use monumenta::player::Player;

fn usage() {
    println!("Usage: weekly_update_players path/to/directory");
}

const INSTANCE_WEEK_OFFSET: i32 = 10000;

fn update_instance_scores(scores: &mut HashMap<String, i32>, objective: &str, increment: i32, max: i32, additional_objectives_to_reset: &[&str]) {
    if let Some(access) = scores.get(objective) {
        if *access >= 1 {
            let mut access: i32 = *access;
            access += increment;
            if access >= max {
                access = 0;
                /* Reset all other specified objectives on overflow */
                for additional_objective in additional_objectives_to_reset {
                    scores.insert(additional_objective.to_string(), 0);
                }
            }
            /* Update this specific objective always, since it either changed or was reset */
            scores.insert(objective.to_string(), access);
        }
    }
}

#[allow(non_snake_case)]
fn fix_total_level(scores: &mut HashMap<String, i32>) {
    let White = *scores.get("White").unwrap_or(&0);
    let Orange = *scores.get("Orange").unwrap_or(&0);
    let Magenta = *scores.get("Magenta").unwrap_or(&0);
    let LightBlue = *scores.get("LightBlue").unwrap_or(&0);
    let Yellow = *scores.get("Yellow").unwrap_or(&0);
    let Lime = *scores.get("Lime").unwrap_or(&0);
    let Cyan = *scores.get("Cyan").unwrap_or(&0);
    let LightGray = *scores.get("LightGray").unwrap_or(&0);
    let CorrectedLevel = 2 + if White > 0 {1} else {0} + if Orange > 0 {1} else {0} + if Magenta > 0 {1} else {0} + if LightBlue > 0 {1} else {0} + if Yellow > 0 {1} else {0} + if Lime > 0 {1} else {0} + if Cyan > 0 {1} else {0} + if LightGray > 0 {1} else {0};

    scores.insert("TotalLevel".to_string(), CorrectedLevel);
}

fn update_player_scores(player: &mut Player) {
    if let Some(scores) = &mut player.scores {
        /*
         * These scores increment by 10000 or if >= max are reset to 0, along with resetting
         * the additional objectives listed at the end
         */
        update_instance_scores(scores, "D0Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D0Finished"]);
        update_instance_scores(scores, "D1Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D1Finished", "D1Delve1", "D1Delve2"]);
        update_instance_scores(scores, "D2Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D2Finished", "D2Delve1", "D2Delve2"]);
        update_instance_scores(scores, "D3Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D3Finished", "D3Delve1", "D3Delve2"]);
        update_instance_scores(scores, "D4Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D4Finished", "D4Delve1", "D4Delve2"]);
        update_instance_scores(scores, "D5Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D5Finished", "D5Delve1", "D5Delve2"]);
        update_instance_scores(scores, "D6Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D6Finished", "D6Delve1", "D6Delve2"]);
        update_instance_scores(scores, "D7Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D7Finished", "D7Delve1", "D7Delve2"]);
        update_instance_scores(scores, "D8Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D8Finished", "D8Delve1", "D8Delve2"]);
        update_instance_scores(scores, "D9Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D9Finished", "D9Delve1", "D9Delve2"]);
        update_instance_scores(scores, "D10Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D10Finished", "D10Delve1", "D10Delve2"]);
        update_instance_scores(scores, "D11Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["D11Finished", "D11Delve1", "D11Delve2"]);
        update_instance_scores(scores, "DTLAccess", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["DTLFinished", "DTLDelve1", "DTLDelve2"]);
        update_instance_scores(scores, "DCAccess", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["DCFinished", "DMRDelve1", "DMRDelve2"]);
        update_instance_scores(scores, "DB1Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["DB1Finished", "DWDelve1", "DWDelve2"]);
        update_instance_scores(scores, "DRL2Access", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["DRL2Finished", "DSCDelve1", "DSCDelve2"]);
        update_instance_scores(scores, "DFFAccess", INSTANCE_WEEK_OFFSET, 3 * INSTANCE_WEEK_OFFSET, &["DFFFinished", "DFFDelve1", "DFFDelve2"]);

        /* DelveDungeon score also increments as if it was a dungeon score */
        update_instance_scores(scores, "DelveDungeon", 1000, 3 * 1000, &[]);

        /* These scores are always reset to 0 */
        scores.insert("DRAccess".to_string(), 0);
        scores.insert("DRDAccess".to_string(), 0);
        scores.insert("DBMAccess".to_string(), 0);
        scores.insert("DSRAccess".to_string(), 0);
        scores.insert("DFSAccess".to_string(), 0);
        scores.insert("DDAccess".to_string(), 0);

        scores.insert("WeeklyMission1".to_string(), 0);
        scores.insert("WeeklyMission2".to_string(), 0);
        scores.insert("WeeklyMission3".to_string(), 0);

        /* Uncomment this with each new season pass */
        scores.insert("SeasonalEventMP".to_string(), 0);

        fix_total_level(scores);
    }
}

fn update_world(world: &str) -> &str {
    if world == "Project_Epic-region_1" {
        return "Project_Epic-valley"
    } else if world == "Project_Epic-region_2" {
        return "Project_Epic-isles"
    }
    return world
}

fn main() -> BoxResult<()> {
    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        usage();
        return Ok(());
    }

    args.remove(0);

    // Get the path to the project_epic directory
    let basedir = args.remove(0);
    let basedir = Path::new(&basedir);
    if !basedir.is_dir() {
        bail!("Supplied input directory does not exist");
    }
    let basedirpath = basedir.to_str().unwrap();

    let start = Utc::now().time(); // START

    // TODO: Argument for num threads
    rayon::ThreadPoolBuilder::new().num_threads(0).build_global()?;

    let end = Utc::now().time(); // STOP
    println!("Created thread pool in {} milliseconds", (end - start).num_milliseconds());

    let start = Utc::now().time(); // START

    /* Enumerate all the UUIDs by looking at the core playerdata folder */
    let uuids : HashSet<Uuid> = fs::read_dir(Path::new(&basedir).join("playerdata"))?
        .into_iter()
        .filter_map(|entry| entry.ok())
        .filter(|path| path.path().extension().unwrap() == "dat")
        .map(|path| Uuid::parse_str(path.path().file_stem().unwrap().to_str().unwrap()).unwrap())
        .collect();

    let end = Utc::now().time(); // STOP
    println!("Loaded {} uuids in {} milliseconds", uuids.len(), (end - start).num_milliseconds());

    let start = Utc::now().time(); // START

    uuids.par_iter().for_each(|uuid| {
        let mut player = Player::new(*uuid);
        player.load_dir(basedirpath).unwrap();

        player.update_history("Weekly update");
        update_player_scores(&mut player);

        /* Remove all the per-shard data */
        if let Some(sharddata) = &mut player.sharddata {
            sharddata.clear();
        }

        /* Update plugin data */
        if let Some(mut plugindata) = player.plugindata {
            for (key, value) in plugindata.iter_mut() {
                /* Update graves with the R1/R2 rename */
                if key == "MonumentaGravesV2" {
                    if let serde_json::value::Value::Object(obj) = value {
                        for (key, value) in obj.iter_mut() {
                            if key == "graves" {
                                for entry in value.as_array_mut().unwrap() {
                                    let entry = entry.as_object_mut().unwrap();
                                    entry.insert("world".to_owned(), json!(update_world(entry.get("world").unwrap().as_str().unwrap())));
                                }
                            } else if key == "thrown_items" {
                                for entry in value.as_array_mut().unwrap() {
                                    let entry = entry.as_object_mut().unwrap();
                                    entry.insert("world".to_owned(), json!(update_world(entry.get("world").unwrap().as_str().unwrap())));
                                }
                                /*
                                 * TODO: Maybe someday this will be worth fixing to automatically
                                 * remove compass graves...
                                 */
                                /*
                                let value : Vec<serde_json::value::Value> = value.as_array_mut().unwrap().iter_mut().filter_map(|entry| {
                                    if let Some(obj) = entry.as_object_mut() {
                                        // Upgrade world if needed
                                        if let Some(world) = obj.get("world") {
                                            if let Some(worldstr) = world.as_str() {
                                                obj.insert("world".to_owned(), json!(update_world(worldstr)));
                                            }
                                        } else {
                                            println!("WARNING: Found thrown_items entry missing world");
                                            return None;
                                        }

                                        if let Some(nbt) = obj.get("nbt") {
                                            if let Some(nbtstr) = nbt.as_str() {
                                                if nbtstr.contains("Quest Compass") {
                                                    println!("Compass!");
                                                    return None;
                                                }
                                            }
                                            return Some(json!(obj));
                                        } else {
                                            println!("WARNING: Found thrown_items entry missing nbt");
                                            return None;
                                        }
                                    } else {
                                        println!("WARNING: Found thrown_items entry that is not an object");
                                        return None;
                                    }
                                }).collect();
                                */
                            } else {
                                println!("GOT UNKNOWN MonumentaGravesV2 KEY: {:?}", key);
                            }
                        }
                    }
                }
            }
            player.plugindata = Some(plugindata);
        }


        player.save_dir(basedirpath).unwrap();
        ()
    });

    let end = Utc::now().time(); // STOP
    println!("Updated {} players in {} milliseconds", uuids.len(), (end - start).num_milliseconds());

    Ok(())
}

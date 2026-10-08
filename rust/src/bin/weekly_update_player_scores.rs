use std::{
    collections::{HashMap, HashSet},
    env, fs,
    path::Path,
};

use anyhow::{self, bail};
use chrono::prelude::*;
use rayon::prelude::*;
use simplelog::*;
use uuid::Uuid;

use monumenta::player::Player;

fn usage() {
    println!("Usage: weekly_update_player_scores path/to/directory");
}

fn update_instance_scores(
    scores: &mut HashMap<String, i32>,
    days_since_epoch: i32,
    start_objective: &str,
    max_days: i32,
    additional_objectives_to_reset: &[&str],
) {
    if let Some(start) = scores.get(start_objective) {
        if *start != i32::MAX && days_since_epoch < *start {
            eprintln!(
                "Got dungeon {} start {} which is in the future! Current days since epoch: {}",
                start_objective, *start, days_since_epoch
            );
        } else if *start == i32::MAX || days_since_epoch - *start >= max_days {
            /* Reset all specified objectives on expiration */
            scores.insert(start_objective.to_string(), 0);
            for additional_objective in additional_objectives_to_reset {
                scores.insert(additional_objective.to_string(), 0);
            }
        }
    }
}

#[allow(non_snake_case)]
fn fix_total_level(scores: &mut HashMap<String, i32>) {
    let Quest03 = *scores.get("Quest03").unwrap_or(&0);
    let White = *scores.get("White").unwrap_or(&0);
    let Magenta = *scores.get("Magenta").unwrap_or(&0);
    let Yellow = *scores.get("Yellow").unwrap_or(&0);
    let Lime = *scores.get("Lime").unwrap_or(&0);
    let LightGray = *scores.get("LightGray").unwrap_or(&0);
    let Cyan = *scores.get("Cyan").unwrap_or(&0);
    let CorrectedLevel = 3
        + if Quest03 == 21 { 1 } else { 0 }
        + if White > 0 { 1 } else { 0 }
        + if Magenta > 0 { 1 } else { 0 }
        + if Yellow > 0 { 1 } else { 0 }
        + if Lime > 0 { 1 } else { 0 }
        + if Cyan > 0 { 1 } else { 0 }
        + if LightGray > 0 { 1 } else { 0 };

    scores.insert("TotalLevel".to_string(), CorrectedLevel);
}

fn update_player_scores(player: &mut Player, days_since_epoch: i32) {
    let scores_to_remove = HashSet::from([
        // "DFSFinished",
        // "DVFinished",
        // "DSRFinished", // all five of these are used for mechs and should really be condensed into one "StrikeChests"
        // "DPSFinished",
        // "DMASFinished",
        "DFSAccess",
        "DFSStartDate", // remove from base->functions/lobbies/abandon/sanctum
        "DVAccess",
        "AzacorAccess",
        "DBMAccess",
        "DSRAccess",
        "DPSAccess",
        "DMASAccess",
        "GodsporeAccess",
        // "CovenAmpAccess", // hope springs eternal...
        "CovenAmpAccessRing", // this one can go though
        "Marketbanned", // wrong scoreboard, correct is MarketBanned
        "DS1Access", // legacy sanctum i think? only use is `datapacks/valley/data/monumenta/functions/lobbies/instances_remaining` and `[...]/instances_remaining_continued_1`
    ]);

    let score_types_access = HashMap::from([
        ("Access", "Access"),
        ("Finished", "Lootroom"), // "lootroom" misleading for willows, reverie, forum, etc... oh well
    ]);

    let score_types_startdate = HashMap::from([
        ("StartDate", "StartDate"),
        ("LastVisit", "LastVisit"),
        ("Type", "Type"), // want to change this but idk what to change to
    ]);
    
    let dungeon_codes_access = HashMap::from([
        ("Tutorial", "T"),
        ("Labs", "0"),
        ("White", "1"),
        ("Orange", "2"),
        ("Magenta", "3"),
        ("LightBlue", "4"),
        ("Yellow", "5"),
        ("Willows", "B1"),
        ("Reverie", "C"),
        ("Corridors", "R"),
        
        ("Lime", "6"),
        ("Pink", "7"),
        ("Gray", "8"),
        ("LightGray", "9"),
        ("Cyan", "10"),
        ("Purple", "11"),
        ("Teal", "TL"),
        ("Shifting", "RL2"),
        ("Forum", "FF"),
        ("Rush", "RD"),
        ("Depths", "D"), // it's D and not DD, so it ends up as DDAccess
        
        ("Blue", "12"),
        ("Brown", "13"),
        ("Indigo", "I"),
        ("SKT", "SKT"), // lol
        ("Gallery", "G"),
        ("Zenith", "CZ"),
        ("Hexfall", "HF"),
        ("Fortune", "WF"),
    ]);
    
    let dungeon_codes_startdate = HashMap::from([
        ("Willows", "BW"),
        ("Reverie", "MR"),
        ("Shifting", "CS"),
    ]);

    let other_score_replacements = HashMap::from([
        ("CurrentPlot", "AccessPlayerplots"),
        ("Guild", "AccessGuildplots"),
        ("CovenAmpAccess", "AccessAmpedCoven"),
        ("R1Access", "AccessValleyInstanced"),
        ("R2Access", "AccessIslesInstanced"),
        ("DR3Access", "AccessRingInstanced"),
        ("R1Type", "TypeValleyInstanced"),
        ("R2Type", "TypeIslesInstanced"),
        ("R3Type", "TypeRingInstanced"),
    ]);
    
    if let Some(scores) = &mut player.scores {
        for objective in scores_to_remove {
            let removed = scores.remove(objective);
            if let Some(_) = removed {
                println!("removed {}", objective);
            }
        }

        for (dungeon, access_code) in dungeon_codes_access {
            for (score_type_old, score_type_new) in &score_types_access {
                let old_objective = format!("D{}{}", access_code, score_type_old);
                let new_objective = format!("{}{}", score_type_new, dungeon);
                let score = scores.remove(&old_objective);
                if let Some(score) = score {
                    println!("{} -> {}", old_objective, new_objective);
                    scores.insert(new_objective, score);
                }
            }

            let &start_date_code = dungeon_codes_startdate.get(dungeon).unwrap_or(&access_code);
            for (score_type_old, score_type_new) in &score_types_startdate {
                let old_objective = format!("D{}{}", start_date_code, score_type_old);
                let new_objective = format!("{}{}", score_type_new, dungeon);
                let score = scores.remove(&old_objective);
                if let Some(score) = score {
                    println!("{} -> {}", old_objective, new_objective);
                    scores.insert(new_objective, score);
                }
            }
        }

        for (old_objective, new_objective) in other_score_replacements {
            let score = scores.remove(old_objective);
            if let Some(score) = score {
                println!("{} -> {}", old_objective, new_objective);
                scores.insert(new_objective.parse().unwrap(), score);
            }
        }

        /* Reset dungeon scores if their StartDate is more than old enough for them to expire */
        update_instance_scores(scores, days_since_epoch, "StartDateLabs", 28, &["AccessLabs", "LootroomLabs"]);
        update_instance_scores(scores, days_since_epoch, "StartDateWhite", 28, &["AccessWhite", "LootroomWhite"]);
        update_instance_scores(scores, days_since_epoch, "StartDateOrange", 28, &["AccessOrange", "LootroomOrange"]);
        update_instance_scores(scores, days_since_epoch, "StartDateMagenta", 28, &["AccessMagenta", "LootroomMagenta"]);
        update_instance_scores(scores, days_since_epoch, "StartDateLightBlue", 28, &["AccessLightBlue", "LootroomLightBlue"]);
        update_instance_scores(scores, days_since_epoch, "StartDateYellow", 28, &["AccessYellow", "LootroomYellow"]);
        update_instance_scores(scores, days_since_epoch, "StartDateWillows", 28, &["AccessWillows", "LootroomWillows"]);
        update_instance_scores(scores, days_since_epoch, "StartDateReverie", 28, &["AccessReverie", "LootroomReverie"]);

        update_instance_scores(scores, days_since_epoch, "StartDateLime", 28, &["AccessLime", "LootroomLime"]);
        update_instance_scores(scores, days_since_epoch, "StartDatePink", 28, &["AccessPink", "LootroomPink"]);
        update_instance_scores(scores, days_since_epoch, "StartDateGray", 28, &["AccessGray", "LootroomGray"]);
        update_instance_scores(scores, days_since_epoch, "StartDateLightGray", 28, &["AccessLightGray", "LootroomLightGray"]);
        update_instance_scores(scores, days_since_epoch, "StartDateCyan", 28, &["AccessCyan", "LootroomCyan"]);
        update_instance_scores(scores, days_since_epoch, "StartDatePurple", 28, &["AccessPurple", "LootroomPurple"]);
        update_instance_scores(scores, days_since_epoch, "StartDateTeal", 28, &["AccessTeal", "LootroomTeal"]);
        update_instance_scores(scores, days_since_epoch, "StartDateShifting", 28, &["AccessShifting", "LootroomShifting"]);
        update_instance_scores(scores, days_since_epoch, "StartDateForum", 28, &["AccessForum", "LootroomForum"]);

        update_instance_scores(scores, days_since_epoch, "StartDateSKT", 14, &["AccessSKT", "LootroomSKT"]);
        update_instance_scores(scores, days_since_epoch, "StartDateBlue", 28, &["AccessBlue", "LootroomBlue"]);
        update_instance_scores(scores, days_since_epoch, "StartDateBrown", 28, &["AccessBrown", "LootroomBrown"]);
        update_instance_scores(scores, days_since_epoch, "StartDateHexfall", 28, &["AccessHexfall", "LootroomHexfall"]);
        update_instance_scores(scores, days_since_epoch, "StartDateIndigo", 28, &["AccessIndigo", "LootroomIndigo"]);
        update_instance_scores(scores, days_since_epoch, "StartDateFortune", 28, &["AccessFortune", "LootroomFortune"]);

        /* DelveDungeon score also resets as if it was a dungeon score */
        update_instance_scores(scores, days_since_epoch, "DelveStartDate", 28, &["DelveDungeon"]);

        /* These scores are always reset to 0 */
        scores.remove("AccessCorridors");
        scores.remove("AccessRush");
        // Sanctum & Verdant
        scores.remove("AccessValleyInstanced");
        // Remorse & Mist
        scores.remove("AccessIslesInstanced");
        scores.remove("AccessDepths");
        // Ring scores
        scores.remove("AccessRingInstanced");
        scores.remove("AccessGallery");
        scores.remove("AccessZenith");

        fix_total_level(scores);
    }
}

fn main() -> anyhow::Result<()> {
    CombinedLogger::init(vec![TermLogger::new(
        LevelFilter::Debug,
        Config::default(),
        TerminalMode::Mixed,
        ColorChoice::Auto,
    ) as Box<dyn SharedLogger>])
    .unwrap();

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
    let uuids: HashSet<Uuid> = fs::read_dir(Path::new(&basedir).join("playerdata"))?
        .filter_map(|entry| entry.ok())
        .filter(|path| path.path().extension().unwrap() == "dat")
        .map(|path| Uuid::parse_str(path.path().file_stem().unwrap().to_str().unwrap()).unwrap())
        .collect();

    let end = Utc::now().time(); // STOP
    println!("Loaded {} uuids in {} milliseconds", uuids.len(), (end - start).num_milliseconds());

    let start = Utc::now().time(); // START
    let days_since_epoch: i32 = (Utc::now() - Utc.timestamp_nanos(0)).num_days() as i32;

    uuids.par_iter().for_each(|uuid| {
        let mut player = Player::new(*uuid);
        player.load_dir(basedirpath).unwrap();

        player.update_history("Weekly update");
        update_player_scores(&mut player, days_since_epoch);

        /* Remove all the per-shard data */
        if let Some(sharddata) = &mut player.sharddata {
            sharddata.clear();
        }

        /* Update plugin data */
        /* This is no longer used but likely to be useful in the future */
        /*
        if let Some(mut plugindata) = player.plugindata {
            for (key, value) in plugindata.iter_mut() {
                /* Update graves with the R1/R2 rename */
                if key == "MonumentaGravesV2" {
                    if let serde_json::value::Value::Object(obj) = value {
                        for (key, value) in obj.iter_mut() {
                            if key == "graves" {
                                // Example only, this code no longer works
                                // for entry in value.as_array_mut().unwrap() {
                                //     let entry = entry.as_object_mut().unwrap();
                                //     entry.insert("world".to_owned(), json!(update_world(entry.get("world").unwrap().as_str().unwrap())));
                                // }
                            } else if key == "thrown_items" {
                                // Example

                            } else {
                                println!("GOT UNKNOWN MonumentaGravesV2 KEY: {:?}", key);
                            }
                        }
                    }
                }
            }
            player.plugindata = Some(plugindata);
        }
        */

        /* Update player content data */
        if let Some(contentdata) = &mut player.contentdata {
            /* TODO

            Need to combine this with score changes, moving players to the appropriate overworld if
            their instance expired. RedisSync is getting support for tracking fallback content for this,
            then we only need to hard-code the fallback content here. That or write something to read the
            redis-sync config maybe? Certain other content should also move the player to the overworld, such
            as quest worlds. That said, players in a dungeon that hasn't expired, or a plot, should stay there.

            In the meantime, an empty string defaults the player back to the default world of the shard.
            */
            contentdata.set_id("");
        }

        player.save_dir(basedirpath).unwrap();
    });

    let end = Utc::now().time(); // STOP
    println!("Updated {} players in {} milliseconds", uuids.len(), (end - start).num_milliseconds());

    Ok(())
}

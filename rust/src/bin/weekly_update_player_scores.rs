#[macro_use] extern crate simple_error;

use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::env;
use std::path::Path;
use std::collections::HashMap;
use simplelog::*;
use uuid::Uuid;
use std::fs;

use monumenta::player::Player;

fn usage() {
    println!("Usage: weekly_update_players path/to/directory");
}

const INSTANCE_WEEK_OFFSET: i32 = 1000;

fn update_instance_scores(scores: &mut HashMap<String, i32>, objective: &str, max: i32, additional_objectives_to_reset: &[&str]) {
    if let Some(access) = scores.get(objective) {
        if *access >= 1 {
            let mut access: i32 = *access;
            access += INSTANCE_WEEK_OFFSET;
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
         * These scores increment by 1000 or if >= max are reset to 0, along with resetting
         * the additional objectives listed at the end
         */
        update_instance_scores(scores, "D0Access", 3 * INSTANCE_WEEK_OFFSET, &["D0Finished"]);
        update_instance_scores(scores, "D1Access", 3 * INSTANCE_WEEK_OFFSET, &["D1Finished", "D1Delve1", "D1Delve2"]);
        update_instance_scores(scores, "D2Access", 3 * INSTANCE_WEEK_OFFSET, &["D2Finished", "D2Delve1", "D2Delve2"]);
        update_instance_scores(scores, "D3Access", 3 * INSTANCE_WEEK_OFFSET, &["D3Finished", "D3Delve1", "D3Delve2"]);
        update_instance_scores(scores, "D4Access", 3 * INSTANCE_WEEK_OFFSET, &["D4Finished", "D4Delve1", "D4Delve2"]);
        update_instance_scores(scores, "D5Access", 3 * INSTANCE_WEEK_OFFSET, &["D5Finished", "D5Delve1", "D5Delve2"]);
        update_instance_scores(scores, "D6Access", 3 * INSTANCE_WEEK_OFFSET, &["D6Finished", "D6Delve1", "D6Delve2"]);
        update_instance_scores(scores, "D7Access", 3 * INSTANCE_WEEK_OFFSET, &["D7Finished", "D7Delve1", "D7Delve2"]);
        update_instance_scores(scores, "D8Access", 3 * INSTANCE_WEEK_OFFSET, &["D8Finished", "D8Delve1", "D8Delve2"]);
        update_instance_scores(scores, "D9Access", 3 * INSTANCE_WEEK_OFFSET, &["D9Finished", "D9Delve1", "D9Delve2"]);
        update_instance_scores(scores, "D10Access", 3 * INSTANCE_WEEK_OFFSET, &["D10Finished", "D10Delve1", "D10Delve2"]);
        update_instance_scores(scores, "D11Access", 3 * INSTANCE_WEEK_OFFSET, &["D11Finished", "D11Delve1", "D11Delve2"]);
        update_instance_scores(scores, "DTLAccess", 3 * INSTANCE_WEEK_OFFSET, &["DTLFinished", "DTLDelve1", "DTLDelve2"]);
        update_instance_scores(scores, "DCAccess", 3 * INSTANCE_WEEK_OFFSET, &["DCFinished", "DMRDelve1", "DMRDelve2"]);
        update_instance_scores(scores, "DB1Access", 3 * INSTANCE_WEEK_OFFSET, &["DB1Finished", "DWDelve1", "DWDelve2"]);
        update_instance_scores(scores, "DRL2Access", 3 * INSTANCE_WEEK_OFFSET, &["DRL2Finished", "DSCDelve1", "DSCDelve2"]);
        update_instance_scores(scores, "DFFAccess", 3 * INSTANCE_WEEK_OFFSET, &["DFFFinished", "DFFDelve1", "DFFDelve2"]);
        update_instance_scores(scores, "DS1Access", 3 * INSTANCE_WEEK_OFFSET, &["DS1Finished"]);
        update_instance_scores(scores, "DS1Finished", 1, &["DS1Access"]);

        /* DelveDungeon score also increments as if it was a dungeon score */
        update_instance_scores(scores, "DelveDungeon", 3 * INSTANCE_WEEK_OFFSET, &[]);

        /* These scores are always reset to 0 */
        scores.insert("DRAccess".to_string(), 0);
        scores.insert("DRDAccess".to_string(), 0);

        fix_total_level(scores);
    }
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

    /* Need to do more work to figure out what uuids are being loaded */
    for entry in fs::read_dir(Path::new(&basedir).join("playerdata"))? {
        if let Ok(file) = entry {
            let path = file.path();
            if path.extension().unwrap() == "dat" {
                let uuid = Uuid::parse_str(path.file_stem().unwrap().to_str().unwrap()).unwrap();

                /* Now that we have a UUID, load it from the base path and push it to redis */

                let mut player = Player::new(uuid);
                player.load_dir(basedir.to_str().unwrap())?;

                player.update_history("Weekly update");
                update_player_scores(&mut player);

                /* Remove all the per-shard data except plots */
                if let Some(sharddata) = &mut player.sharddata {
                    sharddata.retain(|key, _| key == "plots");
                }

                player.save_dir(basedir.to_str().unwrap())?;
            }
        }
    }

    Ok(())
}

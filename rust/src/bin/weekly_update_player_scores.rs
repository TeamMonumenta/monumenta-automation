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
    println!("Usage: weekly_update_players path/to/directory");
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

fn fix_rush_scores(scores: &mut HashMap<String, i32>) {
    let remnant_objective: &str = "RemnantUnlocked";

    let rush_down_objective: &str = "RushDown";
    if let Some(rush_down_score) = scores.get(rush_down_objective)
        && *rush_down_score >= 40
    {
        scores.insert(remnant_objective.to_string(), 1);
    }
    // Additional plugin code required first
    //scores.insert(rush_down_objective.to_string(), 0);

    let rush_duo_objective: &str = "RushDuo";
    if let Some(rush_duo_score) = scores.get(rush_duo_objective)
        && *rush_duo_score >= 80
    {
        scores.insert(remnant_objective.to_string(), 1);
    }
    // Additional plugin code required first
    //scores.insert(rush_duo_objective.to_string(), 0);
}


fn cap_race_times(scores: &mut HashMap<String, i32>, race_objective: &str, min_time: i32) {
    if let Some(race_time) = scores.get(race_objective) {
        if *race_time != 0 && *race_time < min_time {
            scores.insert(race_objective.to_string(), min_time);
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
    let CorrectedLevel = 2
        + if White > 0 { 1 } else { 0 }
        + if Orange > 0 { 1 } else { 0 }
        + if Magenta > 0 { 1 } else { 0 }
        + if LightBlue > 0 { 1 } else { 0 }
        + if Yellow > 0 { 1 } else { 0 }
        + if Lime > 0 { 1 } else { 0 }
        + if Cyan > 0 { 1 } else { 0 }
        + if LightGray > 0 { 1 } else { 0 };

    scores.insert("TotalLevel".to_string(), CorrectedLevel);
}

fn update_player_scores(player: &mut Player, days_since_epoch: i32) {
    if let Some(scores) = &mut player.scores {
        /* Reset dungeon scores if their StartDate is more than old enough for them to expire */
        update_instance_scores(scores, days_since_epoch, "D0StartDate", 28, &["D0Access", "D0Finished"]);
        update_instance_scores(scores, days_since_epoch, "D1StartDate", 28, &["D1Access", "D1Finished"]);
        update_instance_scores(scores, days_since_epoch, "D2StartDate", 28, &["D2Access", "D2Finished"]);
        update_instance_scores(scores, days_since_epoch, "D3StartDate", 28, &["D3Access", "D3Finished"]);
        update_instance_scores(scores, days_since_epoch, "D4StartDate", 28, &["D4Access", "D4Finished"]);
        update_instance_scores(scores, days_since_epoch, "D5StartDate", 28, &["D5Access", "D5Finished"]);
        update_instance_scores(scores, days_since_epoch, "D6StartDate", 28, &["D6Access", "D6Finished"]);
        update_instance_scores(scores, days_since_epoch, "D7StartDate", 28, &["D7Access", "D7Finished"]);
        update_instance_scores(scores, days_since_epoch, "D8StartDate", 28, &["D8Access", "D8Finished"]);
        update_instance_scores(scores, days_since_epoch, "D9StartDate", 28, &["D9Access", "D9Finished"]);
        update_instance_scores(scores, days_since_epoch, "D10StartDate", 28, &["D10Access", "D10Finished"]);
        update_instance_scores(scores, days_since_epoch, "D11StartDate", 28, &["D11Access", "D11Finished"]);
        update_instance_scores(scores, days_since_epoch, "D12StartDate", 28, &["D12Access", "D12Finished"]);
        update_instance_scores(scores, days_since_epoch, "D13StartDate", 28, &["D13Access", "D13Finished"]);
        update_instance_scores(scores, days_since_epoch, "DTLStartDate", 28, &["DTLAccess", "DTLFinished"]);
        update_instance_scores(scores, days_since_epoch, "DMRStartDate", 28, &["DCAccess", "DCFinished"]);
        update_instance_scores(scores, days_since_epoch, "DBWStartDate", 28, &["DB1Access", "DB1Finished"]);
        update_instance_scores(scores, days_since_epoch, "DCSStartDate", 28, &["DRL2Access", "DRL2Finished"]);
        update_instance_scores(scores, days_since_epoch, "DFFStartDate", 28, &["DFFAccess", "DFFFinished"]);
        update_instance_scores(scores, days_since_epoch, "DHFStartDate", 28, &["DHFAccess", "DHFChests"]);
        update_instance_scores(scores, days_since_epoch, "DSKTStartDate", 14, &["DSKTAccess", "DSKTChests"]);
        update_instance_scores(scores, days_since_epoch, "DIStartDate", 28, &["DIAccess", "DIFinished"]);

        /* DelveDungeon score also resets as if it was a dungeon score */
        update_instance_scores(scores, days_since_epoch, "DelveStartDate", 28, &["DelveDungeon"]);

        /* Temporary change to reset Rush wave completion leaderboards and grant access to the Remnant */
        fix_rush_scores(scores);

        /* These scores are always reset to 0 */
        scores.insert("DRAccess".to_string(), 0);
        scores.insert("DRDAccess".to_string(), 0);
        // Sanctum & Verdant
        scores.insert("R1Access".to_string(), 0);
        // Remorse & Mist
        scores.insert("R2Access".to_string(), 0);
        scores.insert("DDAccess".to_string(), 0);
        // Ring scores
        scores.insert("DR3Access".to_string(), 0);
        scores.insert("DGAccess".to_string(), 0);
        scores.insert("DPSAccess".to_string(), 0);
        scores.insert("DMASAccess".to_string(), 0);
        scores.insert("GodsporeAccess".to_string(), 0);
        scores.insert("AzacorAccess".to_string(), 0);
        scores.insert("DCZAccess".to_string(), 0);

        /* Temporary - reset all race scores */

        // All For Nera @ isles/all_for_nera.json
        cap_race_times(scores, "Race2-01", 57000);
        // Blood Rush @ white/blood_rush.json
        cap_race_times(scores, "RaceD-01", 162000);
        // Bursting Bonus @ willows/bursting_bonus.json
        cap_race_times(scores, "RaceD-W", 45000);
        // C'Ircuit @ reverie/circuit.json
        cap_race_times(scores, "RaceD-R", 298000);
        // City Tour @ ring/citytour.json
        cap_race_times(scores, "Race3-CityTour", 24000);
        // Coastal Circuit @ ring/portmanteau.json
        cap_race_times(scores, "Race3-CoastalCircuit", 34000);
        // Delivery Dash @ isles/delivery_dash.json
        cap_race_times(scores, "DeliveryDash", 91000);
        // Elemental Shuffle @ valley/elementalshuffle.json
        cap_race_times(scores, "Race04", 141000);
        // Fast Whispers @ isles/fast_whispers.json
        cap_race_times(scores, "Race2-04", 49000);
        // Get The Cluck Out @ valley/GetTheCluckOut.json
        cap_race_times(scores, "getthecluckout", 29000);
        // Grappler Effect @ indigo/grapplereffect.json
        cap_race_times(scores, "RaceD-17", 550000);
        // High to Low @ valley/hightolow.json
        cap_race_times(scores, "Race03", 92000);
        // Hook Hell @ indigo/hookhell.json
        cap_race_times(scores, "Race3-HookHell", 37000);
        // Jungle Jaunt @ valley/jungle_jaunt.json
        cap_race_times(scores, "Race01New", 29000);
        // Light Footed @ lightgray/light_footed.json
        cap_race_times(scores, "RaceD-10", 211000);
        // Mariya's Game @ valley/mariya_new.json
        cap_race_times(scores, "Race02New", 50000);
        // Miasma Theory @ magenta/miasma_theory.json
        cap_race_times(scores, "RaceD-03", 213000);
        // Mind's Eye @ cyan/minds_eye.json
        cap_race_times(scores, "RaceD-11", 314000);
        // Misty Waters @ isles/misty_waters_new.json
        cap_race_times(scores, "Race2-03New", 42000);
        // P-Zero Wintery Shroomland Times @ valley/pzero_wintery_shroomland.json
        cap_race_times(scores, "PZero-WinteryShroomland", 72000);
        // Pirate Pass @ purple/pirate_pass.json
        cap_race_times(scores, "RaceD-12", 216000);
        // Quicksand @ gray/sand_struggles.json
        cap_race_times(scores, "RaceD-09", 264000);
        // Rapid Ascent @ ring/rapidascent.json
        cap_race_times(scores, "Race3-RapidAscent", 35000);
        // Royal Gambit @ valley/royalgambit.json
        cap_race_times(scores, "RoyalGambitRace", 56100);
        // Ruined Run @ lime/ruined_run.json
        cap_race_times(scores, "RaceD-07", 210000);
        // Runners of Mist @ isles/runners_of_mist.json
        cap_race_times(scores, "Race2-02", 39000);
        // Season's Grace @ pink/seasons_grace.json
        cap_race_times(scores, "RaceD-08", 313000);
        // Shift Clicking @ shiftingcity/shift_clicking.json
        cap_race_times(scores, "RaceD-SC", 250000);
        // Silver Surfer @ skt/silver_surfer.json
        cap_race_times(scores, "RaceD-SKT", 278000);
        // Six Shot Sprint @ isles/six_shot_sprint.json
        cap_race_times(scores, "Race2-07", 100000);
        // Speed Fitness @ isles/speed_fitness.json
        cap_race_times(scores, "Race2-06", 39000);
        // Speed Reading @ forum/speed_reading.json
        cap_race_times(scores, "RaceD-14", 464000);
        // Speedsworn @ valley/speedsworn.json
        cap_race_times(scores, "RaceD-04", 598000);
        // Swift Alchemy @ labs/swift_alchemy.json
        cap_race_times(scores, "RaceD-00", 59000);
        // They Toll for Thee @ ring/starpointbellrace.json
        cap_race_times(scores, "StarpointBellRace", 87000);
        // Time Flies @ teal/time_flies.json
        cap_race_times(scores, "RaceD-13", 365000);
        // Trackmaster @ isles/trackmaster.json
        cap_race_times(scores, "Race2-05", 59000);
        // Treks Machina @ brown/treks_machina.json
        cap_race_times(scores, "RaceD-16", 417000);
        // Truly Occult @ lightblue/truly_occult.json
        cap_race_times(scores, "RaceD-05", 350000);
        // Tutorial+ @ valley/tutorialplus.json
        cap_race_times(scores, "Race00", 96000);
        // Velara-ocity @ valley/velaraocity.json
        cap_race_times(scores, "Velaraocity", 44000);
        // Wild Waltz @ yellow/wild_waltz.json
        cap_race_times(scores, "RaceD-06", 598000);
        // Witchhiking @ blue/witchhiking.json
        cap_race_times(scores, "RaceD-15", 251000);
        // Zoo Tour @ orange/zoo_tour.json
        cap_race_times(scores, "RaceD-02", 125000);

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

        player.save_dir(basedirpath).unwrap();
    });

    let end = Utc::now().time(); // STOP
    println!("Updated {} players in {} milliseconds", uuids.len(), (end - start).num_milliseconds());

    Ok(())
}

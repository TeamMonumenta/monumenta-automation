use monumenta::player::Player;

use anyhow;
use simplelog::*;

use std::{
    env,
    fs::File,
    io::{prelude::*, BufReader}
};

fn main() -> anyhow::Result<()> {
    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 3 {
        println!("Usage: redis_reset_scores <domain> <objectives_list_file>");
        return Ok(());
    }

    args.remove(0);

    let domain = args.remove(0);
    let objectives_file = args.remove(0);
    let mut objectives = vec!();

    let file = File::open(objectives_file)?;
    let reader = BufReader::new(file);

    for line in reader.lines() {
        let mut objective = line?;
        objective.retain(|c| !c.is_whitespace());
        objectives.push(objective);
    }

    println!("Objectives to remove:");
    for objective in &objectives {
        println!("  {}", objective);
    }

    let client = redis::Client::open("redis://127.0.0.1/")?;
    let mut con : redis::Connection = client.get_connection()?;

    println!("Removing objectives...");

    let mut num_players = 0;
    for (_, player) in Player::get_redis_players(&domain, &mut con)?.iter_mut() {
        player.load_redis(&domain, &mut con)?;
        if let Some(scores) = &mut player.scores {
            for objective in &objectives {
                scores.remove(objective);
            }
            player.update_history(&format!("Removed {} scoreboard objectives", objectives.len()));
            player.save_redis(&domain, &mut con)?;
            num_players = num_players + 1;
        }
    }

    println!("Removed {} objectives from {} players", objectives.len(), num_players);

    Ok(())
}

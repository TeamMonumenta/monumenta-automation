use monumenta::player::Player;

use anyhow;
use simplelog::*;

use std::env;

fn main() -> anyhow::Result<()> {
    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 3 {
        println!("Usage: redis_reset_scores <domain> <objective>");
        return Ok(());
    }

    args.remove(0);

    let domain = args.remove(0);
    let objective = args.remove(0);

    let client = redis::Client::open("redis://127.0.0.1/")?;
    let mut con: redis::Connection = client.get_connection()?;

    for (_, player) in Player::get_redis_players(&domain, &mut con)?.iter_mut() {
        player.load_redis(&domain, &mut con)?;
        if let Some(scores) = &mut player.scores {
            scores.insert(objective.to_string(), 0);
            player.update_history(&format!("Reset scores for {}", &objective));
            player.save_redis(&domain, &mut con)?;
        }
        println!("{}", player);
    }

    Ok(())
}

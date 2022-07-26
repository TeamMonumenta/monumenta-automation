use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::env;
use simplelog::*;
use log::warn;

use monumenta::player::Player;

fn increment_player_start_dates(con: &mut redis::Connection,
                                domain: &str,
                                player: &mut Player,
                                amount: i32,
                                history: &str) -> BoxResult<()> {
    player.load_redis_scores(&domain, con)?;
    if let Some(scores) = &mut player.scores {
        for (objective, value) in scores.iter_mut() {
            if !(*objective).contains("StartDate") {
                continue;
            }
            if *value <= 0 {
                continue;
            }
            *value += amount;
        }
    }
    player.update_history(&history);
    player.save_redis(&domain, con)?;

    Ok(())
}

fn main() -> BoxResult<()> {

    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 5 {
        println!("Usage: redis_set_offline_player_score <redis_uri> <domain> <amount> <description>");
        println!("For example:");
        println!("  redis_set_offline_player_score 'redis://127.0.0.1/' play 1 'Make up for day of downtime'");
        return Ok(());
    }

    args.remove(0);

    let redis_uri = args.remove(0);
    let domain = args.remove(0);
    let amount = args.remove(0).parse::<i32>().unwrap();
    let history = args.remove(0);

    let client = redis::Client::open(redis_uri)?;
    let mut con : redis::Connection = client.get_connection()?;

    println!("Incrementing player start dates by {}", amount);
    for (uuid, player) in Player::get_redis_players(&domain, &mut con)?.iter_mut() {
        if let Err(err) = increment_player_start_dates(&mut con, &domain, player, amount, &history) {
            warn!("Player {} failed - their StartDate scores will not be updated: {}", uuid, err);
        }
    }

    Ok(())
}

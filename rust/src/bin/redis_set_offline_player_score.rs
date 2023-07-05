use std::error::Error;
type BoxResult<T> = Result<T, Box<dyn Error>>;

use redis::Commands;
use simplelog::*;
use std::env;
use uuid::Uuid;

use monumenta::player::Player;

fn main() -> BoxResult<()> {
    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 7 {
        println!("Usage: redis_set_offline_player_score <redis_uri> <domain> <player> <objective> <value> <description>");
        println!("For example:");
        println!("  redis_set_offline_player_score 'redis://127.0.0.1/' play Combustible temp 0 'Reset temp value'");
        return Ok(());
    }

    args.remove(0);

    let redis_uri = args.remove(0);
    let domain = args.remove(0);
    let playername = args.remove(0);
    let objective = args.remove(0);
    let value = args.remove(0).parse::<i32>().unwrap();
    let history = args.remove(0);

    let client = redis::Client::open(redis_uri)?;
    let mut con: redis::Connection = client.get_connection()?;

    println!("Loading {}", playername);
    let uuid_str: String = con.hget("name2uuid", playername.to_string())?;
    let uuid: Uuid = Uuid::parse_str(&uuid_str).unwrap();
    let mut player = Player::new(uuid);
    player.load_redis(&domain, &mut con)?;
    if let Some(scores) = &mut player.scores {
        scores.insert(objective.to_string(), value);
        player.update_history(&history);
        player.save_redis(&domain, &mut con)?;
    }
    println!("{}'s {} score has been set to {}", player, objective, value);
    println!("Note - if the player is currently logged in, this did nothing!");

    Ok(())
}

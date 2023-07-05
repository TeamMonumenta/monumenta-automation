#[macro_use]
extern crate log;

use std::error::Error;
type BoxResult<T> = Result<T, Box<dyn Error>>;

use redis::Commands;
use simplelog::*;
use std::env;
use uuid::Uuid;

use monumenta::player::Player;

fn usage() {
    println!("Usage: leaderboard_update_redis 'redis://127.0.0.1/' <domain> leaderboards.yaml");
}

fn update_player_leaderboards(
    uuid: &Uuid,
    player: &mut Player,
    leaderboards: &Vec<String>,
    con: &mut redis::Connection,
    domain: &str,
) -> BoxResult<()> {
    player.load_redis_scores(&domain, con)?;

    let name: String = con.hget("uuid2name", uuid.to_hyphenated().to_string())?;

    for leaderboard in leaderboards.iter() {
        if let Some(score) = player.scores.as_ref().unwrap().get(leaderboard) {
            if *score > 0 {
                let _: () = con.zadd(
                    format!("{}:leaderboard:{}", domain, leaderboard),
                    &name,
                    *score as f32,
                )?;
            }
        }
    }

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

    if args.len() != 4 {
        usage();
        return Ok(());
    }

    args.remove(0);

    let redis_uri = args.remove(0);

    let domain = args.remove(0);

    // Get and read leaderboards yaml
    let leaderboards = args.remove(0);
    let leaderboards = std::fs::File::open(leaderboards)?;
    let leaderboards: Vec<String> = serde_yaml::from_reader(leaderboards)?;

    println!("Updating leaderboards:");
    for leaderboard in leaderboards.iter() {
        println!("  {}", leaderboard);
    }

    let client = redis::Client::open(redis_uri)?;
    let mut con: redis::Connection = client.get_connection()?;

    /* Remove all leaderboards */
    for leaderboard in leaderboards.iter() {
        let _: () = con.del(format!("{}:leaderboard:{}", domain, leaderboard))?;
    }

    /* Add all current non-zero player scores to the leaderboards */
    println!("\nUpdating player scores on leaderboards...");
    for (uuid, player) in Player::get_redis_players(&domain, &mut con)?.iter_mut() {
        if let Err(err) = update_player_leaderboards(uuid, player, &leaderboards, &mut con, &domain)
        {
            warn!(
                "Player {} failed - their leaderboards will not be updated: {}",
                uuid, err
            );
        }
    }

    println!("\nDone.");

    Ok(())
}

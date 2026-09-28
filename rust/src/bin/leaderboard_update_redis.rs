use monumenta::{leaderboards, player::Player};

use log::warn;
use redis::Commands;
use simplelog::*;
use uuid::Uuid;

use std::env;

fn usage() {
    println!("Usage: leaderboard_update_redis 'redis://127.0.0.1/' <domain> <lb-config-dir>");
}

fn update_player_leaderboards(
    uuid: &Uuid,
    player: &mut Player,
    leaderboards: &[String],
    con: &mut redis::Connection,
    domain: &str,
) -> anyhow::Result<()> {
    player.load_redis_scores(domain, con)?;

    let name: String = con.hget("uuid2name", uuid.hyphenated().to_string())?;

    for leaderboard in leaderboards.iter() {
        if let Some(score) = player.scores.as_ref().unwrap().get(leaderboard)
            && *score > 0
        {
            let _: () = con.zadd(format!("{}:leaderboard:{}", domain, leaderboard), &name, *score as f32)?;
        }
    }

    Ok(())
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

    if args.len() != 4 {
        usage();
        return Ok(());
    }

    args.remove(0);

    let redis_uri = args.remove(0);

    let domain = args.remove(0);

    // Get and read leaderboard config files
    let leaderboard_config_dir = args.remove(0);
    let leaderboards: Vec<String> = leaderboards::load_configs(&leaderboard_config_dir)?
        .into_iter()
        .map(|cfg| cfg.objective)
        .collect();

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
        if let Err(err) = update_player_leaderboards(uuid, player, &leaderboards, &mut con, &domain) {
            warn!("Player {} failed - their leaderboards will not be updated: {}", uuid, err);
        }
    }

    println!("\nDone.");

    Ok(())
}

use monumenta::player::Player;

use anyhow::anyhow;
use log::{info, warn};
use redis::{Commands, RedisResult};
use simplelog::*;
use uuid::Uuid;

use std::env;

fn main() -> anyhow::Result<()> {
    CombinedLogger::init(vec![TermLogger::new(
        LevelFilter::Debug,
        Config::default(),
        TerminalMode::Mixed,
        ColorChoice::Auto,
    ) as Box<dyn SharedLogger>])
    .unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 5 {
        println!("Usage: {} 'redis://127.0.0.1/' <domain> <from_player_name> <backup_dir>", args.remove(0));
        return Ok(());
    }

    args.remove(0);

    let redis_uri = args.remove(0);
    let client = redis::Client::open(redis_uri)?;
    let mut con: redis::Connection = client.get_connection()?;

    let domain = args.remove(0);

    let inputname = args.remove(0);
    let inputuuid: RedisResult<String> = con.hget("name2uuid", &inputname);
    if let Err(err) = inputuuid {
        warn!(
            "Failed to look up player's UUID, possibly name spelled wrong? (It is case sensitive). Error was: {}",
            err
        );
        return Err(anyhow!(err));
    }

    let inputuuid: Uuid = Uuid::parse_str(&inputuuid.unwrap())?;

    let backupdir = args.remove(0);

    let mut inputplayer = Player::new(inputuuid);
    inputplayer.load_redis(&domain, &mut con)?;

    if let Err(err) = inputplayer.save_dir(&backupdir) {
        warn!("Failed to save player {} domain {} to backup directory {}: {}", inputname, domain, backupdir, err);
        return Err(err);
    }

    if let Err(err) = inputplayer.del(&domain, &mut con) {
        warn!("Failed to delete original player {} domain {}: {}", inputuuid, domain, err);
        return Err(err);
    }

    info!("Successfully deleted original player data for user {} domain {}", &inputname, &domain);

    Ok(())
}

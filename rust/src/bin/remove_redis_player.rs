use monumenta::player::Player;

use anyhow;
use log::{info, warn};
use redis::Commands;
use simplelog::*;
use std::env;
use uuid::Uuid;

type BoxResult<T> = Result<T, anyhow::Error>;

fn main() -> BoxResult<()> {
    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 4 {
        println!(
            "Usage: {} <domain> <from_player_name> <backup_dir>",
            args.remove(0)
        );
        return Ok(());
    }

    args.remove(0);

    let client = redis::Client::open("redis://127.0.0.1/")?;
    let mut con: redis::Connection = client.get_connection()?;

    let domain = args.remove(0);

    let inputname = args.remove(0);
    let inputuuid: String = con.hget("name2uuid", &inputname)?;
    let inputuuid: Uuid = Uuid::parse_str(&inputuuid)?;

    let backupdir = args.remove(0);

    let mut inputplayer = Player::new(inputuuid);
    inputplayer.load_redis(&domain, &mut con)?;

    if let Err(err) = inputplayer.save_dir(&backupdir) {
        warn!(
            "Failed to save player {} domain {} to backup directory {}: {}",
            inputname, domain, backupdir, err
        );
        return Err(err);
    }

    if let Err(err) = inputplayer.del(&domain, &mut con) {
        warn!(
            "Failed to delete original player {} domain {}: {}",
            inputuuid, domain, err
        );
        return Err(err);
    }

    info!(
        "Successfully deleted original player data for user {} domain {}",
        &inputname, &domain
    );

    Ok(())
}

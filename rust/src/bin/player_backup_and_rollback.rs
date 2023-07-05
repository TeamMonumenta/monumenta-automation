use monumenta::player::Player;

use anyhow::{self, bail};
use redis::Commands;
use simplelog::*;
use uuid::Uuid;

use std::{env, path::Path};

fn main() -> anyhow::Result<()> {
    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 6 {
        bail!("Usage: player_backup_and_rollback 'redis://127.0.0.1/' <domain> <player> <inputdirectory> <backupdir>");
    }

    args.remove(0); // Program name

    let redis_uri = args.remove(0);
    let client = redis::Client::open(redis_uri)?;
    let mut con: redis::Connection = client.get_connection()?;

    let domain = args.remove(0);
    let inputname = args.remove(0);
    let inputuuid: String = con.hget("name2uuid", &inputname)?;
    let inputuuid: Uuid = Uuid::parse_str(&inputuuid)?;

    // Get the path to the input directory
    let indirstr = args.remove(0);
    let indir = Path::new(&indirstr);
    if !indir.is_dir() {
        bail!("Input directory does not exist");
    }

    // Get the path to the output directory
    let backupdirstr = args.remove(0);
    let backupdir = Path::new(&backupdirstr);
    if backupdir.is_dir() {
        bail!("Backup directory already exists");
    }

    // Load original player from redis
    let mut origplayer = Player::new(inputuuid);
    origplayer.load_redis(&domain, &mut con)?;

    // Load rollback player data from directory
    let mut rollbackplayer = Player::new(inputuuid);
    rollbackplayer.load_dir(&indirstr)?;

    // Save the original player to the backup directory
    if let Err(err) = origplayer.save_dir(&backupdirstr) {
        bail!(
            "Failed to save player {} domain {} to backup directory {}: {}",
            inputname,
            domain,
            backupdirstr,
            err
        );
    }

    // Save the rollback player to redis
    if let Err(err) = rollbackplayer.save_redis(&domain, &mut con) {
        bail!(
            "Failed to save player {} domain {} to redis: {}",
            inputname,
            domain,
            err
        );
    }

    Ok(())
}

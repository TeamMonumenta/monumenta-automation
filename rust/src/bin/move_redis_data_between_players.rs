use monumenta::player::Player;

use anyhow::{self, bail};
use log::{info, warn};
use redis::Commands;
use simplelog::*;
use uuid::Uuid;

use std::env;

fn main() -> anyhow::Result<()> {
    let mut multiple = vec![];
    multiple.push(TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed, ColorChoice::Auto) as Box<dyn SharedLogger>);
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 6 {
        bail!("Usage: {} 'redis://127.0.0.1/' <domain> <from_player_name> <to_player_name> <backup_dir>", args.remove(0));
    }

    args.remove(0);

    let redis_uri = args.remove(0);
    let client = redis::Client::open(redis_uri)?;
    let mut con : redis::Connection = client.get_connection()?;

    let domain = args.remove(0);

    let inputname = args.remove(0);
    let inputuuid: String = con.hget("name2uuid", &inputname)?;
    let inputuuid: Uuid = Uuid::parse_str(&inputuuid)?;

    let outputname = args.remove(0);
    let outputuuid: String = con.hget("name2uuid", &outputname)?;
    let outputuuid: Uuid = Uuid::parse_str(&outputuuid)?;

    let backupdir = args.remove(0);

    let mut inputplayer = Player::new(inputuuid);
    inputplayer.load_redis(&domain, &mut con)?;

    let bungeelocs = format!("{}:bungee:locations", domain);
    let inputlocation: String = con.hget(&bungeelocs, inputuuid.hyphenated().to_string())?;

    if let Err(err) = inputplayer.save_dir(&backupdir) {
        warn!("Failed to save player {} domain {} to backup directory {}: {}", inputname, domain, backupdir, err);
        return Err(err);
    }

    let mut outputplayer = inputplayer.clone();
    outputplayer.uuid = outputuuid;

    // TODO: Need to update remote data for plot access records

    outputplayer.update_history(&format!("Import from {}", &inputname));

    if let Err(err) = outputplayer.save_redis(&domain, &mut con) {
        warn!("Failed to save player {} domain {} to redis: {}", outputuuid, domain, err);
        return Err(err);
    }

    info!("Successfully copied player data from {} to {} for domain {}", &inputname, &outputname, &domain);

    if let Err(err) = inputplayer.del(&domain, &mut con) {
        warn!("Failed to delete original player {} domain {}: {}", inputuuid, domain, err);
        return Err(err);
    }

    // Delete the location record for bungee, moving the player back to the default
    con.hdel(&bungeelocs, inputuuid.hyphenated().to_string())?;
    // Move the new player to the location of the old player
    con.hset(&bungeelocs, outputuuid.hyphenated().to_string(), inputlocation)?;

    info!("Successfully deleted original player data for user {} domain {}", &inputname, &domain);


    Ok(())
}

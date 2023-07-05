use monumenta::player::Player;

use anyhow;
use simplelog::*;

use std::{
    env,
    fs,
    path::Path
};

fn usage() {
    println!("Usage: export_redis_advancements 'redis://127.0.0.1/' <domain> path/to/advancements");
}

fn main() -> anyhow::Result<()> {
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

    // Get the path to the output advancements directory
    let basedir = args.remove(0);
    let basedir = Path::new(&basedir);
    if !basedir.is_dir() {
        fs::create_dir_all(basedir.to_str().unwrap())?;
    }

    let client = redis::Client::open(redis_uri)?;
    let mut con: redis::Connection = client.get_connection()?;

    println!("Exporting advancements...");
    // Iterate while at the same time removing the elements from the returned map
    Player::get_redis_players(&domain, &mut con)?.retain(|uuid, player| {
        let uuidstr = uuid.to_hyphenated().to_string();
        player.load_redis_advancements(&domain, &mut con).unwrap();
        player
            .save_file_advancements(basedir.join(format!("{}.json", uuidstr)).to_str().unwrap())
            .unwrap();
        drop(player);
        false
    });
    println!("Done");

    Ok(())
}

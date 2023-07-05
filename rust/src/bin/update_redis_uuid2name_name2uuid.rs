use monumenta::player::Player;

use anyhow;
use redis::Commands;
use simplelog::*;

use std::{
    collections::HashMap,
    env
};

fn main() -> anyhow::Result<()> {
    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 3 {
        println!("Usage: save_playerdata_to_redis 'redis://127.0.0.1/' <domain>");
        return Ok(());
    }

    args.remove(0);

    let redis_uri = args.remove(0);
    let domain = args.remove(0);

    let mut uuid2name: HashMap<String, String> = HashMap::new();

    let client = redis::Client::open(redis_uri)?;
    let mut con : redis::Connection = client.get_connection()?;

    for (uuid, player) in Player::get_redis_players(&domain, &mut con)?.iter_mut() {
        player.load_redis(&domain, &mut con)?;
        if let Some(name) = &player.name {
            let uuidstr = uuid.to_hyphenated().to_string();
            let _: () = con.hset("uuid2name", &uuidstr, name)?;
            let _: () = con.hset("name2uuid", name, &uuidstr)?;
            uuid2name.insert(uuidstr.to_string(), name.to_string());
        }
    }

    println!("\n\nuuid2name:{:?}", uuid2name);

    Ok(())
}

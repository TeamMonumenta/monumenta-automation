use monumenta::player::Player;

use redis::Commands;
use simplelog::*;

use std::{collections::HashMap, env};

fn usage() {
    println!("Usage: redis_upgrade_plugindata_format <domain>");
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

    if args.len() < 2 {
        usage();
        return Ok(());
    }

    args.remove(0);

    let redis_uri = "redis://127.0.0.1/";
    let domain = args.remove(0);

    let client = redis::Client::open(redis_uri)?;
    let mut con: redis::Connection = client.get_connection()?;

    for (uuid, player) in Player::get_redis_players(&domain, &mut con)?.iter_mut() {
        if let Ok(oldplugindata) = con.hgetall(format!("{}:playerdata:{}:plugindata", domain, uuid.hyphenated())) {
            /* There is plugindata here */
            let oldplugindata: HashMap<String, String> = oldplugindata;
            let mut newplugindata = HashMap::new();
            for (key, value) in oldplugindata.iter() {
                let value: serde_json::Value = serde_json::from_str(value)?;
                newplugindata.insert(key.to_string(), value);
            }
            player.plugindata = Some(newplugindata);
            /* Clear out the old style data */
            let _: () = con.del(format!("{}:playerdata:{}:plugindata", domain, uuid.hyphenated()))?;
        } else {
            /* No plugindata found - try the new format */
            if player.load_redis_plugindata(&domain, &mut con).is_err() {
                /* Also no data under plugins (the new path) -> create some default data */
                player.plugindata = Some(HashMap::new());
            }
        }

        player.save_redis_plugindata(&domain, &mut con)?;

        println!("{}", player);
    }

    Ok(())
}

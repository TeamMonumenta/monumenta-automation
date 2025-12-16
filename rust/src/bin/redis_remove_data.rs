use redis::Commands;
use simplelog::*;

use std::env;

fn usage() {
    println!("Usage: redis_playerdata_save_load 'redis://127.0.0.1/' <pattern>");
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

    if args.len() < 3 {
        usage();
        return Ok(());
    }

    args.remove(0);

    let redis_uri = args.remove(0);
    let pattern = args.remove(0);

    let mut confirm = false;
    if !args.is_empty() {
        let confirm_arg = args.remove(0);
        if confirm_arg == "--confirm" {
            confirm = true;
        }
    }

    let client = redis::Client::open(redis_uri)?;
    let mut con: redis::Connection = client.get_connection()?;

    println!("Removing data matching '{}'", pattern);
    let keys: Vec<String> = con.keys(pattern)?;
    for chunk in keys.chunks(20) {
        let mut pipe = redis::pipe();
        for key in chunk {
            if confirm {
                pipe.cmd("UNLINK").arg(key);
            } else {
                println!("{:?}", key);
            }
        }
        if confirm {
            pipe.query::<()>(&mut con)?;
        }
    }

    if keys.is_empty() {
        println!("No matching data found");
    } else if !confirm {
        println!("Matched {} keys\nTo actually execute this operation, add --confirm", keys.len());
    } else {
        println!("Removed {} keys", keys.len());
    }

    Ok(())
}

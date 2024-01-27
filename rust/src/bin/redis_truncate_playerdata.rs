use monumenta::player::Player;

use anyhow::{self, bail};
use clap::Parser;
use rayon::prelude::*;
use simplelog::*;
use uuid::Uuid;
use std::cell::RefCell;

#[derive(Parser, Debug)]
/// Tool to move playerdata between redis to and from a local directory
pub struct Opts {
    /// The address to connect to redis, for example 'redis://127.0.0.1/'
    #[arg(required = true)]
    redis_uri: String,

    /// The domain to pull data from, for example 'play', 'build', 'playerbuild', ...
    #[arg(required = true)]
    domain: String,

    /// How much data to keep
    #[arg(required = true)]
    history_amount_to_keep: u16,
}

// Thread-local connection used to loop over players reusing the same
// connection per thread in the pool
thread_local!(static THREAD_CONNECTIONS: RefCell<Option<redis::Connection>> = RefCell::new(None));

fn main() -> anyhow::Result<()> {
    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let args = Opts::parse();

    if args.history_amount_to_keep < 1 {
        bail!("History amount to keep must be at least 1");
    }

    // Open the top-level redis client, and a connection for initial use
    let client = redis::Client::open(args.redis_uri.clone())?;
    let mut con : redis::Connection = client.get_connection()?;

    println!("Determining player uuids...");
    let uuids: Vec<Uuid> = Player::get_redis_players(&args.domain, &mut con)?.keys().map(|uuid: &Uuid| uuid.clone()).collect();
    println!("Truncating data for {} players to {} {}", uuids.len(), args.history_amount_to_keep, (if args.history_amount_to_keep == 1 {"entry"} else {"entries"}));
    uuids.par_iter().for_each(|uuid: &Uuid| {
        THREAD_CONNECTIONS.with(|cell| {
            let mut local_con = cell.borrow_mut();

            // Create a new connection once per thread if it is not initialized
            if local_con.is_none() {
                let con = client.get_connection();
                if let Err(err) = con {
                    eprintln!("Failed to open threaded connection: {}", err);
                    return;
                } else if let Ok(con) = con {
                    *local_con = Some(con);
                }
            }
            let mut con = local_con.as_mut().unwrap();

            let mut player = Player::new(uuid.to_owned());
            if let Err(err) = player.trim_redis_history(&args.domain, &mut con, args.history_amount_to_keep as isize) {
                eprintln!("Failed to trim history for player {}: {}", uuid,  err);
                return;
            }
        });
    });
    println!("Data for {} players truncated to {} {}", uuids.len(), args.history_amount_to_keep, (if args.history_amount_to_keep == 1 {"entry"} else {"entries"}));

    Ok(())
}

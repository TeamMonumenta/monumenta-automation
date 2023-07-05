use monumenta::player::Player;

use anyhow::{self, bail};
use clap::{Args, Parser, Subcommand};
use rayon::prelude::*;
use simplelog::*;
use uuid::Uuid;

use std::{
    cell::RefCell,
    fs,
    path::Path
};

#[derive(Parser, Debug)]
/// Tool to move playerdata between redis to and from a local directory
pub struct Opts {
    /// The address to connect to redis, for example 'redis://127.0.0.1/'
    #[arg(required = true)]
    redis_uri: String,

    /// The domain to pull data from, for example 'play', 'build', 'playerbuild', ...
    #[arg(required = true)]
    domain: String,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Args, Debug, Clone)]
pub struct InputOpts {
    path: String,

    /// Optional for --input mode, how much history to trim to after appending this data
    #[arg(default_value_t = u16::MAX)]
    history_amount_to_keep: u16,
}

#[derive(Args, Debug, Clone)]
pub struct OutputOpts {
    path: String,

    /// Optional argument for output mode to only retrieve one specific player
    player_name: Option<String>,
}


#[derive(Subcommand, Debug, Clone)]
enum Commands {
    #[command(name = "--input")]
    /// Input player data from the directory specified into redis
    INPUT(InputOpts),

    #[command(name = "--output")]
    /// Output player data from redis to the directory specified
    OUTPUT(OutputOpts),
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

    // Make sure directory exists / does not exist as appropriate for command
    if let Commands::OUTPUT(outargs) = &args.command {
        if Path::new(&outargs.path).is_dir() {
            bail!("Supplied output directory already exists!");
        }
    }
    if let Commands::INPUT(inargs) = &args.command {
        if !Path::new(&inargs.path).is_dir() {
            bail!("Supplied input directory does not exist");
        }
        if inargs.history_amount_to_keep < 1 {
            bail!("History amount to keep must be at least 1");
        }
    }

    // Open the top-level redis client, and a connection for initial use
    let client = redis::Client::open(args.redis_uri.clone())?;
    let mut con : redis::Connection = client.get_connection()?;

    match &args.command {
        Commands::OUTPUT(outargs) => {
            if let Some(player_name) = &outargs.player_name {
                // Caller requested just one player - fetch them
                let player = Player::from_name(player_name, &mut con)?;
                output_player(&player, &client, &args.domain, &outargs.path)
            } else {
                // Caller didn't specify a player to pull - fetch all of them
                Player::get_redis_players(&args.domain, &mut con)?.par_iter().for_each(|(_, player)| {
                    output_player(player, &client, &args.domain, &outargs.path)
                })
            }
        }
        Commands::INPUT(inargs) => {
            let basedir = Path::new(&inargs.path);
            /* Need to do more work to figure out what uuids are being loaded */
            let uuids: Vec<Uuid> = fs::read_dir(Path::new(&basedir).join("playerdata"))?.filter_map(|entry| {
                if let Ok(file) = entry {
                    let path = file.path();
                    if path.extension().unwrap() == "dat" {
                        return Some(Uuid::parse_str(path.file_stem().unwrap().to_str().unwrap()).unwrap());
                    }
                }
                return None;
            }).collect();

            uuids.par_iter().for_each(|uuid| {
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

                    /* Now that we have a UUID, load it from the base path and push it to redis */
                    let mut player = Player::new(uuid.to_owned());
                    if let Err(err) = player.load_dir(basedir.to_str().unwrap()) {
                        eprintln!("Failed to load player {} from dir {}: {}", player, basedir.to_str().unwrap(), err);
                    } else {
                        if let Err(err) = player.save_redis(&args.domain, &mut con) {
                            eprintln!("Failed to save player {} to redis: {}", player, err);
                        } else {
                            if inargs.history_amount_to_keep < u16::MAX {
                                if let Err(err) = player.trim_redis_history(&args.domain, &mut con, inargs.history_amount_to_keep as isize) {
                                    eprintln!("Failed to trim player's redis history {}: {}", player, err);
                                }
                            }

                            println!("{}", player);
                        }
                    }
                });
            });
        }
    }

    Ok(())
}

fn output_player(player: &Player, client: &redis::Client, domain: &str, basedir: &str) -> () {
    THREAD_CONNECTIONS.with(|cell| {
        /*
         * Clone the player, which at this point is just the UUID.
         * This allows this player to be loaded with a bunch of data and then dropped
         * when this iteration completes, eliminating the need to keep all player data
         * in memory all at once
         */
        let mut player = player.clone();

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

        // Use the connection to load a player and save it to the output directory
        let result = player.load_redis(domain, &mut con);
        if let Ok(_) = result {
            if let Err(err) = player.save_dir(basedir) {
                eprintln!("Failed to save player data for {}: {}", player, err);
            }
            println!("{}", player);
        } else if let Err(err) = result {
            eprintln!("Failed to load player data for {}: {}", player, err);
        }
    });
}

#[macro_use] extern crate simple_error;

use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::env;
use std::path::Path;
use simplelog::*;
use rayon::prelude::*;
use uuid::Uuid;
use std::fs;
use std::cell::RefCell;

use monumenta::player::Player;

#[derive(PartialEq)]
enum Mode {
    INPUT,
    OUTPUT
}

fn usage() {
    println!("Usage: redis_playerdata_save_load 'redis://127.0.0.1/' <domain> <--input path/to/directory [history-amount-to-keep] | --output path/to/directory>");
}

fn main() -> BoxResult<()> {
    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() < 5 {
        usage();
        return Ok(());
    }

    args.remove(0); // Program name

    let redis_uri = args.remove(0);

    let domain = args.remove(0);

    let mode = match &args.remove(0)[..] {
        "--input" => Mode::INPUT,
        "--output" => Mode::OUTPUT,
        _ => {
            usage();
            return Ok(());
        }
    };

    // Get the path to the input/output directory
    let basedir = args.remove(0);
    let basedir = Path::new(&basedir);
    if mode == Mode::OUTPUT && basedir.is_dir() {
        bail!("Supplied output directory already exists!");
    } else if mode == Mode::INPUT && !basedir.is_dir() {
        bail!("Supplied input directory does not exist");
    }

    // Default to keeping all history elements
    let mut to_keep : isize = 999999;
    if Mode::INPUT == mode {
        if args.len() > 0 {
            to_keep = args.remove(0).parse::<isize>().unwrap();
        }
        if to_keep < 0 {
            bail!("Number of history elements to keep must be 1 or more");
        }
    }

    let client = redis::Client::open(redis_uri)?;
    let mut con : redis::Connection = client.get_connection()?;

    // Thread-local connection used by the inner loops
    thread_local!(static THREAD_CONNECTIONS: RefCell<Option<redis::Connection>> = RefCell::new(None));

    match mode {
        Mode::OUTPUT => {
            Player::get_redis_players(&domain, &mut con)?.par_iter().for_each(|(_, player)| {
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
                    let result = player.load_redis(&domain, &mut con);
                    if let Ok(_) = result {
                        if let Err(err) = player.save_dir(basedir.to_str().unwrap()) {
                            eprintln!("Failed to save player data for {}: {}", player, err);
                        }
                        println!("{}", player);
                    } else if let Err(err) = result {
                        eprintln!("Failed to load player data for {}: {}", player, err);
                    }
                });
            });
        }
        Mode::INPUT => {
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
                        if let Err(err) = player.save_redis(&domain, &mut con) {
                            eprintln!("Failed to save player {} to redis: {}", player, err);
                        } else {
                            if to_keep < 999999 {
                                if let Err(err) = player.trim_redis_history(&domain, &mut con, to_keep) {
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

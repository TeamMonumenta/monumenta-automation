#[macro_use] extern crate simple_error;

use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::env;
use std::path::Path;
use simplelog::*;
use uuid::Uuid;
use std::fs;

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

    args.remove(0);

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

    match mode {
        Mode::OUTPUT => {
            for (_, player) in Player::get_redis_players(&domain, &mut con)?.iter_mut() {
                let result = player.load_redis(&domain, &mut con);
                if let Ok(_) = result {
                    player.save_dir(basedir.to_str().unwrap())?;
                    println!("{}", player);
                } else if let Err(err) = result {
                    eprintln!("Failed to load player data for {}: {}", player, err);
                }
            }
        }
        Mode::INPUT => {
            /* Need to do more work to figure out what uuids are being loaded */
            for entry in fs::read_dir(Path::new(&basedir).join("playerdata"))? {
                if let Ok(file) = entry {
                    let path = file.path();
                    if path.extension().unwrap() == "dat" {
                        let uuid = Uuid::parse_str(path.file_stem().unwrap().to_str().unwrap()).unwrap();

                        /* Now that we have a UUID, load it from the base path and push it to redis */

                        let mut player = Player::new(uuid);
                        player.load_dir(basedir.to_str().unwrap())?;
                        player.save_redis(&domain, &mut con)?;
                        if to_keep < 999999 {
                            player.trim_redis_history(&domain, &mut con, to_keep)?;
                        }

                        println!("{}", player);
                    }
                }
            }
        }
    }

    Ok(())
}

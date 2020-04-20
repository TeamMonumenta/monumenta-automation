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
    println!("Usage: save_playerdata_to_redis 'redis://127.0.0.1/' <domain> <--input path/to/directory | --output path/to/directory>");
}

fn main() -> BoxResult<()> {
    CombinedLogger::init(
        vec![
            TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed).unwrap(),
        ]
    ).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 5 {
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

    // Get the path to the project_epic directory
    let basedir = args.remove(0);
    let basedir = Path::new(&basedir);
    if mode == Mode::OUTPUT && basedir.is_dir() {
        bail!("Supplied output directory already exists!");
    } else if mode == Mode::INPUT && !basedir.is_dir() {
        bail!("Supplied input directory does not exist");
    }

    let client = redis::Client::open(redis_uri)?;
    let mut con : redis::Connection = client.get_connection()?;

    match mode {
        Mode::OUTPUT => {
            for (_, player) in Player::get_redis_players(&domain, &mut con)?.iter_mut() {
                player.load_redis(&domain, &mut con)?;
                player.save_dir(basedir.to_str().unwrap())?;
                println!("{}", player);
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

                        println!("{}", player);
                    }
                }
            }
        }
    }

    Ok(())
}

#[macro_use] extern crate simple_error;

use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::env;
use std::path::Path;
use simplelog::*;

use monumenta::player::Player;

fn main() -> BoxResult<()> {
    CombinedLogger::init(
        vec![
            TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed).unwrap(),
        ]
    ).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        println!("Usage: save_playerdata_to_redis path/to/directory");
        return Ok(());
    }

    args.remove(0);

    // Get the path to the project_epic directory
    let basedir = args.remove(0);
    let basedir = Path::new(&basedir);
    if basedir.is_dir() {
        bail!("Supplied output directory already exists!");
    }

    let client = redis::Client::open("redis://127.0.0.1/")?;
    let mut con : redis::Connection = client.get_connection()?;

    for (_, player) in Player::get_redis_players("build", &mut con)?.iter_mut() {
        player.load_redis("build", &mut con)?;
        player.save_dir(basedir.to_str().unwrap())?;
        println!("{}", player);
    }

    Ok(())
}

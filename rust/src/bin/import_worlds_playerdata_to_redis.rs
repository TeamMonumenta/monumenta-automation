use monumenta::player::Player;
use monumenta::world::World;

use anyhow::{self, bail};
use log::warn;
use simplelog::*;
use uuid::Uuid;

use std::{
    collections::HashMap,
    env,
    path::Path
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
        println!("Usage: save_playerdata_to_redis path/to/locations.yml path/to/project_epic");
        return Ok(());
    }

    args.remove(0);

    // Get and read locations yaml
    let locations = args.remove(0);
    let locations = std::fs::File::open(locations)?;
    let locations: HashMap<String, String> = serde_yaml::from_reader(locations)?;
    // Convert the string/string map to uuid/string, dropping any keys that are not uuids
    let locations: HashMap<Uuid, &String> = locations.iter().map(|(k, v)| (Uuid::parse_str(k), v)).filter_map(|(k, v)| if let Ok(res) = k {Some((res, v))} else {None}).collect();

    // Get the path to the project_epic directory
    let basedir = args.remove(0);
    let basedir = Path::new(&basedir);
    if !basedir.is_dir() {
        bail!("Supplied project epic path does not point to a directory!");
    }

    let mut worlds: HashMap<String, World> = HashMap::new();
    let mut uuid2name: HashMap<Uuid, String> = HashMap::new();

    let client = redis::Client::open("redis://127.0.0.1/")?;
    let mut con : redis::Connection = client.get_connection()?;

    for (uuid, world_name) in locations {
        if !worlds.contains_key(world_name) {
            let sub_path = format!("{0}/Project_Epic-{0}", world_name);
            let path = basedir.join(sub_path);
            worlds.insert(world_name.to_string(), World::new(path.to_str().unwrap())?);
        }

        if let Some(world) = worlds.get_mut(world_name) {
            println!("{}, {}", uuid, world_name);

            let _ = world.load_scoreboard();

            let mut player = Player::new(uuid);

            if let Err(err) = player.load_world(&world) {
                warn!("Failed to load player {} on {}: {}", uuid, world_name, err);
                continue;
            }

            if let Some(name) = &player.name {
                uuid2name.insert(uuid, name.to_string());
            }

            let domain = "play";
            player.update_history("Player File Import");
            if let Err(err) = player.save_redis(domain, &mut con) {
                warn!("Failed to save player {} domain {} to redis: {}", uuid, domain, err);
                continue;
            }

            //debug!("{:x?}", player.playerdata_bytes);
            //debug!("{}", serde_json::to_string(&player.scores.unwrap()).unwrap());
            //debug!("{}", player.advancements.unwrap().to_string_pretty())
        }
    }

    println!("{:?}", uuid2name);

    Ok(())
}

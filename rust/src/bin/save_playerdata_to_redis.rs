#[macro_use] extern crate simple_error;
#[macro_use] extern crate log;

use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::env;
use std::collections::HashMap;
use std::path::Path;
use uuid::Uuid;
use simplelog::*;

use monumenta::world::World;

fn main() -> BoxResult<()> {
    CombinedLogger::init(
        vec![
            TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed).unwrap(),
        ]
    ).unwrap();

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


    for (uuid, world_name) in locations {
        if !worlds.contains_key(world_name) {
            let sub_path = format!("{0}/Project_Epic-{0}", world_name);
            let path = basedir.join(sub_path);
            worlds.insert(world_name.to_string(), World::new(path.to_str().unwrap())?);
        }

        if let Some(world) = worlds.get_mut(world_name) {
            println!("{}, {}", uuid, world_name);

            if let Ok(data) = world.get_player_data(&uuid) {
                let mut src = std::io::Cursor::new(&data[..]);
                let blob = nbt::Blob::from_gzip_reader(&mut src).unwrap();

                // Grab the player's last known name from the data
                // Need this to get scoreboards
                if let Some(nbt::Value::Compound(bukkit_compound)) = blob.get("bukkit") {
                    if let Some(nbt::Value::String(name)) = bukkit_compound.get("lastKnownName") {
                        uuid2name.insert(uuid, name.to_string());
                    }
                }
                //debug!("{:x?}", data);
            } else {
                warn!("Failed to load player data for {} on {}", uuid, world_name);
            }

            if let Some(scoreboard) = world.get_scoreboard() {
                if let Some(name) = uuid2name.get(&uuid) {
                    //debug!("{}", serde_json::to_string(&scoreboard.get_player_scores(name)).unwrap());
                } else {
                    warn!("Unable to determine player name for {} while trying to load their scores", uuid);
                }
            } else {
                warn!("Failed to load scoreboard for {}", world_name);
            }

            if let Ok(advancements) = world.get_advancements_data(&uuid) {
                if let Ok(serde_json::Value::Object(advancements)) = serde_json::from_str(&advancements) {
                    //debug!("{}", serde_json::to_string(&advancements).unwrap());
                } else {
                    warn!("Failed to parse advancements data for {} on {} as string", uuid, world_name);
                }
            } else {
                warn!("Failed to load advancements data for {} on {}", uuid, world_name);
            }
        }
    }

    println!("{:?}", uuid2name);

    Ok(())
}

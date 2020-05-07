use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::fs;
use std::fmt;
use std::path::Path;
use std::io::{Read};
use std::collections::HashMap;
use std::collections::HashSet;
use std::time::{SystemTime, UNIX_EPOCH};
use uuid::Uuid;
use redis::Commands;
use crate::world::World;
use crate::advancements::Advancements;

pub struct Player {
    pub uuid: Uuid,
    pub name: Option<String>,
    pub playerdata: Option<nbt::Blob>,
    pub advancements: Option<Advancements>,
    pub scores: Option<HashMap<String, i32>>,
    pub sharddata: Option<HashMap<String, String>>,
    pub history: Option<String>,
}

impl fmt::Display for Player {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: name={}, data={}, advancements={}, scores={}, sharddata={}, history={}",
               self.uuid,
               if let Some(name) = &self.name { name } else { "?" },
               if let Some(_) = self.playerdata { "Some" } else { "None" },
               if let Some(_) = self.advancements { "Some" } else { "None" },
               if let Some(_) = self.scores { "Some" } else { "None" },
               if let Some(_) = self.sharddata { "Some" } else { "None" },
               if let Some(history) = &self.history { history } else { "None" })
    }
}

impl fmt::Debug for Player {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: history={}\n  name={},\n  data={},\n  advancements={},\n  scores={},\n  sharddata={}",
               self.uuid,
               if let Some(history) = &self.history { history } else { "None" },
               if let Some(name) = &self.name { name } else { "?" },
               if let Some(data) = &self.playerdata { format!("{:?}", data) } else { "None".to_string() },
               if let Some(advancements) = &self.advancements { advancements.to_string_pretty() } else { "None".to_string() },
               if let Some(scores) = &self.scores { format!("{:?}", scores) } else { "None".to_string() },
               if let Some(sharddata) = &self.sharddata { format!("{:?}", sharddata) } else { "None".to_string() })
    }
}

impl Player {
    pub fn new(uuid: Uuid) -> Player {
        Player{uuid: uuid, name: None, playerdata: None, advancements: None, scores: None, sharddata: None, history: None}
    }

    pub fn get_redis_players(domain: &str, con: &mut redis::Connection) -> BoxResult<HashMap<Uuid, Player>> {
        let mut uuid: HashSet<Uuid> = HashSet::new();

        let keys: Vec<String> = con.keys(format!("{}:playerdata:*", domain))?;
        for key in keys {
            let split: Vec<&str> = key.split(":").collect();
            if split.len() >= 3 {
                uuid.insert(Uuid::parse_str(split[2])?);
            } else {
                warn!("Found unrecognized player data key: {}", key);
            }
        }

        Ok(uuid.iter().map(|uuid| (*uuid, Player::new(*uuid))).collect())
    }

    pub fn load_world(&mut self, world: &World) -> BoxResult<()> {
        self.load_world_player_data(world)?;
        self.load_world_advancements(world)?;
        self.load_world_scores(world)?;
        self.update_history(&world.get_name());
        Ok(())
    }

    pub fn load_world_player_data(&mut self, world: &World) -> BoxResult<()> {
        let mut contents = Vec::new();
        world.get_player_data_file(&self.uuid)?.read_to_end(&mut contents)?;
        self.load_player_data_common(contents)
    }

    pub fn load_world_advancements(&mut self, world: &World) -> BoxResult<()> {
        self.advancements = Some(Advancements::load_from_file(&mut world.get_player_advancements_file(&self.uuid)?)?);
        Ok(())
    }

    pub fn load_world_scores(&mut self, world: &World) -> BoxResult<()> {
        if let Some(name) = &self.name {
            self.scores = Some(world.get_player_scores(name)?);
            Ok(())
        } else {
            bail!("Player name not known - try loading player data first")
        }
    }

    pub fn load_redis(&mut self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        self.load_redis_player_data(domain, con)?;
        self.load_redis_advancements(domain, con)?;
        self.load_redis_scores(domain, con)?;
        self.load_redis_history(domain, con)?;
        self.load_redis_sharddata(domain, con)?;
        Ok(())
    }

    pub fn load_redis_player_data(&mut self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        let data: Vec<u8> = con.lindex(format!("{}:playerdata:{}:data", domain, self.uuid.to_hyphenated().to_string()), 0)?;
        self.load_player_data_common(data)
    }

    pub fn load_redis_advancements(&mut self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        let advancements: String = con.lindex(format!("{}:playerdata:{}:advancements", domain, self.uuid.to_hyphenated().to_string()), 0)?;
        self.advancements = Some(Advancements::load_from_string(&advancements)?);
        Ok(())
    }

    pub fn load_redis_scores(&mut self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        let scores: String = con.lindex(format!("{}:playerdata:{}:scores", domain, self.uuid.to_hyphenated().to_string()), 0)?;
        let scores: HashMap<String, i32> = serde_json::from_str(&scores)?;
        self.scores = Some(scores);
        Ok(())
    }

    pub fn load_redis_sharddata(&mut self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        self.sharddata = match con.hgetall(format!("{}:playerdata:{}:sharddata", domain, self.uuid.to_hyphenated().to_string())) {
            Ok(sharddata) => {
                let sharddata: HashMap<String, String> = sharddata;
                if sharddata.is_empty() {
                    None
                } else {
                    Some(sharddata)
                }
            },
            _ => None
        };
        Ok(())
    }

    pub fn load_redis_history(&mut self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        self.history = Some(con.lindex(format!("{}:playerdata:{}:history", domain, self.uuid.to_hyphenated().to_string()), 0)?);
        Ok(())
    }

    pub fn save_redis(&mut self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        self.save_redis_player_data(domain, con)?;
        self.save_redis_advancements(domain, con)?;
        self.save_redis_scores(domain, con)?;
        self.save_redis_sharddata(domain, con)?;
        self.save_redis_history(domain, con)?;
        Ok(())
    }

    pub fn trim_redis_history(&mut self, domain: &str, con: &mut redis::Connection, count: isize) -> BoxResult<()> {
        con.ltrim(format!("{}:playerdata:{}:history", domain, self.uuid.to_hyphenated().to_string()), 0, count - 1)?;
        con.ltrim(format!("{}:playerdata:{}:scores", domain, self.uuid.to_hyphenated().to_string()), 0, count - 1)?;
        con.ltrim(format!("{}:playerdata:{}:advancements", domain, self.uuid.to_hyphenated().to_string()), 0, count - 1)?;
        con.ltrim(format!("{}:playerdata:{}:data", domain, self.uuid.to_hyphenated().to_string()), 0, count - 1)?;
        Ok(())
    }

    pub fn save_dir(&self, basepath: &str) -> BoxResult<()> {
        let basepath = Path::new(basepath);
        let uuidstr = self.uuid.to_hyphenated().to_string();

        self.save_file_player_data(basepath.join(format!("playerdata/{}.dat", uuidstr)).to_str().unwrap())?;
        self.save_file_advancements(basepath.join(format!("advancements/{}.json", uuidstr)).to_str().unwrap())?;
        self.save_file_scores(basepath.join(format!("scores/{}.json", uuidstr)).to_str().unwrap())?;
        self.save_file_sharddata(basepath.join(format!("sharddata/{}.json", uuidstr)).to_str().unwrap())?;
        self.save_file_history(basepath.join(format!("history/{}.txt", uuidstr)).to_str().unwrap())?;
        Ok(())
    }

    pub fn save_file_player_data(&self, filepath: &str) -> BoxResult<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(playerdata) = &self.playerdata {
            let mut contents : Vec<u8> = Vec::new();
            playerdata.to_gzip_writer(&mut contents)?;
            fs::write(filepath, contents)?;
        }
        Ok(())
    }

    pub fn save_file_advancements(&self, filepath: &str) -> BoxResult<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(advancements) = &self.advancements {
            fs::write(filepath, advancements.to_string_pretty())?;
        }
        Ok(())
    }

    pub fn save_file_scores(&self, filepath: &str) -> BoxResult<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(scores) = &self.scores {
            let scores: String = serde_json::to_string_pretty(scores)?;
            fs::write(filepath, scores)?;
        }
        Ok(())
    }

    pub fn save_file_sharddata(&self, filepath: &str) -> BoxResult<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(sharddata) = &self.sharddata {
            let sharddata: String = serde_json::to_string_pretty(sharddata)?;
            fs::write(filepath, sharddata)?;
        }
        Ok(())
    }

    pub fn save_file_history(&self, filepath: &str) -> BoxResult<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(history) = &self.history {
            fs::write(filepath, history)?;
        }
        Ok(())
    }


    pub fn load_dir(&mut self, basepath: &str) -> BoxResult<()> {
        let basepath = Path::new(basepath);
        let uuidstr = self.uuid.to_hyphenated().to_string();

        self.load_file_player_data(&basepath.join(format!("playerdata/{}.dat", uuidstr)))?;
        self.load_file_advancements(&basepath.join(format!("advancements/{}.json", uuidstr)))?;
        self.load_file_scores(&basepath.join(format!("scores/{}.json", uuidstr)))?;
        self.load_file_sharddata(&basepath.join(format!("sharddata/{}.json", uuidstr)))?;
        self.load_file_history(&basepath.join(format!("history/{}.txt", uuidstr)))?;
        Ok(())
    }

    pub fn update_history(&mut self, description: &str) {
        self.history = Some(format!("{}|{}|{}", description, SystemTime::now().duration_since(UNIX_EPOCH).expect("Time went backwards").as_millis(), (&self.name).as_ref().unwrap_or(&"Unknown".to_string())));
    }

    /********************* Private Functions *********************/

    fn save_redis_player_data(&self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        if let Some(playerdata) = &self.playerdata {
            let mut contents : Vec<u8> = Vec::new();
            playerdata.to_gzip_writer(&mut contents)?;
            let _: () = con.lpush(format!("{}:playerdata:{}:data", domain, self.uuid.to_hyphenated().to_string()), contents)?;
        }
        Ok(())
    }

    fn save_redis_advancements(&self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        if let Some(advancements) = &self.advancements {
            con.lpush(format!("{}:playerdata:{}:advancements", domain, self.uuid.to_hyphenated().to_string()), advancements.to_string())?;
        }
        Ok(())
    }

    fn save_redis_scores(&self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        if let Some(scores) = &self.scores {
            let scores: String = serde_json::to_string(scores)?;
            con.lpush(format!("{}:playerdata:{}:scores", domain, self.uuid.to_hyphenated().to_string()), scores)?;
        }
        Ok(())
    }

    fn save_redis_sharddata(&self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        if let Some(sharddata) = &self.sharddata {
            let redis_path = format!("{}:playerdata:{}:sharddata", domain, self.uuid.to_hyphenated().to_string());
            con.del(&redis_path)?;
            for (key, val) in sharddata.iter() {
                let _: () = con.hset(&redis_path, key, val)?;
            }
        }
        Ok(())
    }

    fn save_redis_history(&self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        if let Some(history) = &self.history {
            con.lpush(format!("{}:playerdata:{}:history", domain, self.uuid.to_hyphenated().to_string()), history)?;
        }
        Ok(())
    }

    fn load_file_player_data(&mut self, path: &Path) -> BoxResult<()> {
        let mut contents = Vec::new();
        World::get_file_common(path)?.read_to_end(&mut contents)?;
        self.load_player_data_common(contents)
    }

    fn load_file_advancements(&mut self, path: &Path) -> BoxResult<()> {
        self.advancements = Some(Advancements::load_from_file(&mut World::get_file_common(path)?)?);
        Ok(())
    }

    fn load_file_scores(&mut self, path: &Path) -> BoxResult<()> {
        let contents = fs::read_to_string(path)?;
        let scores: HashMap<String, i32> = serde_json::from_str(&contents)?;
        self.scores = Some(scores);
        Ok(())
    }

    fn load_file_sharddata(&mut self, path: &Path) -> BoxResult<()> {
        self.sharddata = match fs::read_to_string(path) {
            Ok(contents) => Some(serde_json::from_str(&contents)?),
            _ => None
        };
        Ok(())
    }

    fn load_file_history(&mut self, path: &Path) -> BoxResult<()> {
        let contents = fs::read_to_string(path)?;
        self.history = Some(contents);
        Ok(())
    }

    fn load_player_data_common(&mut self, contents: Vec<u8>) -> BoxResult<()> {
        let mut src = std::io::Cursor::new(&contents[..]);
        let blob = nbt::Blob::from_gzip_reader(&mut src)?;

        // Grab the player's last known name from the data
        if let Some(nbt::Value::Compound(bukkit_compound)) = blob.get("bukkit") {
            if let Some(nbt::Value::String(name)) = bukkit_compound.get("lastKnownName") {
                self.name = Some(name.to_string());
            }
        }

        self.playerdata = Some(blob);
        Ok(())
    }
}

use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::fs;
use std::fmt;
use std::path::Path;
use std::io::{Read};
use std::collections::HashMap;
use std::collections::HashSet;
use std::hash::{Hash, Hasher};
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
}

impl PartialEq for Player {
    fn eq(&self, other: &Self) -> bool {
        self.uuid == other.uuid
    }
}
impl Eq for Player {}
impl Hash for Player {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.uuid.hash(state);
    }
}

impl fmt::Display for Player {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: name={}, data={}, advancements={}, scores={}",
               self.uuid,
               if let Some(name) = &self.name { name } else { "?" },
               if let Some(_) = self.playerdata { "Some" } else { "None" },
               if let Some(_) = self.advancements { "Some" } else { "None" },
               if let Some(_) = self.scores { "Some" } else { "None" })
    }
}

impl fmt::Debug for Player {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}:\n  name={},\n  data={},\n  advancements={},\n  scores={}",
               self.uuid,
               if let Some(name) = &self.name { name } else { "?" },
               if let Some(data) = &self.playerdata { format!("{:?}", data) } else { "None".to_string() },
               if let Some(advancements) = &self.advancements { advancements.to_string_pretty() } else { "None".to_string() },
               if let Some(scores) = &self.scores { format!("{:?}", scores) } else { "None".to_string() })
    }
}

impl Player {
    pub fn new(uuid: Uuid) -> Player {
        Player{uuid: uuid, name: None, playerdata: None, advancements: None, scores: None}
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

    pub fn save_redis(&self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        self.save_redis_player_data(domain, con)?;
        self.save_redis_advancements(domain, con)?;
        self.save_redis_scores(domain, con)?;
        Ok(())
    }

    pub fn save_redis_player_data(&self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        if let Some(playerdata) = &self.playerdata {
            let mut contents : Vec<u8> = Vec::new();
            playerdata.to_gzip_writer(&mut contents)?;
            let _: () = con.lpush(format!("{}:playerdata:{}:data", domain, self.uuid.to_hyphenated().to_string()), contents)?;
        }
        Ok(())
    }

    pub fn save_redis_advancements(&self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        if let Some(advancements) = &self.advancements {
            con.lpush(format!("{}:playerdata:{}:advancements", domain, self.uuid.to_hyphenated().to_string()), advancements.to_string())?;
        }
        Ok(())
    }

    pub fn save_redis_scores(&self, domain: &str, con: &mut redis::Connection) -> BoxResult<()> {
        if let Some(scores) = &self.scores {
            let scores: String = serde_json::to_string(scores)?;
            con.lpush(format!("{}:playerdata:{}:scores", domain, self.uuid.to_hyphenated().to_string()), scores)?;
        }
        Ok(())
    }

    pub fn save_dir(&self, basepath: &str) -> BoxResult<()> {
        let basepath = Path::new(basepath);
        let uuidstr = self.uuid.to_hyphenated().to_string();

        self.save_file_player_data(basepath.join(format!("playerdata/{}.dat", uuidstr)).to_str().unwrap())?;
        self.save_file_advancements(basepath.join(format!("advancements/{}.json", uuidstr)).to_str().unwrap())?;
        self.save_file_scores(basepath.join(format!("scores/{}.json", uuidstr)).to_str().unwrap())?;
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

    /********************* Private Functions *********************/

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

use crate::advancements::Advancements;
use crate::world::World;

use anyhow::{self, bail};
use log::warn;
use redis::Commands;
use uuid::Uuid;

use std::{
    collections::{HashMap, HashSet},
    fmt,
    fs,
    io::Read,
    path::Path,
    time::{SystemTime, UNIX_EPOCH}
};

#[derive(Clone)]
pub struct Player {
    pub uuid: Uuid,
    pub name: Option<String>,
    pub playerdata: Option<nbt::Blob>,
    pub advancements: Option<Advancements>,
    pub scores: Option<HashMap<String, i32>>,
    pub plugindata: Option<HashMap<String, serde_json::Value>>,
    pub sharddata: Option<HashMap<String, String>>,
    pub remotedata: Option<HashMap<String, String>>,
    pub history: Option<String>,
}

impl fmt::Display for Player {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: name={}, data={}, advancements={}, scores={}, plugindata={}, sharddata={}, remotedata={}, history={}",
               self.uuid,
               if let Some(name) = &self.name { name } else { "?" },
               if let Some(_) = self.playerdata { "Some" } else { "None" },
               if let Some(_) = self.advancements { "Some" } else { "None" },
               if let Some(_) = self.scores { "Some" } else { "None" },
               if let Some(_) = self.plugindata { "Some" } else { "None" },
               if let Some(_) = self.sharddata { "Some" } else { "None" },
               if let Some(_) = self.remotedata { "Some" } else { "None" },
               if let Some(history) = &self.history { history } else { "None" })
    }
}

impl fmt::Debug for Player {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: history={}\n  name={},\n  data={},\n  advancements={},\n  scores={},\n  plugindata={},\n  sharddata={},\n  remotedata={}",
               self.uuid,
               if let Some(history) = &self.history { history } else { "None" },
               if let Some(name) = &self.name { name } else { "?" },
               if let Some(data) = &self.playerdata { format!("{:?}", data) } else { "None".to_string() },
               if let Some(advancements) = &self.advancements { advancements.to_string_pretty() } else { "None".to_string() },
               if let Some(scores) = &self.scores { format!("{:?}", scores) } else { "None".to_string() },
               if let Some(plugindata) = &self.plugindata { format!("{:?}", plugindata) } else { "None".to_string() },
               if let Some(sharddata) = &self.sharddata { format!("{:?}", sharddata) } else { "None".to_string() },
               if let Some(remotedata) = &self.remotedata { format!("{:?}", remotedata) } else { "None".to_string() })
    }
}

impl Player {
    pub fn new(uuid: Uuid) -> Player {
        Player{uuid, name: None, playerdata: None, advancements: None, scores: None, plugindata: None, sharddata: None, remotedata: None, history: None}
    }

    pub fn from_name(name: &str, con: &mut redis::Connection) -> anyhow::Result<Player> {
        let player_uuid_str: String = con.hget("name2uuid", name)?;
        let uuid = Uuid::parse_str(&player_uuid_str)?;

        Ok(Player{uuid, name: None, playerdata: None, advancements: None, scores: None, plugindata: None, sharddata: None, remotedata: None, history: None})
    }

    pub fn get_redis_players(domain: &str, con: &mut redis::Connection) -> anyhow::Result<HashMap<Uuid, Player>> {
        let mut uuid: HashSet<Uuid> = HashSet::new();

        let keys: Vec<String> = con.keys(format!("{}:playerdata:*:data", domain))?;
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

    pub fn load_world(&mut self, world: &World) -> anyhow::Result<()> {
        self.load_world_player_data(world)?;
        self.load_world_advancements(world)?;
        self.load_world_scores(world)?;
        self.plugindata = Some(HashMap::new());
        self.update_history(&world.get_name());
        Ok(())
    }

    pub fn load_world_player_data(&mut self, world: &World) -> anyhow::Result<()> {
        let mut contents = Vec::new();
        world.get_player_data_file(&self.uuid)?.read_to_end(&mut contents)?;
        self.load_player_data_common(contents)
    }

    pub fn load_world_advancements(&mut self, world: &World) -> anyhow::Result<()> {
        self.advancements = Some(Advancements::load_from_file(&mut world.get_player_advancements_file(&self.uuid)?)?);
        Ok(())
    }

    pub fn load_world_scores(&mut self, world: &World) -> anyhow::Result<()> {
        if let Some(name) = &self.name {
            self.scores = Some(world.get_player_scores(name)?);
            Ok(())
        } else {
            bail!("Player name not known - try loading player data first")
        }
    }

    pub fn load_redis(&mut self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        if let Err(err) = self.load_redis_player_data(domain, con) {
            bail!("Failed to load player data for {}: {}", self.uuid.hyphenated(), err);
        }
        if let Err(err) = self.load_redis_advancements(domain, con) {
            bail!("Failed to load advancements for {}: {}", self.uuid.hyphenated(), err);
        }
        if let Err(err) = self.load_redis_scores(domain, con) {
            bail!("Failed to load scores for {}: {}", self.uuid.hyphenated(), err);
        }
        if let Err(err) = self.load_redis_plugindata(domain, con) {
            bail!("Failed to load plugindata for {}: {}", self.uuid.hyphenated(), err);
        }
        if let Err(err) = self.load_redis_history(domain, con) {
            bail!("Failed to load history for {}: {}", self.uuid.hyphenated(), err);
        }
        if let Err(err) = self.load_redis_sharddata(domain, con) {
            bail!("Failed to load sharddata for {}: {}", self.uuid.hyphenated(), err);
        }
        if let Err(err) = self.load_redis_remotedata(domain, con) {
            bail!("Failed to load remotedata for {}: {}", self.uuid.hyphenated(), err);
        }
        Ok(())
    }

    pub fn load_redis_player_data(&mut self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        let data: Vec<u8> = con.lindex(format!("{}:playerdata:{}:data", domain, self.uuid.hyphenated().to_string()), 0)?;
        self.load_player_data_common(data)
    }

    pub fn load_redis_advancements(&mut self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        let advancements: String = con.lindex(format!("{}:playerdata:{}:advancements", domain, self.uuid.hyphenated().to_string()), 0)?;
        self.advancements = Some(Advancements::load_from_string(&advancements)?);
        Ok(())
    }

    pub fn load_redis_scores(&mut self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        let scores: String = con.lindex(format!("{}:playerdata:{}:scores", domain, self.uuid.hyphenated().to_string()), 0)?;
        let scores: HashMap<String, i32> = serde_json::from_str(&scores)?;
        self.scores = Some(scores);
        Ok(())
    }

    pub fn load_redis_plugindata(&mut self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        let plugindata: String = con.lindex(format!("{}:playerdata:{}:plugins", domain, self.uuid.hyphenated().to_string()), 0)?;
        let result = serde_json::from_str(&plugindata);
        if let Err(err) = result {
            bail!("Failed to parse json data: {}\nData: {}", err, plugindata);
        } else if let Ok(result) = result {
            let plugindata: HashMap<String, serde_json::Value> = result;
            self.plugindata = Some(plugindata);
        }
        Ok(())
    }

    pub fn load_redis_sharddata(&mut self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        self.sharddata = match con.hgetall(format!("{}:playerdata:{}:sharddata", domain, self.uuid.hyphenated().to_string())) {
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

    pub fn load_redis_remotedata(&mut self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        self.remotedata = match con.hgetall(format!("{}:playerdata:{}:remotedata", domain, self.uuid.hyphenated().to_string())) {
            Ok(remotedata) => {
                let remotedata: HashMap<String, String> = remotedata;
                if remotedata.is_empty() {
                    None
                } else {
                    Some(remotedata)
                }
            },
            _ => None
        };
        Ok(())
    }

    pub fn load_redis_history(&mut self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        self.history = Some(con.lindex(format!("{}:playerdata:{}:history", domain, self.uuid.hyphenated().to_string()), 0)?);
        Ok(())
    }

    pub fn save_redis(&self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        self.save_redis_player_data(domain, con)?;
        self.save_redis_advancements(domain, con)?;
        self.save_redis_scores(domain, con)?;
        self.save_redis_plugindata(domain, con)?;
        self.save_redis_sharddata(domain, con)?;
        self.save_redis_remotedata(domain, con)?;
        self.save_redis_history(domain, con)?;
        Ok(())
    }

    pub fn trim_redis_history(&mut self, domain: &str, con: &mut redis::Connection, count: isize) -> anyhow::Result<()> {
        con.ltrim(format!("{}:playerdata:{}:history", domain, self.uuid.hyphenated().to_string()), 0, count - 1)?;
        con.ltrim(format!("{}:playerdata:{}:scores", domain, self.uuid.hyphenated().to_string()), 0, count - 1)?;
        con.ltrim(format!("{}:playerdata:{}:plugins", domain, self.uuid.hyphenated().to_string()), 0, count - 1)?;
        con.ltrim(format!("{}:playerdata:{}:advancements", domain, self.uuid.hyphenated().to_string()), 0, count - 1)?;
        con.ltrim(format!("{}:playerdata:{}:data", domain, self.uuid.hyphenated().to_string()), 0, count - 1)?;
        Ok(())
    }

    pub fn del(&mut self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        con.del(format!("{}:playerdata:{}:history", domain, self.uuid.hyphenated().to_string()))?;
        con.del(format!("{}:playerdata:{}:scores", domain, self.uuid.hyphenated().to_string()))?;
        con.del(format!("{}:playerdata:{}:plugins", domain, self.uuid.hyphenated().to_string()))?;
        con.del(format!("{}:playerdata:{}:advancements", domain, self.uuid.hyphenated().to_string()))?;
        con.del(format!("{}:playerdata:{}:data", domain, self.uuid.hyphenated().to_string()))?;
        con.del(format!("{}:playerdata:{}:sharddata", domain, self.uuid.hyphenated().to_string()))?;
        con.del(format!("{}:playerdata:{}:remotedata", domain, self.uuid.hyphenated().to_string()))?;
        Ok(())
    }

    pub fn save_dir(&self, basepath: &str) -> anyhow::Result<()> {
        let basepath = Path::new(basepath);
        let uuidstr = self.uuid.hyphenated().to_string();

        self.save_file_player_data(basepath.join(format!("playerdata/{}.dat", uuidstr)).to_str().unwrap())?;
        self.save_file_advancements(basepath.join(format!("advancements/{}.json", uuidstr)).to_str().unwrap())?;
        self.save_file_scores(basepath.join(format!("scores/{}.json", uuidstr)).to_str().unwrap())?;
        self.save_file_plugindata(basepath.join(format!("plugindata/{}.json", uuidstr)).to_str().unwrap())?;
        self.save_file_sharddata(basepath.join(format!("sharddata/{}.json", uuidstr)).to_str().unwrap())?;
        self.save_file_remotedata(basepath.join(format!("remotedata/{}.json", uuidstr)).to_str().unwrap())?;
        self.save_file_history(basepath.join(format!("history/{}.txt", uuidstr)).to_str().unwrap())?;
        Ok(())
    }

    pub fn save_file_player_data(&self, filepath: &str) -> anyhow::Result<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(playerdata) = &self.playerdata {
            let mut contents : Vec<u8> = Vec::new();
            playerdata.to_gzip_writer(&mut contents)?;
            fs::write(filepath, contents)?;
        }
        Ok(())
    }

    pub fn save_file_advancements(&self, filepath: &str) -> anyhow::Result<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(advancements) = &self.advancements {
            fs::write(filepath, advancements.to_string())?;
        }
        Ok(())
    }

    pub fn save_file_scores(&self, filepath: &str) -> anyhow::Result<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(scores) = &self.scores {
            let scores: String = serde_json::to_string(scores)?;
            fs::write(filepath, scores)?;
        }
        Ok(())
    }

    pub fn save_file_plugindata(&self, filepath: &str) -> anyhow::Result<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(plugindata) = &self.plugindata {
            let plugindata: String = serde_json::to_string(plugindata)?;
            fs::write(filepath, plugindata)?;
        }
        Ok(())
    }

    pub fn save_file_sharddata(&self, filepath: &str) -> anyhow::Result<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(sharddata) = &self.sharddata {
            let sharddata: String = serde_json::to_string(sharddata)?;
            fs::write(filepath, sharddata)?;
        }
        Ok(())
    }

    pub fn save_file_remotedata(&self, filepath: &str) -> anyhow::Result<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(remotedata) = &self.remotedata {
            let remotedata: String = serde_json::to_string(remotedata)?;
            fs::write(filepath, remotedata)?;
        }
        Ok(())
    }

    pub fn save_file_history(&self, filepath: &str) -> anyhow::Result<()> {
        let path = Path::new(filepath);
        fs::create_dir_all(path.parent().unwrap().to_str().unwrap())?;

        if let Some(history) = &self.history {
            fs::write(filepath, history)?;
        }
        Ok(())
    }


    pub fn load_dir(&mut self, basepath: &str) -> anyhow::Result<()> {
        let basepath = Path::new(basepath);
        let uuidstr = self.uuid.hyphenated().to_string();

        self.load_file_player_data(&basepath.join(format!("playerdata/{}.dat", uuidstr)))?;
        self.load_file_advancements(&basepath.join(format!("advancements/{}.json", uuidstr)))?;
        self.load_file_scores(&basepath.join(format!("scores/{}.json", uuidstr)))?;
        self.load_file_plugindata(&basepath.join(format!("plugindata/{}.json", uuidstr)))?;
        self.load_file_sharddata(&basepath.join(format!("sharddata/{}.json", uuidstr)))?;
        self.load_file_remotedata(&basepath.join(format!("remotedata/{}.json", uuidstr)))?;
        self.load_file_history(&basepath.join(format!("history/{}.txt", uuidstr)))?;
        Ok(())
    }

    pub fn update_history(&mut self, description: &str) {
        self.history = Some(format!("{}|{}|{}", description, SystemTime::now().duration_since(UNIX_EPOCH).expect("Time went backwards").as_millis(), (&self.name).as_ref().unwrap_or(&"Unknown".to_string())));
    }

    /********************* Private Functions *********************/

    fn save_redis_player_data(&self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        if let Some(playerdata) = &self.playerdata {
            let mut contents : Vec<u8> = Vec::new();
            playerdata.to_gzip_writer(&mut contents)?;
            let _: () = con.lpush(format!("{}:playerdata:{}:data", domain, self.uuid.hyphenated().to_string()), contents)?;
        }
        Ok(())
    }

    fn save_redis_advancements(&self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        if let Some(advancements) = &self.advancements {
            con.lpush(format!("{}:playerdata:{}:advancements", domain, self.uuid.hyphenated().to_string()), advancements.to_string())?;
        }
        Ok(())
    }

    fn save_redis_scores(&self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        if let Some(scores) = &self.scores {
            let scores: String = serde_json::to_string(scores)?;
            con.lpush(format!("{}:playerdata:{}:scores", domain, self.uuid.hyphenated().to_string()), scores)?;
        }
        Ok(())
    }

    /* This one needs to be public at least for now to migrate data */
    pub fn save_redis_plugindata(&self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        if let Some(plugindata) = &self.plugindata {
            let plugindata: String = serde_json::to_string(plugindata)?;
            con.lpush(format!("{}:playerdata:{}:plugins", domain, self.uuid.hyphenated().to_string()), plugindata)?;
        }
        Ok(())
    }

    fn save_redis_sharddata(&self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        if let Some(sharddata) = &self.sharddata {
            let redis_path = format!("{}:playerdata:{}:sharddata", domain, self.uuid.hyphenated().to_string());
            con.del(&redis_path)?;
            for (key, val) in sharddata.iter() {
                let _: () = con.hset(&redis_path, key, val)?;
            }
        }
        Ok(())
    }

    fn save_redis_remotedata(&self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        if let Some(remotedata) = &self.remotedata {
            let redis_path = format!("{}:playerdata:{}:remotedata", domain, self.uuid.hyphenated().to_string());
            con.del(&redis_path)?;
            for (key, val) in remotedata.iter() {
                let _: () = con.hset(&redis_path, key, val)?;
            }
        }
        Ok(())
    }

    fn save_redis_history(&self, domain: &str, con: &mut redis::Connection) -> anyhow::Result<()> {
        if let Some(history) = &self.history {
            con.lpush(format!("{}:playerdata:{}:history", domain, self.uuid.hyphenated().to_string()), history)?;
        }
        Ok(())
    }

    fn load_file_player_data(&mut self, path: &Path) -> anyhow::Result<()> {
        let mut contents = Vec::new();
        World::get_file_common(path)?.read_to_end(&mut contents)?;
        self.load_player_data_common(contents)
    }

    fn load_file_advancements(&mut self, path: &Path) -> anyhow::Result<()> {
        self.advancements = Some(Advancements::load_from_file(&mut World::get_file_common(path)?)?);
        Ok(())
    }

    fn load_file_scores(&mut self, path: &Path) -> anyhow::Result<()> {
        let contents = fs::read_to_string(path)?;
        let scores: HashMap<String, i32> = serde_json::from_str(&contents)?;
        self.scores = Some(scores);
        Ok(())
    }

    fn load_file_plugindata(&mut self, path: &Path) -> anyhow::Result<()> {
        let contents = fs::read_to_string(path)?;
        let plugindata: HashMap<String, serde_json::Value> = serde_json::from_str(&contents)?;
        self.plugindata = Some(plugindata);
        Ok(())
    }

    fn load_file_sharddata(&mut self, path: &Path) -> anyhow::Result<()> {
        self.sharddata = match fs::read_to_string(path) {
            Ok(contents) => Some(serde_json::from_str(&contents)?),
            _ => None
        };
        Ok(())
    }

    fn load_file_remotedata(&mut self, path: &Path) -> anyhow::Result<()> {
        self.remotedata = match fs::read_to_string(path) {
            Ok(contents) => Some(serde_json::from_str(&contents)?),
            _ => None
        };
        Ok(())
    }

    fn load_file_history(&mut self, path: &Path) -> anyhow::Result<()> {
        let contents = fs::read_to_string(path)?;
        self.history = Some(contents);
        Ok(())
    }

    fn load_player_data_common(&mut self, contents: Vec<u8>) -> anyhow::Result<()> {
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

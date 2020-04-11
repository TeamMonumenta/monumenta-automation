use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::io::{Read};
use std::collections::HashMap;
use uuid::Uuid;
use crate::world::World;
use crate::advancements::Advancements;

pub struct Player {
    pub uuid: Uuid,
    pub name: Option<String>,
    pub playerdata_bytes: Option<Vec<u8>>,
    pub playerdata: Option<nbt::Blob>,
    pub playerdata_modified: bool,
    pub advancements: Option<Advancements>,
    pub scores: Option<HashMap<String, i32>>,
}

impl Player {
    pub fn new(uuid: Uuid) -> Player {
        Player{uuid: uuid, name: None, playerdata_bytes: None, playerdata: None, playerdata_modified: false, advancements: None, scores: None}
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

        let mut src = std::io::Cursor::new(&contents[..]);
        let blob = nbt::Blob::from_gzip_reader(&mut src)?;

        // Grab the player's last known name from the data
        if let Some(nbt::Value::Compound(bukkit_compound)) = blob.get("bukkit") {
            if let Some(nbt::Value::String(name)) = bukkit_compound.get("lastKnownName") {
                self.name = Some(name.to_string());
            }
        }

        self.playerdata_bytes = Some(contents);
        self.playerdata = Some(blob);
        self.playerdata_modified = false;
        Ok(())
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
}

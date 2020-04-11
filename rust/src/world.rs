use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::path::Path;
use std::fs::File;
use std::io::{Read};
use uuid::Uuid;

use crate::scoreboard::Scoreboard;

pub struct World {
    basepath: String,
    scoreboard: Option<Scoreboard>,
}

impl World {
    pub fn new(basepath: &str) -> BoxResult<World> {
        Ok(World{basepath: basepath.to_string(), scoreboard: None})
    }

    pub fn get_scoreboard(&mut self) -> &Option<Scoreboard> {
        // If the scoreboard is already loaded, return it. Otherwise load it and hang onto it
        if let Some(_) = &self.scoreboard {
            &self.scoreboard
        } else {
            if let Ok(scoreboard) = Scoreboard::load(Path::new(&self.basepath).join("data/scoreboard.dat").to_str().unwrap()) {
                self.scoreboard = Some(scoreboard);
                &self.scoreboard
            } else {
                &None
            }
        }
    }

    pub fn get_player_data(&self, uuid: &Uuid) -> BoxResult<Vec<u8>> {
        let path = Path::new(&self.basepath).join(format!("playerdata/{}.dat", uuid.to_hyphenated().to_string()));
        if !path.is_file() {
            bail!("Player data file does not exist!");
        }

        let mut file = File::open(path.to_str().unwrap())?;
        let mut contents = Vec::new();
        file.read_to_end(&mut contents)?;

        Ok(contents)
    }

    pub fn get_advancements_data(&self, uuid: &Uuid) -> BoxResult<String> {
        let path = Path::new(&self.basepath).join(format!("advancements/{}.json", uuid.to_hyphenated().to_string()));
        if !path.is_file() {
            bail!("Player advancements file does not exist!");
        }

        let mut file = File::open(path.to_str().unwrap())?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;

        Ok(contents)
    }
}


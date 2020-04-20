use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::path::Path;
use std::fs::File;
use std::collections::HashMap;
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

    pub fn load_scoreboard(&mut self) -> BoxResult<()> {
        // Load scoreboard only if not already loaded
        if let Some(_) = self.scoreboard {
            return Ok(());
        }

        let path = Path::new(&self.basepath).join("data/scoreboard.dat");
        let strpath = path.to_str().unwrap();
        if let Ok(scoreboard) = Scoreboard::load(strpath) {
            self.scoreboard = Some(scoreboard);
            Ok(())
        } else {
            bail!("Could not load scoreboard {}", strpath)
        }
    }

    pub fn get_scoreboard(&self) -> BoxResult<&Scoreboard> {
        if let Some(scoreboard) = &self.scoreboard {
            Ok(scoreboard)
        } else {
            bail!("Scoreboard not loaded");
        }
    }

    pub fn get_name(&self) -> String {
        Path::new(&self.basepath).file_name().unwrap().to_str().unwrap().to_string()
    }

    pub fn get_player_scores(&self, player_name: &str) -> BoxResult<HashMap<String, i32>> {
        Ok(self.get_scoreboard()?.get_player_scores(player_name))
    }

    pub fn get_player_data_file(&self, uuid: &Uuid) -> BoxResult<File> {
        World::get_file_common(&Path::new(&self.basepath).join(format!("playerdata/{}.dat", uuid.to_hyphenated().to_string())))
    }

    pub fn get_player_advancements_file(&self, uuid: &Uuid) -> BoxResult<File> {
        World::get_file_common(&Path::new(&self.basepath).join(format!("advancements/{}.json", uuid.to_hyphenated().to_string())))
    }

    pub fn get_player_stats_file(&self, uuid: &Uuid) -> BoxResult<File> {
        World::get_file_common(&Path::new(&self.basepath).join(format!("stats/{}.json", uuid.to_hyphenated().to_string())))
    }

    pub fn get_file_common(path: &Path) -> BoxResult<File> {
        let strpath = path.to_str().unwrap();
        if !path.is_file() {
            bail!("path {} does not exist or is not a file", strpath);
        }
        match File::open(strpath.to_string()) {
            Ok(file) => Ok(file),
            Err(err) => bail!("Failed to open file {}: {}", strpath, err),
        }
    }
}

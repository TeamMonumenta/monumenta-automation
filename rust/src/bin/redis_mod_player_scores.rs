use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use std::env;
use simplelog::*;
use redis::Commands;
use uuid::Uuid;

use monumenta::player::Player;

macro_rules! map(
    { $($key:expr => $value:expr),+ } => {
        {
            let mut m = ::std::collections::HashMap::new();
            $(
                m.insert($key, $value);
            )+
            m
        }
     };
);

fn main() -> BoxResult<()> {
    let changes = map!(
        "DataCrusader" => 28,
        "creeper_joh" => 22,
        "zdtsd" => 21,
        "Wembler" => 19,
        "VolatileAnomaly" => 19,
        "BoganC" => 17,
        "Anson6311" => 11,
        "Tatsu43" => 10,
        "whyprophecy" => 10,
        "sjasogun" => 10,
        "jjking80" => 10,
        "Derailious" => 9,
        "TKTOM7" => 9,
        "Kingofcows76" => 8,
        "cartsinabag" => 8,
        "TheCrusader57" => 8,
        "quackqwack_" => 7,
        "xnx_" => 6,
        "helphelp11" => 5,
        "__Kiro__" => 5,
        "Sky_Watcher" => 4,
        "Skepter" => 4,
        "emeraldcore71" => 4,
        "Xeronsis" => 3,
        "WxAaRoNxW" => 3,
        "Stealthy69er" => 3,
        "Pakstf" => 3,
        "rayman520" => 3,
        "NobodyPi" => 3,
        "jordenko" => 3,
        "forte_927" => 3,
        "chuwenhsuan" => 3,
        "SupperMariosGr" => 3,
        "Spy21DD" => 2,
        "SikaBg" => 2,
        "Legro8" => 2,
        "gizmo90704" => 2,
        "Compsogbrickus" => 2,
        "BeastMasterFTW" => 2,
        "cyndal_" => 2,
        "ISA_x_JAKE" => 2,
        "moonberserker" => 2,
        "Zouba64" => 1,
        "virtul" => 1,
        "Tryke_O" => 1,
        "TheMonarchAwaken" => 1,
        "spearmkw" => 1,
        "SphorUs" => 1,
        "RockNRed" => 1,
        "Raisin5488" => 1,
        "QooQooMagic" => 1,
        "prets" => 1,
        "NightMessenger" => 1,
        "Mehaz" => 1,
        "LordGeek101" => 1,
        "deceasedapple" => 1,
        "Casiel368" => 1,
        "ooAddman" => 1,
        "GluonCraft" => 1,
        "SorcererAxis81" => 1,
        "LeMicro" => 1,
        "collectics" => 1,
        "popoffREV" => 1,
        "Combustible" => 10
    );

    let mut multiple = vec![];
    match TermLogger::new(LevelFilter::Debug, Config::default(), TerminalMode::Mixed) {
        Some(logger) => multiple.push(logger as Box<dyn SharedLogger>),
        None => multiple.push(SimpleLogger::new(LevelFilter::Debug, Config::default())),
    }
    CombinedLogger::init(multiple).unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 3 {
        println!("Usage: redis_reset_scores <domain> <objective>");
        return Ok(());
    }

    args.remove(0);

    let domain = args.remove(0);
    let objective = args.remove(0);

    let client = redis::Client::open("redis://127.0.0.1/")?;
    let mut con : redis::Connection = client.get_connection()?;

    for (playername, add_val) in changes {
        println!("Loading {}", playername);
        let uuid_str: String = con.hget("name2uuid", playername.to_string())?;
        let uuid: Uuid = Uuid::parse_str(&uuid_str).unwrap();

        let mut player = Player::new(uuid);
        player.load_redis(&domain, &mut con)?;
        if let Some(scores) = &mut player.scores {
            let new_score = scores.get(&objective).unwrap_or(&0) + add_val;
            scores.insert(objective.to_string(), new_score);
            player.update_history("Added bug tokens");
            player.save_redis(&domain, &mut con)?;
        }
        println!("{}", player);
    }

    Ok(())
}

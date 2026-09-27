use std::{
    env,
    fs::{self, File},
    io::{BufWriter, Write},
    path::Path,
};

use log::LevelFilter;
use monumenta::leaderboards;
use redis::Commands;
use serde::Serialize;
use simplelog::{ColorChoice, CombinedLogger, Config, SharedLogger, TermLogger, TerminalMode};

#[derive(Serialize)]
struct ScoreEntry {
    name: String,
    score: i32,
}

fn main() -> anyhow::Result<()> {
    CombinedLogger::init(vec![TermLogger::new(
        LevelFilter::Debug,
        Config::default(),
        TerminalMode::Mixed,
        ColorChoice::Auto,
    ) as Box<dyn SharedLogger>])
    .unwrap();

    let mut args: Vec<String> = env::args().collect();

    if args.len() != 5 {
        print_usage();
        return Ok(());
    }

    // Parse args
    args.remove(0);

    let redis_uri = args.remove(0);
    let domain = args.remove(0);
    let lb_config_dir = args.remove(0);
    let output_dir = args.remove(0);

    // Ensure output_dir exists
    let output_dir = Path::new(&output_dir);
    if !output_dir.is_dir() {
        fs::create_dir_all(output_dir)?;
    }
    // Create redis connection and fetch all leaderboard configs
    let client = redis::Client::open(redis_uri)?;
    let mut con: redis::Connection = client.get_connection()?;
    let configs = leaderboards::load_configs(&lb_config_dir)?;

    for cfg in &configs {
        // Get all leaderboard score entries for a given objective
        // Returns [] if the object has no associated zset
        let key = format!("{}:leaderboard:{}", domain, cfg.objective);
        let entries: Vec<(String, f64)> = con.zrevrange_withscores(&key, 0, -1)?;
        let scores: Vec<ScoreEntry> = entries
            .iter()
            .map(|(name, score)| ScoreEntry {
                name: name.clone(),
                score: *score as i32,
            })
            .collect();

        // Write to output_dir/<objective>.json
        let path = output_dir.join(format!("{}.json", cfg.objective));
        let mut writer = BufWriter::new(File::create(path)?);
        serde_json::to_writer_pretty(&mut writer, &scores)?;
        writer.flush()?;
    }

    Ok(())
}

fn print_usage() {
    println!("Usage: export_leaderboard_scores redis://127.0.0.1 <domain> <leaderboard-configs-dir> <output-dir>");
}

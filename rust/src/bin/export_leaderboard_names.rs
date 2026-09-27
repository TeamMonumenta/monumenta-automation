use std::{collections::HashSet, env, fs::File, io};

use log::LevelFilter;
use serde::{Deserialize, Serialize};
use simplelog::{ColorChoice, CombinedLogger, Config, SharedLogger, TermLogger, TerminalMode};
use walkdir::WalkDir;

#[derive(Deserialize)]
struct LeaderboardConfig {
    objective: String,
    plain_display_name: String,
    category: Option<String>,
    release: Option<String>,
}
#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct LeaderboardOut {
    objective: String,
    display_name: String,
    category: Option<String>,
    release: Option<String>,
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

    if args.len() != 3 {
        print_usage();
        return Ok(());
    }

    // Read args
    args.remove(0);
    let lb_config_dir = args.remove(0);
    let output_file = args.remove(0);

    // Get all valid json entries in specified config dir.
    let mut entries: Vec<LeaderboardOut> = Vec::new();
    let mut seen: HashSet<String> = HashSet::new();

    for entry in WalkDir::new(&lb_config_dir) {
        let entry = entry?;

        if entry.file_type().is_file() && entry.path().extension().is_some_and(|ext| ext == "json") {
            let file = File::open(entry.path())?;
            let cfg: LeaderboardConfig = serde_json::from_reader(io::BufReader::new(file))?;

            // Skip duplicate entries (there shouldn't be any, but just in case)
            if seen.contains(&cfg.objective) {
                continue;
            }

            seen.insert(cfg.objective.clone());
            entries.push(LeaderboardOut {
                objective: cfg.objective,
                display_name: cfg.plain_display_name,
                category: cfg.category,
                release: cfg.release,
            });
        }
    }

    // Write to output file
    let file = File::create(&output_file)?;
    let mut writer = io::BufWriter::new(file);
    serde_json::to_writer_pretty(&mut writer, &entries)?;
    io::Write::flush(&mut writer)?;

    Ok(())
}

fn print_usage() {
    println!("Usage: export_leaderboard_names <leaderboard-configs-dir> <output-file>");
}

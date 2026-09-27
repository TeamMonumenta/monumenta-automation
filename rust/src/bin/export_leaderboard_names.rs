use std::{env, fs::File, io};

use log::LevelFilter;
use monumenta::leaderboards;
use serde::Serialize;
use simplelog::{ColorChoice, CombinedLogger, Config, SharedLogger, TermLogger, TerminalMode};

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
    let entries: Vec<LeaderboardOut> = leaderboards::load_configs(&lb_config_dir)?
        .into_iter()
        .map(|cfg| LeaderboardOut {
            objective: cfg.objective,
            display_name: cfg.plain_display_name,
            category: cfg.category,
            release: cfg.release,
        })
        .collect();

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


use monumenta::scoreboard;

use anyhow;

use std::env;

fn usage() {
    println!("Usage: find_unassigned_objectives <domain>");
}

fn main() -> anyhow::Result<()> {
    /* Load all the arguments as datapacks */
    let mut args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        usage();
        return Ok(());
    }

    args.remove(0); // Program name
    let domain = args.remove(0);

    let client = redis::Client::open("redis://127.0.0.1/")?;
    let mut con: redis::Connection = client.get_connection()?;

    let mut scoreboards = scoreboard::ScoreboardCollection::new();
    let scoreboard = scoreboard::Scoreboard::load_redis(&domain, &mut con)?;
    scoreboards.add_existing_scoreboard(scoreboard)?;

    let count_vec: Vec<(String, f64)> = scoreboards.get_objective_usage_sorted();

    println!("Objectives by usage:");
    for (objective_name, percentage) in count_vec.iter() {
        println!("{0: <20}{1}", objective_name, percentage);
    }

    /* Put all the zero count items into a new unused_vec and sort by name */
    let unused_vec: Vec<&(String, f64)> = count_vec.iter().filter(|(_, val)| *val == 0.0).collect();
    let mut unused_vec: Vec<&String> = unused_vec
        .iter()
        .map(|(objective_name, _)| objective_name)
        .collect();
    unused_vec.sort_by(|a, b| b.partial_cmp(a).unwrap());

    println!("\n\nUnused objectives:");
    for objective_name in unused_vec.iter() {
        println!("{}", objective_name);
    }

    Ok(())
}

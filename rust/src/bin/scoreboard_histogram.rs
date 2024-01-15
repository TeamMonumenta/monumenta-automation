use monumenta::scoreboard;

use anyhow;

use std::{collections::HashMap, env};

fn main() -> anyhow::Result<()> {
    /* Load all the arguments as datapacks */
    let mut args: Vec<String> = env::args().collect();

    if args.len() != 3 {
        println!("Usage: scoreboard_histogram path/to/scoreboard.dat objective_name");
        return Ok(());
    }

    args.remove(0);
    let scoreboard_path = args.get(0).unwrap();
    let scoreboard = scoreboard::Scoreboard::load(scoreboard_path)?;
    let objective_name = args.get(1).unwrap();
    let objective = scoreboard.objectives.get(objective_name).unwrap();

    let mut freq_map: HashMap<i32, i32> = HashMap::new();
    for (_, value) in objective.data.iter() {
        let mut seen_count = *freq_map.get(&value.score).unwrap_or(&0);
        seen_count += 1;
        freq_map.insert(value.score, seen_count);
    }

    /* Create a vector from the hash table data and sort it by key */
    let mut count_vec: Vec<(&i32, &i32)> = freq_map.iter().collect();
    count_vec.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());

    println!(
        "Distribution of objective {} for scoreboard {}:",
        objective_name, scoreboard_path
    );
    for (value, amount) in count_vec.iter() {
        println!("{0: <10}{1}", value, amount);
    }

    Ok(())
}

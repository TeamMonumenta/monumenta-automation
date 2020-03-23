use std::env;
use std::collections::HashMap;

use std::error::Error;
type BoxResult<T> = Result<T,Box<dyn Error>>;

use monumenta::scoreboard;

fn main() -> BoxResult<()> {
    /* Load all the arguments as datapacks */
    let mut args: Vec<String> = env::args().collect();

    if args.len() <= 1 {
        println!("Usage: find_unassigned_objectives path/to/datapack path/to/other_datapack ...");
        return Ok(());
    }

    let mut scoreboards = scoreboard::ScoreboardCollection::new();

    args.remove(0);
    while let Some(arg) = args.pop() {
        scoreboards.add_scoreboard(&arg)?;
    }

    /*
     * Iterate over all scoreboards and accumulate the nonzero_count and total_entries for each
     * objective
     *
     * key = objective name
     * val = (nonzero_count, total_entries)
     */
    let mut counts: HashMap<String, (i32, i32)> = HashMap::new();
    for (_, scoreboard) in scoreboards.scoreboards.iter() {
        for (objective_name, objective) in scoreboard.objectives.iter() {
            let mut nonzero_count = 0;
            let mut total_entries = 0;

            /* Retrieve stored values from the hash table if they are present */
            if let Some((stored_nonzero_count, stored_total_entries)) = counts.get(objective_name) {
                nonzero_count = *stored_nonzero_count;
                total_entries = *stored_total_entries;
            }

            for (_, score) in objective.data.iter() {
                total_entries += 1;
                if score.score != 0 {
                    nonzero_count += 1
                }
            }

            /*
             * This avoids 0/0 later. Just assume each objective had at least one item in it that
             * was 0
             */
            if total_entries == 0 {
                total_entries = 1;
            }

            counts.insert(objective_name.to_string(), (nonzero_count, total_entries));
        }
    }

    /* Create a vector from the hash table data and sort it by value */
    let mut count_vec: Vec<(String, f64)> = counts.iter().map(|(objective_name, (nonzero_count, total_entries))| (objective_name.to_string(), *nonzero_count as f64 / *total_entries as f64)).collect();
    count_vec.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

    println!("Objectives by usage:");
    for (objective_name, percentage) in count_vec.iter() {
        println!("{0: <20}{1}", objective_name, percentage);
    }

    /* Put all the zero count items into a new unused_vec and sort by name */
    let unused_vec: Vec<&(String, f64)> = count_vec.iter().filter(|(_, val)| *val == 0.0).collect();
    let mut unused_vec: Vec<&String> = unused_vec.iter().map(|(objective_name, _)| objective_name).collect();
    unused_vec.sort_by(|a, b| b.partial_cmp(&a).unwrap());

    println!("\n\nUnused objectives:");
    for objective_name in unused_vec.iter() {
            println!("{}", objective_name);
    }

    Ok(())
}

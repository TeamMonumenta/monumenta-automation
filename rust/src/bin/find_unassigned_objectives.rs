use std::env;

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

    let count_vec: Vec<(String, f64)> = scoreboards.get_objective_usage_sorted();

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

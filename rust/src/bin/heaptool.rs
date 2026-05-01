use std::fs::File;

use anyhow::Result;
use clap::Parser;
use memmap2::Mmap;
use monumenta::hprof::read_prof;

#[derive(Parser, Debug)]
struct Cli {
    #[arg()]
    file: String,

    /// Minimum number of leaked instances of a given class to report and trigger a non-zero exit
    /// code. Use this to avoid false positives from objects transiently in-flight when the heap
    /// dump was captured.
    #[arg(long, default_value_t = 1)]
    min_leaked: usize,
}

fn main() -> Result<()> {
    let args = Cli::parse();
    let contents = unsafe { Mmap::map(&File::open(args.file)?)? };
    let leaks_found = read_prof(&contents, args.min_leaked)?;
    if leaks_found {
        std::process::exit(1);
    }
    Ok(())
}

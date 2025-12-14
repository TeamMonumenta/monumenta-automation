use std::fs::File;

use anyhow::Result;
use clap::Parser;
use memmap2::Mmap;
use monumenta::hprof::read_prof;

#[derive(Parser, Debug)]
struct Cli {
    #[arg()]
    file: String,
}

fn main() -> Result<()> {
    let args = Cli::parse();
    let contents = unsafe { Mmap::map(&File::open(args.file)?)? };
    read_prof(&contents)?;
    Ok(())
}

use std::fs::File;

use alloc::peak_usage;
use anyhow::Result;
use clap::Parser;
use memmap2::Mmap;
use reader::read_prof;

mod graph;
mod alloc;
mod reader;
mod id;

#[derive(Parser, Debug)]
struct Cli {
    #[arg()]
    file: String,
}

fn main() -> Result<()> {
    let args = Cli::parse();
    let contents = unsafe { Mmap::map(&File::open(args.file)?)? };
    read_prof(&contents)?;

    println!("max bytes used: {}", peak_usage());

    Ok(())
}

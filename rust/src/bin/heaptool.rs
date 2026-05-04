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

    /// Minimum number of leaked instances for a pattern group to be included in output. Groups
    /// below this threshold are still counted in the header but not printed.
    #[arg(long, default_value_t = 1)]
    min_pattern_leaked: usize,

    /// Disable inner class name normalization in pattern signatures. By default, inner class
    /// suffixes are stripped (e.g. HashMap$Node and HashMap$TreeNode both become HashMap;
    /// BossAbilityGroup$1 and BossAbilityGroup$2 both become BossAbilityGroup) so that
    /// structurally equivalent patterns are grouped together.
    #[arg(long)]
    no_normalize_inner_classes: bool,

    /// Show object IDs (hex addresses) next to each entry in pattern output. IDs are from one
    /// arbitrary example instance and change between runs, so they are hidden by default to keep
    /// output diff-friendly.
    #[arg(long)]
    show_ids: bool,

    /// Emit results as a JSON array to stdout. Each element has an instance_count and a chain
    /// array of compact display strings matching the normal text output (runs collapsed, field
    /// annotations included). Progress and summary messages are still written to stderr.
    #[arg(long)]
    json: bool,
}

fn main() -> Result<()> {
    let args = Cli::parse();
    let contents = unsafe { Mmap::map(&File::open(args.file)?)? };
    let leaks_found = read_prof(&contents, args.min_leaked, args.min_pattern_leaked, !args.no_normalize_inner_classes, args.show_ids, args.json)?;
    if leaks_found {
        std::process::exit(1);
    }
    Ok(())
}

use anyhow;
use redis::Commands;

use std::{
    collections::{BTreeMap, HashSet},
    env
};

fn usage() {
    println!("Usage: shard_utils 'redis://127.0.0.1/' <domain> get <player_name>");
    println!("Usage: shard_utils 'redis://127.0.0.1/' <domain> histogram");
    println!("Usage: shard_utils 'redis://127.0.0.1/' <domain> transfer <player_name> <shard>");
    println!("Usage: shard_utils 'redis://127.0.0.1/' <domain> bulk_transfer <comma_separated_sources> <comma_separated_destinations>");
}

fn main() -> anyhow::Result<()> {
    let mut args: Vec<String> = env::args().collect();

    if args.len() < 4 {
        usage();
        return Ok(());
    }

    args.remove(0);

    let redis_uri = args.remove(0);
    let client = redis::Client::open(redis_uri)?;
    let mut con : redis::Connection = client.get_connection()?;

    let domain = args.remove(0);
    let locations_key = format!("{}:bungee:locations", domain);

    match &args.remove(0)[..] {
        "get" => {
            return get(&mut con, &locations_key, &mut args);
        },
        "histogram" => {
            return histogram(&mut con, &locations_key, &mut args);
        },
        "transfer" => {
            return transfer(&mut con, &locations_key, &mut args);
        },
        "bulk_transfer" => {
            return bulk_transfer(&mut con, &locations_key, &mut args);
        },
        _ => {
            usage();
            return Ok(());
        }
    };
}

fn get(con: &mut redis::Connection, locations_key: &String, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 1 {
        usage();
        return Ok(());
    }

    let player_name = args.remove(0);
    let player_uuid_str: String = con.hget("name2uuid", &player_name)?;

    let shard: String = con.hget(&locations_key, &player_uuid_str)?;

    println!("{} is on {}", player_name, shard);

    return Ok(());
}

fn histogram(con: &mut redis::Connection, locations_key: &String, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 0 {
        usage();
        return Ok(());
    }

    println!("Histogram:");
    let mut total_players: usize = 0;
    let mut player_counts: BTreeMap<String, usize> = BTreeMap::new();
    let iter: redis::Iter<'_, (String, String)> = con.hscan(&locations_key)?;
    for (_, shard) in iter {
        total_players += 1;
        match player_counts.get(&shard) {
            Some(&old_count) => {
                player_counts.insert(shard, 1 + old_count);
            },
            None => {
                player_counts.insert(shard, 1);
            }
        }
    }

    let header_shard: String = "Shard".to_string();
    let header_count: String = "Count".to_string();
    let header_histogram: String = "Histogram (log2)".to_string();

    let mut max_shard_width: usize = header_shard.len();
    let mut max_count_width: usize = header_count.len();
    for (shard, count) in &player_counts {
        let test_size: usize = format!("{shard}", shard=shard).len();
        if test_size > max_shard_width {
            max_shard_width = test_size;
        }

        let test_size: usize = format!("{count}", count=count).len();
        if test_size > max_count_width {
            max_count_width = test_size;
        }
    }

    println!("{shard:<max_shard_width$} │ {count:>max_count_width$} │ {bar}",
        shard=header_shard,
        max_shard_width=max_shard_width,
        count=header_count,
        max_count_width=max_count_width,
        bar=header_histogram
    );
    println!("{}─┼─{}─┼─{}",
        "─".repeat(max_shard_width),
        "─".repeat(max_count_width),
        "─".repeat(header_histogram.len())
    );
    for (shard, count) in &player_counts {
        println!("{shard:<max_shard_width$} │ {count:>max_count_width$} │ {bar}",
            shard=shard,
            max_shard_width=max_shard_width,
            count=count,
            max_count_width=max_count_width,
            bar="━".repeat(histogram_len(*count))
        );
    }

    println!("There are {} players across {} shards.", total_players, player_counts.len());
    return Ok(());
}

fn histogram_len(count: usize) -> usize {
    if count <= 0 {
        return 0;
    }
    return (count as f32 + 1.).log2().ceil() as usize;
}

fn transfer(con: &mut redis::Connection, locations_key: &String, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 2 {
        usage();
        return Ok(());
    }

    let player_name = args.remove(0);
    let player_uuid_str: String = con.hget("name2uuid", &player_name)?;

    let shard: String = args.remove(0);
    con.hset(&locations_key, &player_uuid_str, &shard)?;

    println!("Transferred {} to {}", player_name, shard);

    return Ok(());
}

fn bulk_transfer(con: &mut redis::Connection, locations_key: &String, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 2 {
        usage();
        return Ok(());
    }

    let from_shards_str = args.remove(0);
    let mut from_shards: HashSet<String> = HashSet::new();
    println!("Transferring players from the shard(s):");
    for from_shard in from_shards_str.split(",") {
        println!("- {}", from_shard);
        from_shards.insert(from_shard.to_string());
    }

    let to_shards_str: String = args.remove(0);
    let mut to_shards_vec: Vec<String> = Vec::new();
    println!("...to the shard(s):");
    for to_shard_str in to_shards_str.split(",") {
        println!("- {}", to_shard_str);
        let to_shard: String = to_shard_str.to_string();
        to_shards_vec.push(to_shard);
    }

    println!("Getting list to modify...");
    let mut to_update: HashSet<String> = HashSet::new();
    let iter: redis::Iter<'_, (String, String)> = con.hscan(&locations_key)?;
    for (player_uuid_str, from_shard) in iter {
        if from_shards.contains(&from_shard) {
            to_update.insert(player_uuid_str);
        }
    }
    println!("Applying changes...");
    let mut to_index: usize = 0;
    for player_uuid_str in &to_update {
        let to_shard: &String = &to_shards_vec.get(to_index).unwrap();
        to_index = (to_index + 1) % &to_shards_vec.len();
        con.hset(&locations_key, &player_uuid_str, &to_shard)?;
    }
    println!("Transferred {} players", &to_update.len());

    return Ok(());
}

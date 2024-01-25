use std::env;
use anyhow::bail;
use chrono::Duration;
use monumenta::lockout_lib::LockoutEntry;
use serde_json::json;

fn usage() {
    println!("Usage: lockout 'redis://127.0.0.1/' <domain> claim <shard> <owner> <duration in minutes> <reason>");
    println!("Usage: lockout 'redis://127.0.0.1/' <domain> check <shard>");
    println!("Usage: lockout 'redis://127.0.0.1/' <domain> checkall");
    println!();
    println!("A lockout allows a player to claim a shard, preventing others from using it until they are done.");
    println!();
    println!("Returns json to stdout in the form {{\"results\": results}}, where:");
    println!("- A single result from claim or check is in the format: `null` or:");
    println!("{{");
    println!("    \"domain\": \"volt\",");
    println!("    \"shard\": \"* or valley-2\",");
    println!("    \"owner\": \"@NickNackGus (example for in-game mention, for Discord use all lowercase)\",");
    println!("    \"expiration\": <Unix Timestamp in milliseconds>,");
    println!("    \"reason\": \"Testing the lockout system\",");
    println!("}}");
    println!();
    println!("Starting a new claim will return null on error, or the new/old claim on that shard.");
    println!();
    println!("checkall returns an object of shard name to active lockout results instead.");
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

    return match &args.remove(0)[..] {
        "claim" => {
            claim(&domain, &mut con, &mut args)
        },
        "check" => {
            check(&domain, &mut con, &mut args)
        },
        "checkall" => {
            check_all(&domain, &mut con, &mut args)
        },
        _ => {
            usage();
            Ok(())
        },
    }
}

fn claim(domain: &str, con: &mut redis::Connection, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 4 {
        usage();
        return Ok(());
    }

    let shard = args.remove(0);
    let owner = args.remove(0);
    let duration_str = args.remove(0);
    let reason = args.remove(0);

    let num_minutes: i64 = duration_str.parse()?;
    if num_minutes < 1 {
        bail!("Cannot start a claim for less than 1 minute: {}", num_minutes);
    }
    let duration = Duration::minutes(num_minutes);

    let new_lockout = LockoutEntry::new(&owner, duration, &domain, &shard, &reason)?;
    let found_lockout = new_lockout.start_lockout(con);

    let final_result = json!({
        "results": found_lockout
    });
    let result_json = serde_json::to_string(&final_result)?;
    print!("{}", result_json);

    Ok(())
}

fn check(domain: &str, con: &mut redis::Connection, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 1 {
        usage();
        return Ok(());
    }

    let shard = args.remove(0);

    let opt_result = LockoutEntry::get_lockout(domain, con, &shard);
    let final_result = json!({
        "results": opt_result
    });
    let result_json = serde_json::to_string(&final_result)?;
    print!("{}", result_json);
    Ok(())
}

fn check_all(domain: &str, con: &mut redis::Connection, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 0 {
        usage();
        return Ok(());
    }

    let results = LockoutEntry::get_all_lockouts(domain, con)?;
    let final_result = json!({
        "results": results
    });
    let result_json = serde_json::to_string(&final_result)?;
    print!("{}", result_json);
    Ok(())
}

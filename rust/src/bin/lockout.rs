use std::env;
use anyhow::bail;
use chrono::Duration;
use monumenta::lockout_lib::{LockoutAPI, LockoutEntry};
use serde_json::json;

fn usage() {
    println!("Usage: lockout <domain> claim <shard> <owner> <duration in minutes> <reason>");
    println!("Usage: lockout <domain> check <shard>");
    println!("Usage: lockout <domain> checkall");
    println!("Usage: lockout <domain> clear <shard> <owner>");
    println!();
    println!("A lockout allows a player to claim a shard, preventing others from using it until they are done.");
    println!();
    println!("Returns json to stdout in the form {{\"results\": results}}, where:");
    println!("- A single claim is in the format: `null` or:");
    println!("{{");
    println!("    \"domain\": \"volt\",");
    println!("    \"shard\": \"* or valley-2\",");
    println!("    \"owner\": \"@NickNackGus (example for in-game mention, for Discord use all lowercase)\",");
    println!("    \"expiration\": <Unix Timestamp in milliseconds>,");
    println!("    \"reason\": \"Testing the lockout system\",");
    println!("}}");
    println!();
    println!("Starting a new claim will return the new/old claim on that shard.");
    println!();
    println!("check returns a single claim or null.");
    println!();
    println!("checkall returns an object of shard name to active lockout results instead.");
    println!();
    println!("clear returns the cleared claims");
    println!();
    println!("Claiming the shard * claims all shards");
    println!("Clearing the owner * clears all owners");
}

fn main() -> anyhow::Result<()> {
    let mut args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        usage();
        return Ok(());
    }

    args.remove(0);

    let domain = args.remove(0);

    return match &args.remove(0)[..] {
        "claim" => {
            claim(&domain, &mut args)
        },
        "check" => {
            check(&domain, &mut args)
        },
        "checkall" => {
            check_all(&domain, &mut args)
        },
        "clear" => {
            clear(&domain, &mut args)
        }
        _ => {
            usage();
            Ok(())
        },
    }
}

fn claim(domain: &str, args: &mut Vec<String>) -> anyhow::Result<()> {
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
    let mut api: LockoutAPI = LockoutAPI::load(domain)?;
    let found_lockout = api.start_lockout(new_lockout.clone());
    api.save()?;

    let final_result = json!({
        "results": found_lockout
    });
    let result_json = serde_json::to_string(&final_result)?;
    print!("{}", result_json);

    if found_lockout.owner != new_lockout.owner {
        bail!("Another user has a conflicting claim");
    }
    if found_lockout.shard != new_lockout.shard {
        bail!("You have a conflicting claim elsewhere");
    }

    Ok(())
}

fn check(domain: &str, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 1 {
        usage();
        return Ok(());
    }

    let shard = args.remove(0);

    let mut api: LockoutAPI = LockoutAPI::load(domain)?;
    let opt_result = api.get_lockout(&shard);
    api.save()?;
    let final_result = json!({
        "results": opt_result
    });
    let result_json = serde_json::to_string(&final_result)?;
    print!("{}", result_json);
    Ok(())
}

fn check_all(domain: &str, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 0 {
        usage();
        return Ok(());
    }

    let mut api: LockoutAPI = LockoutAPI::load(domain)?;
    let results = api.get_all_lockouts();
    api.save()?;
    let final_result = json!({
        "results": results
    });
    let result_json = serde_json::to_string(&final_result)?;
    print!("{}", result_json);
    Ok(())
}

fn clear(domain: &str, args: &mut Vec<String>) -> anyhow::Result<()> {
    if args.len() != 2 {
        usage();
        return Ok(());
    }

    let shard = args.remove(0);
    let owner = args.remove(0);

    let mut api: LockoutAPI = LockoutAPI::load(domain)?;
    let opt_result = api.clear_lockouts(&shard, &owner);
    api.save()?;
    let final_result = json!({
        "results": opt_result
    });
    let result_json = serde_json::to_string(&final_result)?;
    print!("{}", result_json);
    Ok(())
}


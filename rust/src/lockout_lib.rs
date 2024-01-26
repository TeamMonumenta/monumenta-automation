use std::collections::HashMap;
use std::fmt;
use std::fmt::Formatter;

use anyhow::{self, bail};
use chrono::{DateTime, Duration, Utc};
use chrono::serde::ts_seconds;
use redis::{Commands, RedisResult};
use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize)]
pub struct LockoutEntry {
    pub domain: String,
    pub shard: String,
    pub owner: String,
    #[serde(with = "ts_seconds")]
    pub expiration: DateTime<Utc>,
    pub reason: String,
}

impl fmt::Display for LockoutEntry {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{} {} is locked by {} until {} for {}",
            self.domain,
            self.shard,
            self.owner,
            self.expiration,
            self.reason,
        )
    }
}

impl fmt::Debug for LockoutEntry {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        match serde_json::to_string(self) {
            Ok(value) => {
                write!(f, "{}",
                    value
                )
            }
            Err(_) => {
                write!(f, "LockoutEntry{{{}, {}, {}, {}, {}}}",
                       self.domain,
                       self.shard,
                       self.owner,
                       self.expiration,
                       self.reason,
                )
            }
        }
    }
}

impl LockoutEntry {
    pub fn new(owner: &str, duration: Duration, domain: &str, shard: &str, reason: &str) -> anyhow::Result<LockoutEntry> {
        let opt_expiration: Option<DateTime<Utc>> = Utc::now().checked_add_signed(duration);
        if opt_expiration.is_none() {
            bail!("Invalid duration option")
        }
        Ok(LockoutEntry {
            owner: owner.to_string(),
            expiration: opt_expiration.unwrap(),
            domain: domain.to_string(),
            shard: shard.to_string(),
            reason: reason.to_string(),
        })
    }

    pub fn start_lockout(&self, con: &mut redis::Connection) -> Option<LockoutEntry> {
        return match Self::get_lockout(self.domain.as_ref(), con, self.shard.as_ref()) {
            None => {
                self._internal_set_lockout(con, None)
            }
            Some(existing) => {
                if existing.owner == self.owner {
                    self._internal_set_lockout(con, Some(existing.clone()))
                } else {
                    Some(existing.clone())
                }
            }
        }
    }

    fn _internal_set_lockout(&self, con: &mut redis::Connection, current: Option<LockoutEntry>) -> Option<LockoutEntry> {
        let self_json: String = serde_json::to_string(&self).unwrap();
        match con.hset::<String, String, String, i64>(format!("{}:lockout", self.domain), self.shard.clone(), self_json) {
            Ok(_) => {
                Some(self.clone())
            },
            Err(err) => {
                eprintln!("An error occurred: {}", err);
                current
            }
        }
    }

    pub fn get_lockout(domain: &str, con: &mut redis::Connection, shard: &str) -> Option<LockoutEntry> {
        match Self::get_all_lockouts(&domain, con, false) {
            Ok(all_lockouts) => {
                let opt_all_shard_lockout = all_lockouts.get("*");
                if opt_all_shard_lockout.is_some() {
                    return opt_all_shard_lockout.cloned();
                }

                let opt_shard_lockout = all_lockouts.get(shard);
                if opt_shard_lockout.is_some() {
                    return opt_shard_lockout.cloned();
                }

                None
            }
            Err(_) => None
        }
    }

    pub fn get_all_lockouts(domain: &str, con: &mut redis::Connection, debug: bool) -> anyhow::Result<HashMap<String, LockoutEntry>> {
        let mut lockouts: HashMap<String, LockoutEntry> = HashMap::new();

        let raw_lockouts: HashMap<String, String> = con.hgetall(format!("{}:lockout", domain))?;
        for raw_lockout in raw_lockouts.values() {
            let lockout: LockoutEntry = serde_json::from_str(raw_lockout)?;
            if debug || !Self::handle_expiration(&lockout, con) {
                lockouts.insert(lockout.shard.clone(), lockout);
            }
        }

        Ok(lockouts)
    }

    pub fn clear_lockouts(domain: &str, con: &mut redis::Connection, shard: &str, owner: &str) -> anyhow::Result<()> {
        for lockout in Self::get_all_lockouts(domain, con, false)?.values() {
            if owner != "*" && owner != lockout.owner {
                continue;
            }

            if shard != "*" && shard != lockout.shard {
                continue;
            }

            lockout.rescind(con)?;
        }
        Ok(())
    }

    pub fn rescind(&self, con: &mut redis::Connection) -> RedisResult<i64> {
        con.hdel(format!("{}:lockout", &self.domain), &self.shard)
    }

    pub fn has_expired(&self) -> bool {
        Utc::now() >= self.expiration
    }

    // Returns true for expired entries
    pub fn handle_expiration(lockout: &LockoutEntry, con: &mut redis::Connection) -> bool {
        if !lockout.has_expired() {
            return false;
        }

        match lockout.rescind(con) {
            Ok(_) => (),
            Err(_) => ()
        }
        return true;
    }
}

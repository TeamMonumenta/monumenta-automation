use std::collections::HashMap;
use std::fmt;
use std::fmt::Formatter;
use std::fs::{create_dir_all, read_to_string, write};

use anyhow::{self, bail};
use chrono::{DateTime, Duration, Utc};
use chrono::serde::ts_seconds;
use redis::{Commands, RedisResult};
use serde::{Deserialize, Serialize};

pub struct LockoutAPI {
    domain: String,
    entries: HashMap<String, LockoutEntry>,
}

impl LockoutAPI {
    fn default(domain: &str) -> LockoutAPI {
        let entries: HashMap<String, LockoutEntry> = HashMap::new();
        LockoutAPI{
            domain: domain.to_string(),
            entries,
        }
    }

    pub fn load(domain: &str) -> anyhow::Result<LockoutAPI> {
        if let Err(_) = create_dir_all("/home/epic/4_SHARED/lockouts") {
            bail!("Unable to create lockouts directory")
        }
        let lockout_path = format!("/home/epic/4_SHARED/lockouts/{}.json", domain);
        let lockout_json_text = match read_to_string(lockout_path) {
            Ok(data) => {data}
            Err(_) => {
                return Ok(Self::default(domain));
            }
        };

        let raw_entries: serde_json::Map<String, serde_json::Value> = match serde_json::from_str(&*lockout_json_text) {
            Ok(data) => {
                data
            },
            Err(_) => {
                return Ok(Self::default(domain));
            }
        };

        let mut entries: HashMap<String, LockoutEntry> = HashMap::new();
        for (shard, raw_entry) in raw_entries {
            if let Ok(entry) = serde_json::from_value::<LockoutEntry>(raw_entry) {
                if entry.is_current() {
                    entries.insert(shard, entry);
                }
            }
        };

        return Ok(LockoutAPI{
            domain: domain.to_string(),
            entries,
        })
    }

    pub fn save(&mut self) -> anyhow::Result<()> {
        if let Err(_) = create_dir_all("/home/epic/4_SHARED/lockouts") {
            bail!("Unable to create lockouts directory")
        }
        let lockout_path = format!("/home/epic/4_SHARED/lockouts/{}.json", self.domain);
        let serialized = serde_json::to_string_pretty(&self.entries);
        if let Err(_) = serialized {
            bail!("Unable to serialize lockouts");
        }
        if let Err(_) = write(lockout_path, serialized.unwrap()) {
            bail!("Unable to save lockouts")
        }
        Ok(())
    }

    pub fn start_lockout(&mut self, entry: LockoutEntry) -> LockoutEntry {
        if entry.shard == "*" {
            // Check for existing entries from other owners
            for existing_entry in self.entries.values() {
                if entry.owner != existing_entry.owner {
                    return existing_entry.clone();
                }
            }

            // Clear all entries from the same owner
            self.entries.clear();
        } else {
            // Check for an existing entries from other owners
            if let Some(&ref existing_entry) = self.entries.get("*") {
                if entry.owner != existing_entry.owner {
                    return existing_entry.clone();
                }
            }
            if let Some(&ref existing_entry) = self.entries.get(&entry.shard) {
                if entry.owner != existing_entry.owner {
                    return existing_entry.clone();
                }
            }

            // Remove existing entries from the same owner if there are no conflicts
            if let Some(&ref existing_entry) = self.entries.clone().get("*") {
                self.entries.remove(&existing_entry.owner);
            }
            if let Some(&ref existing_entry) = self.entries.clone().get(&entry.shard) {
                self.entries.remove(&existing_entry.owner);
            }
        }

        self.entries.insert(entry.shard.clone(), entry.clone());
        entry.clone()
    }

    pub fn get_lockout(&mut self, shard: &str) -> Option<LockoutEntry> {
        match self.entries.get("*") {
            Some(&ref entry) => {
                return Some(entry.clone());
            }
            None => {
            }
        }

        match self.entries.get(shard) {
            Some(&ref entry) => {
                return Some(entry.clone());
            }
            None => {
            }
        }

        None
    }

    pub fn get_all_lockouts(&self) -> HashMap<String, LockoutEntry> {
        self.entries.clone()
    }

    pub fn clear_lockouts(&mut self, shard: &str, owner: &str) -> HashMap<String, LockoutEntry> {
        let mut cleared: HashMap<String, LockoutEntry> = HashMap::new();
        self.entries.retain(|_, entry| {
            let keep = entry.keep_after_clear(shard, owner);
            if !keep {
                cleared.insert(entry.shard.clone(), entry.clone());
            }
            keep
        });
        cleared
    }
}

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

    pub fn keep_after_clear(&self, shard: &str, owner: &str) -> bool {
        return !((shard == "*" || shard == self.shard) && (owner == "*" || owner == self.owner));
    }

    pub fn rescind(&self, con: &mut redis::Connection) -> RedisResult<i64> {
        con.hdel(format!("{}:lockout", &self.domain), &self.shard)
    }

    pub fn is_current(&self) -> bool {
        Utc::now() < self.expiration
    }
}

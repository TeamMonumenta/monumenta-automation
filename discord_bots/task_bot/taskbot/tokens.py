"""Manage service tokens: long-lived API tokens for other programs.

Service tokens let the game plugin on the shards reach the API and act for
Minecraft players (see API.md, "Service tokens"). They aren't tied to a Discord
user, so they are created here, with access to the database, rather than with
the Discord slash command. Run inside the bot's pod:

    kubectl exec deploy/bug-bot -- python -m taskbot.tokens create shards-play
    kubectl exec deploy/bug-bot -- python -m taskbot.tokens list
    kubectl exec deploy/bug-bot -- python -m taskbot.tokens revoke shards-play

The database path comes from the same config.yml as the bot ($TASK_HOME), or --db.
A token is printed once; only its hash is stored.
"""

import argparse
import datetime
import hashlib
import os
import re
import secrets
import sys
from typing import Optional

from . import config as config_mod
from .service import Conflict, TaskService, UserError
from .store import TaskStore


MAX_TOKENS_PER_USER = 20
TOKEN_PREFIX = "tb_"             # minted in Discord for a team member
SERVICE_TOKEN_PREFIX = "tbs_"    # minted here for another program


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def mint_token(service: TaskService, discord_id: int, ttl_hours: int, scope: str) -> tuple[str, int]:
    """Create a token, returning (raw token, expires_at). Only its hash is stored."""
    store = service.store
    now = service.now()
    if store.count_tokens(discord_id, now) >= MAX_TOKENS_PER_USER:
        raise Conflict(f"You already have {MAX_TOKENS_PER_USER} active tokens; revoke them first")
    token = TOKEN_PREFIX + secrets.token_urlsafe(32)
    expires_at = now + ttl_hours * 3600
    store.add_token(hash_token(token), discord_id, scope, now, expires_at)
    return token, expires_at


def mint_service_token(service: TaskService, name: str, max_privilege: int, ttl_days: int,
                       scope: str = "write") -> tuple[str, int]:
    """A long-lived token for another program, e.g. the game plugin on the play shards.

    It isn't tied to a Discord user. A request with it acts either as the service
    itself, or (with the player headers) as a Minecraft player, with whatever
    privilege the service asserts for that player, capped at max_privilege.
    """
    if not re.match(r"^[a-z0-9][a-z0-9_.-]{0,63}$", name):
        raise UserError("Service names are lowercase letters, digits, '.', '_' and '-'")
    now = service.now()
    token = SERVICE_TOKEN_PREFIX + secrets.token_urlsafe(32)
    expires_at = now + ttl_days * 86400
    service.store.add_token(hash_token(token), 0, scope, now, expires_at, service=name,
                            max_privilege=max(0, min(4, max_privilege)))
    return token, expires_at


def _fmt(ts: Optional[int]) -> str:
    if ts is None:
        return "never"
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m taskbot.tokens", description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    parser.add_argument("--db", help="database file (default: db_path from $TASK_HOME/config.yml)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_create = sub.add_parser("create", help="create a service token and print it once")
    p_create.add_argument("service", help="a name for what will use it, e.g. shards-play")
    p_create.add_argument("--max-privilege", type=int, default=2,
                          help="the most privilege it may grant a player (0-4, default %(default)s)")
    p_create.add_argument("--days", type=int, default=3650, help="lifetime (default %(default)s)")
    p_create.add_argument("--read-only", action="store_true")
    sub.add_parser("list", help="list service tokens (not the tokens themselves)")
    p_revoke = sub.add_parser("revoke", help="revoke a service's tokens")
    p_revoke.add_argument("service")
    p_revoke.add_argument("--hash-prefix", default="", help="only the token whose hash starts with this")
    args = parser.parse_args(argv)

    db_file = args.db or config_mod.load().db_file
    if not os.path.exists(db_file):
        # Opening would create an empty database, and the token would go into it unseen
        sys.exit(f"No database at {db_file}")
    store = TaskStore.open(db_file)
    service = TaskService(store, config_mod.InstanceConfig())
    try:
        if args.cmd == "create":
            token, expires_at = mint_service_token(service, args.service, args.max_privilege, args.days,
                                                   "read" if args.read_only else "write")
            print(token)
            print(f"service {args.service}, max privilege {max(0, min(4, args.max_privilege))}, "
                  f"expires {_fmt(expires_at)}", file=sys.stderr)
        elif args.cmd == "list":
            tokens = store.service_tokens()
            if not tokens:
                print("No service tokens")
            for t in tokens:
                print(f"{t.service:<20} hash {t.token_hash[:12]}  {t.scope:<5} max privilege "
                      f"{t.max_privilege}  created {_fmt(t.created_at)}  expires {_fmt(t.expires_at)}  "
                      f"last used {_fmt(t.last_used_at)}")
        else:
            count = store.revoke_service_tokens(args.service, args.hash_prefix)
            print(f"Revoked {count} token(s)")
    except UserError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
import json
import asyncio
from pprint import pprint
from lib_py3.lib_k8s import KubernetesManager
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path

async def _list_shards_states_internal(_k8s):
        """Common check for a shard's state for use in the summaries

        Format is
        {
            "valley-2": {
                "status": "starting",
                "reaction": ":arrow_up:",
                "reaction_order": 1,
                "last_change": <integer unix timestamp in seconds>,
            }
        }
        """
        tz = timezone.utc
        shard_states_path = Path('/home/epic/edmund/tmp/') / 'shard_states'
        shard_states_path.mkdir(mode=0o775, parents=True, exist_ok=True)

        previous_states = {}
        for shard_state_path in shard_states_path.iterdir():
            name = shard_state_path.name
            if not (shard_state_path.is_file() and name.endswith('.json')):
                continue
            name = name[:-5] # Remove .json
            previous_shard_state = None
            try:
                previous_shard_state = json.loads(shard_state_path.read_text(encoding='utf-8-sig'))
            except Exception:
                continue
            previous_states[name] = previous_shard_state

        current_states = {}
        shards = await _k8s.list()
        for name, state in shards.items():
            prev_status = previous_states.get(name, {}).get('status', None)
            if state["type"] == "deployment":
                status = 'error'
                reaction = ':exclamation:'
                reaction_order = 99
                if state["replicas"] == 1 and state["available_replicas"] == 1:
                    status = 'started'
                    reaction = ':white_check_mark:'
                    reaction_order = 0
                elif state["replicas"] == 1 and state["available_replicas"] == 0:
                    status = 'starting'
                    reaction = ':arrow_up:'
                    reaction_order = 1
                elif state["replicas"] == 0 and "pod_name" in state:
                    status = 'stopping'
                    reaction = ':arrow_down:'
                    reaction_order = 2
                elif state["replicas"] == 0 and "pod_name" not in state:
                    status = 'stopped'
                    reaction = ':x:'
                    reaction_order = 3

                if status == prev_status:
                    current_states[name] = previous_states[name]
                else:
                    current_state = {
                        "status": status,
                        "reaction": reaction,
                        "reaction_order": reaction_order,
                        "last_change": int(datetime.now(tz).timestamp()),
                    }
                    current_states[name] = current_state
                    shard_state_path = shard_states_path / f'{name}.json'
                    with open(shard_state_path, 'w', encoding='utf-8') as fp:
                        print(
                            json.dumps(
                                current_state,
                                ensure_ascii=False,
                                indent=2,
                                separators=(',', ': ')
                            ),
                            file=fp
                        )
            elif state["type"] == "statefulset":
                for pod in state["pods"]:
                    name, is_ready = pod[0],pod[1]
                    status = 'error'
                    reaction = ':exclamation:'
                    reaction_order = 99
                    if is_ready:
                        status = 'started'
                        reaction = ':white_check_mark:'
                        reaction_order = 0
                    elif not is_ready:
                        status = 'starting'
                        reaction = ':arrow_up:'
                        reaction_order = 1
                    # elif state["replicas"] == 0 and "pod_name" in state:
                    #     status = 'stopping'
                    #     reaction = ':arrow_down:'
                    #     reaction_order = 2
                    # elif state["replicas"] == 0 and "pod_name" not in state:
                    #     status = 'stopped'
                    #     reaction = ':x:'
                    #     reaction_order = 3

                    if status == prev_status:
                        current_states[name] = previous_states[name]
                    else:
                        current_state = {
                            "status": status,
                            "reaction": reaction,
                            "reaction_order": reaction_order,
                            "last_change": int(datetime.now(tz).timestamp()),
                        }
                        current_states[name] = current_state
                        shard_state_path = shard_states_path / f'{name}.json'
                        with open(shard_state_path, 'w', encoding='utf-8') as fp:
                            print(
                                json.dumps(
                                    current_state,
                                    ensure_ascii=False,
                                    indent=2,
                                    separators=(',', ': ')
                                ),
                                file=fp
                            )

        return current_states

@staticmethod
def get_discord_timestamp(datetime_, fmt=":f"):
    '''Get a Discord timestamp code

Available formats are:
""   - Default              - "June 24, 2021 3:49 AM"
":t" - Short time           - "3:49 AM"
":T" - Long Time            - "3:49:19 AM"
":d" - Short date           - "06/24/2021"
":D" - Long Date            - "June 24, 2021"
":f" - Short full (default) - "June 24, 2021 3:49 AM"
":F" - Long Full            - "Thursday, June 24, 2021 3:49 AM"
":R" - Relative             - "2 years ago", "in 5 seconds"

The argument datetime may be a datetime object or a Unix timestamp in seconds (int or float)
'''
    unix_timestamp = datetime_
    if isinstance(datetime_, datetime):
        unix_timestamp = datetime_.timestamp()
    return f"<t:{int(unix_timestamp)}{fmt}>"

async def _get_list_shards_str_status(_k8s):
        """Get a status message formatted string"""
        shards = await _list_shards_states_internal(_k8s)

        buckets = {}
        for name, state in shards.items():
            reaction = state['reaction']
            reaction_order = state['reaction_order']
            last_change = (state['last_change'] // 60) * 60 # Round to the nearest minute

            if reaction_order not in buckets:
                buckets[reaction_order] = {
                    "reaction": reaction,
                    "shards": {},
                }
            bucket_shards = buckets[reaction_order]["shards"]
            if last_change not in bucket_shards:
                bucket_shards[last_change] = []
            bucket_shards[last_change].append(name)

        msg = []
        if len(shards) <= 0:
            msg.append("No shards to list")
        for _, bucket in sorted(buckets.items()):
            formatted_shards = []
            for last_change, shards_at_timestamp in sorted(bucket["shards"].items()):
                last_change_formatted = get_discord_timestamp(last_change, ':R')
                shards_at_timestamp = ', '.join(shards_at_timestamp)
                formatted_shards.append(f'{shards_at_timestamp} ({last_change_formatted})')
            msg.append(f'{bucket["reaction"]}: ' + '; '.join(formatted_shards))

        return "\n".join(msg)

async def _get_list_shards_str_summary(_k8s):
    """Get a `~list shard summary` formatted string"""
    shards = await _list_shards_states_internal(_k8s)

    buckets = {}
    for name, state in shards.items():
        reaction = state['reaction']
        reaction_order = state['reaction_order']

        if reaction_order not in buckets:
            buckets[reaction_order] = {
                "reaction": reaction,
                "shards": [],
            }
        buckets[reaction_order]["shards"].append(name)

    msg = []
    if len(shards) <= 0:
        msg.append("No shards to list")
    for _, bucket in sorted(buckets.items()):
        msg.append(f'{bucket["reaction"]}: ' + ', '.join(bucket["shards"]))

    return "\n".join(msg)

async def _get_list_shards_str_long(_k8s):
    """Get a `~list shard` formatted string"""
    shards = await _list_shards_states_internal(_k8s)
    #print(shards)

    msg = []

    for name, state in shards.items():
        #if state["type"] == "deployment":
        msg.append(f'{state["reaction"]} {name} since {get_discord_timestamp(state["last_change"], ":R")}')
    if not msg:
        msg.append("No shards to list")

    return "\n".join(msg)

async def main():
    k8s = KubernetesManager("volt")
    #pprint(await _get_list_shards_str_status(k8s))
    pprint(await _get_list_shards_str_long(k8s))
    #pprint(await _get_list_shards_str_summary(k8s))

asyncio.run(main())

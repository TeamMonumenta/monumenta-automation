#!/usr/bin/env python3
import asyncio
from pprint import pprint
from lib_py3.shard_manager import ShardManager

NAMESPACE = "volt"
shard_list = ["automation-bot-m17", "ring", "ring-2", "plots", "valley"]

async def main():
    sm = ShardManager(NAMESPACE,"127.0.0.1", 6379, shard_list)

    print("=== get_shard_states ===")
    pprint(await sm.get_shard_states(force_refresh=True))

    print("\n=== scale ===")
    await sm.scale(["valley"], 1)

    print("=== get_shard_states ===")
    pprint(await sm.get_shard_states(force_refresh=True))

    print("=== get_shard_states ===")
    pprint(await sm.get_shard_states(force_refresh=True))

    print("=== get_shard_states ===")
    pprint(await sm.get_shard_states(force_refresh=True))

    print("\n=== scale ===")
    await sm.scale(["valley"], 2)

    print("=== get_shard_states ===")
    pprint(await sm.get_shard_states(force_refresh=True))

    print("\n=== namespace property ===")
    pprint(sm.namespace)

    # Uncomment to test start/stop/restart/scale on specific shards.
    # These modify live state so they are left commented out by default.

    print("\n=== stop valley ===")
    await sm.stop(["valley"])

    print("=== get_shard_states ===")
    pprint(await sm.get_shard_states(force_refresh=True))
    
    print("\n=== start ===")
    try:
        await sm.start(["valley-2"])
    except Exception as e:
        print(f"Expected exception is IllegalStatefulSetOperation: {str(e) }")

    print("=== get_shard_states ===")
    pprint(await sm.get_shard_states(force_refresh=True))

    print("\n=== start ===")
    await sm.start(["valley"])
    
    print("=== get_shard_states ===")
    pprint(await sm.get_shard_states(force_refresh=True))

    print("\n=== restart ===")
    await sm.restart(["valley"])

    print("=== get_shard_states ===")
    pprint(await sm.get_shard_states(force_refresh=True))

    #print("\n=== scale ===")
    #await sm.scale(["valley"], 1)

asyncio.run(main())
#!/usr/bin/env python3
"""Wait for a shard to be fully online according to its heartbeat packets"""


import argparse
import asyncio
from pathlib import Path
import subprocess
import sys
import uuid
from lib_py3.lib_sockets import SocketManager


class HeartbeatWaiter():
    def __init__(self, hostname, shards):
        self._hostname = hostname
        self._rabbitmq_queue_name = f'await-heartbeat-{uuid.uuid4()}'
        self._shards = shards
        self._remaining_shards = set(shards)
        self._future = None
        self._socket = None


    async def run(self):
        self._future = asyncio.get_event_loop().create_future()
        self._socket = SocketManager(self._hostname, self._rabbitmq_queue_name, durable=False, callback=None, server_type="await-heartbeat", track_heartbeats=True)
        while self._remaining_shards:
            await asyncio.sleep(1)
            running_shards = set(self._socket.remote_heartbeats())
            self._remaining_shards.difference_update(running_shards)
        print(f'Done! Now online: {self._shards}')


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('-a', '--address', nargs='?', help="RabbitMQ address; if not specified, namespace and deployment must be specified to look up the address")
    arg_parser.add_argument('-n', '--namespace', nargs='?', help="RabbitMQ namespace")
    arg_parser.add_argument('-d', '--deployment', nargs='?', help="RabbitMQ deployment")
    arg_parser.add_argument('shard', nargs='+')
    args = arg_parser.parse_args()

    # Get RabbitMQ address
    hostname = args.address
    if not hostname:
        utility_code_path = Path(__file__).parent
        get_deployment_addr_path = utility_code_path / 'get_deployment_address.sh'

        get_address_subprocess = subprocess.run([str(get_deployment_addr_path), args.namespace, args.deployment], capture_output=True)
        if get_address_subprocess.returncode:
            sys.exit(f'Could not get RabbitMQ address: {get_address_subprocess.stderr}')
        hostname = get_address_subprocess.stdout.decode(encoding='utf-8').strip()

    # Wait for shards to have active heartbeats
    heartbeat_waiter = HeartbeatWaiter(hostname, args.shard)
    asyncio.run(heartbeat_waiter.run())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

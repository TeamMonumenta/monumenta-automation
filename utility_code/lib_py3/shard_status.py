"""A combined view of each shard's status, from Kubernetes and MonumentaNetworkRelay"""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Optional


@dataclass
class ShardStatus:
    name: str
    # One of 'started', 'starting', 'stopping', 'stopped', or 'error'
    status: str
    reaction: str
    # Order to display statuses in, lowest first
    reaction_order: int
    # Unix timestamp in seconds of the last status change
    last_change: int
    # Players on this shard (including hidden players);
    # None if unknown, ie the shard is not sending heartbeats or players are not being tracked
    player_count: Optional[int] = None


class ShardStatusTracker():
    def __init__(self, k8s, state_dir: Path, socket=None):
        """Tracks the status of shards

        k8s: a KubernetesManager for the shards' namespace
        state_dir: directory to persist the time of each shard's last status change, so it survives restarts
        socket: an optional SocketManager; player counts are included if it tracks remote players
        """
        self._k8s = k8s
        self._state_dir = state_dir
        self._socket = socket


    async def snapshot(self):
        """Get the current status of all shards, as a dict of shard name to ShardStatus"""
        self._state_dir.mkdir(mode=0o775, parents=True, exist_ok=True)

        previous_states = {}
        for shard_state_path in self._state_dir.iterdir():
            name = shard_state_path.name
            if not (shard_state_path.is_file() and name.endswith('.json')):
                continue
            name = name[:-5] # Remove .json
            try:
                previous_states[name] = json.loads(shard_state_path.read_text(encoding='utf-8-sig'))
            except Exception:
                continue

        player_counts = None
        online_servers = set()
        if self._socket is not None:
            player_counts = self._socket.remote_player_counts()
            # Only servers that players can be on; excludes bots and other tools that send heartbeats
            online_servers = {
                server for server, heartbeat_data in self._socket.remote_heartbeats().items()
                if heartbeat_data.get("server-type", "minecraft") in ("minecraft", "proxy")
            }

        result = {}
        shards = await self._k8s.list()
        for name, k8s_state in shards.items():
            status, reaction, reaction_order = self._k8s_status(k8s_state)

            state = previous_states.get(name, None)
            if state is None or state.get('status', None) != status:
                state = {
                    "status": status,
                    "reaction": reaction,
                    "reaction_order": reaction_order,
                    "last_change": int(datetime.now(timezone.utc).timestamp()),
                }
                with open(self._state_dir / f'{name}.json', 'w', encoding='utf-8') as fp:
                    print(
                        json.dumps(
                            state,
                            ensure_ascii=False,
                            indent=2,
                            separators=(',', ': ')
                        ),
                        file=fp
                    )

            player_count = None
            # Relies on each shard's k8s deployment name matching its network relay name
            if player_counts is not None and name in online_servers:
                player_count = player_counts.get(name, 0)

            result[name] = ShardStatus(
                name=name,
                status=state["status"],
                reaction=state["reaction"],
                reaction_order=state["reaction_order"],
                last_change=state["last_change"],
                player_count=player_count,
            )

        return result


    @staticmethod
    def _k8s_status(k8s_state):
        """Returns (status, reaction, reaction_order) for a shard's state from KubernetesManager.list()"""
        if k8s_state["replicas"] == 1 and k8s_state["available_replicas"] == 1:
            return ('started', ':white_check_mark:', 0)
        if k8s_state["replicas"] == 1 and k8s_state["available_replicas"] == 0:
            return ('starting', ':arrow_up:', 1)
        if k8s_state["replicas"] == 0 and "pod_name" in k8s_state:
            return ('stopping', ':arrow_down:', 2)
        if k8s_state["replicas"] == 0 and "pod_name" not in k8s_state:
            return ('stopped', ':x:', 3)
        return ('error', ':exclamation:', 99)

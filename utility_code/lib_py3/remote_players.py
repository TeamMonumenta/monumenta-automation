"""Tracks which players are on which servers, based on MonumentaNetworkRelay's remote player messages

This is a read-only observer of the remote player protocol implemented by network-relay's
RemotePlayerManagerAbstraction. It never has local players of its own, so it only needs to:
- Record "update" messages broadcast by shards/proxies as players join, leave, or change
- Forget all players on a server when that server goes offline
- Ask servers to re-broadcast their players when it starts tracking them (handled by SocketManager)
"""

import threading


class RemotePlayerTracker():
    REMOTE_PLAYER_CHANNEL_BASE = "monumenta.networkrelay.remote_player"
    REMOTE_PLAYER_REFRESH_CHANNEL = REMOTE_PLAYER_CHANNEL_BASE + ".refresh"
    REMOTE_PLAYER_UPDATE_CHANNEL = REMOTE_PLAYER_CHANNEL_BASE + ".update"
    # Matches RemotePlayerManagerAbstraction.REMOTE_PLAYER_MESSAGE_TTL
    REMOTE_PLAYER_MESSAGE_TTL = 5


    def __init__(self):
        self._lock = threading.Lock()
        # {player_uuid: {server_type: server_id}}
        self._players = {}


    def handle_update(self, data):
        """Process the data of a remote_player.update message"""
        server_type = data["serverType"]
        server_id = data["serverId"]
        player_uuid = data["playerUuid"]

        with self._lock:
            player = self._players.setdefault(player_uuid, {})
            if data["isOnline"]:
                player[server_type] = server_id
            # Ignore offline messages from a server the player is no longer on.
            # When a player moves from shard A to shard B, B's "online" can arrive before A's "offline";
            # A's message must not remove the player from B.
            elif player.get(server_type, None) == server_id:
                del player[server_type]

            if not player:
                del self._players[player_uuid]


    def server_offline(self, server_id):
        """Forget all players on a server that went offline"""
        with self._lock:
            for player_uuid, player in list(self._players.items()):
                for server_type, player_server_id in list(player.items()):
                    if player_server_id == server_id:
                        del player[server_type]
                if not player:
                    del self._players[player_uuid]


    def clear(self):
        """Forget all players"""
        with self._lock:
            self._players.clear()


    def player_counts(self):
        """Get the number of players on each server, including hidden players

        Servers without players are not included
        """
        counts = {}
        with self._lock:
            for player in self._players.values():
                for server_id in player.values():
                    counts[server_id] = counts.get(server_id, 0) + 1
        return counts

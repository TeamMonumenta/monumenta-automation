from datetime import datetime
from datetime import timedelta
from pprint import pformat
from concurrent.futures import ThreadPoolExecutor
import asyncio
import copy
import json
import logging
import threading
import traceback
import pika
from lib_py3.remote_players import RemotePlayerTracker
from lib_py3.shard_health import ShardHealth

logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)

class SocketManager():
    """A manager for RabbitMQ sockets

    Call close() when done with it, or use it as a context manager (`with` / `async with`) to do so automatically.
    Long-lived instances that are used for the life of the process do not need to be closed.
    """
    BROADCAST_EXCHANGE_NAME = "broadcast"
    HEARTBEAT_CHANNEL = "monumentanetworkrelay.heartbeat"


    # Default log level is INFO
    def __init__(
        self,
        rabbit_host,
        queue_name,
        durable=False,
        callback=None,
        log_level=20,
        server_type="bot",
        track_heartbeats=False,
        track_remote_players=False
    ):
        """SocketManager constructor:

        rabbit_host: the address of the RabbitMQ server to connect to
        queue_name: the name of the queue to use for this connection
        durable: whether or not the queue for this socket should persist for a while after the connection is lost
        callback: a method that accepts a `message` dictionary as transmitted via json;
                  see the MonumentaNetworkRelay source code
        log_level: the log level to use for this SocketManager as defined by the `logging` Python library
        server_type: the server type to advertise to other servers using MonumentaNetworkRelay; used for broadcasting commands
        track_heartbeats: if True, keeps track of the last heartbeat from each online server
        track_remote_players: if True, keeps track of which players are on which servers; implies track_heartbeats
        """
        # Used only for sending packets to RabbitMQ - receiving will open its own connection
        # pika connections are not thread safe, so all use of these must hold _send_lock
        self._send_lock = threading.Lock()
        self._connection = None
        self._channel = None

        self._queue_name = queue_name
        self._callback = callback
        self._rabbit_host = rabbit_host
        self._durable_queue = durable
        self._server_type = server_type
        self._heartbeat_threshhold = datetime.min
        # Remote player tracking relies on heartbeats to know when a server's players should be forgotten
        self._track_heartbeats = track_heartbeats or track_remote_players

        self._remote_heartbeats_lock = threading.Lock()
        self._remote_heartbeats = {}

        self._remote_players = None
        # Refresh requests are sent from here, not the consumer thread, so a slow send can't stall receiving messages
        self._refresh_executor = None
        if track_remote_players:
            self._remote_players = RemotePlayerTracker()
            # Servers that have been asked to re-broadcast their players; only used by the consumer thread
            self._remote_player_servers = set()
            self._refresh_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"{queue_name}-player-refresh")

        # Set by close() to stop the consumer thread and reject further sends
        self._closed = threading.Event()
        self.thread = None

        logger.setLevel(log_level)

        # Create a thread to connect to the queue and block / consume messages
        if callback is not None or self._track_heartbeats:
            self.thread = threading.Thread(target=self._subscriber)
            self.thread.daemon = True
            self.thread.start()


    def _subscriber(self):
        def callback(channel, method_frame, header_frame, body):
            try:
                dec = json.JSONDecoder()
                message = dec.decode(body.decode('utf8'))

                logger.debug("Got packet: %s", pformat(message))

                if self._track_heartbeats:
                    now = datetime.utcnow()
                    # Servers that stopped sending heartbeats, as of this message
                    went_offline = []

                    try:
                        heartbeat_source = message.get("source", None)
                        heartbeat_data = message.get("pluginData", {}).get("monumentanetworkrelay", None)
                        if heartbeat_source is None:
                            pass
                        elif message.get("online", None) is False:
                            # Server is shutting down. Network relay's shutdown message has no pluginData, so don't require it.
                            with self._remote_heartbeats_lock:
                                if heartbeat_source in self._remote_heartbeats:
                                    del self._remote_heartbeats[heartbeat_source]
                                    went_offline.append(heartbeat_source)
                        elif heartbeat_data is not None and message.get("online", False):
                            remote_heartbeat_entry = {
                                "last_heartbeat": now,
                                "heartbeat_data": heartbeat_data,
                            }
                            with self._remote_heartbeats_lock:
                                self._remote_heartbeats[heartbeat_source] = remote_heartbeat_entry
                    except Exception:
                        logger.warning("Failed to process remote heartbeat in message: %s", repr(body))
                        logger.warning(traceback.format_exc())

                    try:
                        expiry_time = now - timedelta(seconds=10)

                        with self._remote_heartbeats_lock:
                            for source, full_heartbeat_data in list(self._remote_heartbeats.items()):
                                if expiry_time >= full_heartbeat_data["last_heartbeat"]:
                                    del self._remote_heartbeats[source]
                                    went_offline.append(source)
                    except Exception:
                        logger.warning("Failed to remove outdated remote heartbeats: %s", repr(body))
                        logger.warning(traceback.format_exc())

                    if self._remote_players is not None:
                        self._update_remote_player_servers(went_offline)

                if self._remote_players is not None and message.get("channel", None) == RemotePlayerTracker.REMOTE_PLAYER_UPDATE_CHANNEL:
                    try:
                        self._remote_players.handle_update(message["data"])
                    except Exception:
                        logger.warning("Failed to process remote player update: %s", repr(body))
                        logger.warning(traceback.format_exc())

                if self._callback is not None:
                    self._callback(message)

            except Exception:
                logger.warning("Failed to process rabbitmq message: %r", body)
                logger.warning(traceback.format_exc())

            channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        has_connected = False
        while not self._closed.is_set():
            connection = None
            channel = None
            try:
                # Create the connection
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._rabbit_host))
                channel = connection.channel()

                # close() may have been called while connecting
                if self._closed.is_set():
                    break

                # Create the exchange for broadcast messages
                logger.debug("Declaring exchange %s", self.BROADCAST_EXCHANGE_NAME)
                channel.exchange_declare(self.BROADCAST_EXCHANGE_NAME, exchange_type="fanout")

                # Declare the queue
                # x-expires: delete the queue when no consumers are connected to it for 20 minutes
                logger.debug("Declaring queue %s", self._queue_name)
                channel.queue_declare(queue=self._queue_name, durable=self._durable_queue, arguments={'x-expires': 1200000})

                # Bind queue to the exchange
                logger.debug("Binding queue %s to exchange %s", self._queue_name, self.BROADCAST_EXCHANGE_NAME)
                channel.queue_bind(self._queue_name, self.BROADCAST_EXCHANGE_NAME, routing_key="")

                ## Start consuming messages
                logger.info("Started rabbitmq message consumer for queue %s", self._queue_name)
                channel.basic_consume(queue=self._queue_name, on_message_callback=callback)

                if has_connected and self._remote_players is not None:
                    # Player updates may have been missed while disconnected, including players going offline,
                    # which a refresh alone would never correct. Start over: each server is asked for its players
                    # again on its next heartbeat, which also confirms it is reachable again.
                    self._remote_players.clear()
                    self._remote_player_servers.clear()
                has_connected = True

                # Equivalent to channel.start_consuming(), but checks periodically whether close() was called.
                # consumer_tags becomes empty if the broker cancels the consumer (e.g. the queue was deleted).
                while channel.consumer_tags and not self._closed.is_set():
                    connection.process_data_events(time_limit=1)

                # pika logs the broker's reason when it closes the channel
                if channel.is_closed:
                    raise ConnectionError(f"Rabbitmq consumer channel for queue {self._queue_name} was closed")
                if not self._closed.is_set():
                    logger.warning("Rabbitmq consumer for queue %s was cancelled", self._queue_name)
            except Exception as e:
                logger.warning("Rabbitmq consumer thread failed: %s", e)
                logger.warning(traceback.format_exc())
            finally:
                # Always clean up, however consuming ended, so connections aren't leaked across reconnects.
                # Closing the connection also cancels the consumer and closes the channel.
                # Failures here must not escape, or they would kill this thread and stop reconnecting.
                try:
                    if connection is not None and connection.is_open:
                        connection.close()
                except Exception:
                    pass

            if self._closed.is_set():
                break
            logger.warning("Attempting to reconnect rabbitmq consumer...")
            # Wait before reconnecting, but wake up immediately if close() is called
            self._closed.wait(10)


    def _update_remote_player_servers(self, went_offline):
        """Keeps remote player tracking in sync with which servers are online

        Called from the consumer thread for every message. Mirrors RemotePlayerManagerAbstraction's
        registerServer/unregisterServer.
        """
        for source in went_offline:
            self._remote_players.server_offline(source)
            self._remote_player_servers.discard(source)

        # Ask servers that are newly sending heartbeats to re-broadcast all of their players.
        # On startup, this is how the initial player list is built.
        with self._remote_heartbeats_lock:
            targets = [
                source for source, full_heartbeat_data in self._remote_heartbeats.items()
                if source not in self._remote_player_servers
                and full_heartbeat_data["heartbeat_data"].get("server-type", "minecraft") in ("minecraft", "proxy")
            ]
        self._remote_player_servers.update(targets)

        # Sent from another thread, so a slow send can't stall receiving messages
        if targets and not self._closed.is_set():
            self._refresh_executor.submit(self._send_refresh_requests, targets)


    def _send_refresh_requests(self, targets):
        for target in targets:
            try:
                self.send_packet(target, RemotePlayerTracker.REMOTE_PLAYER_REFRESH_CHANNEL, {"uuid": "*"},
                                 ttl_seconds=RemotePlayerTracker.REMOTE_PLAYER_MESSAGE_TTL)
            except Exception:
                logger.warning("Failed to request remote players from %s", target)
                logger.warning(traceback.format_exc())


    def _ensure_channel_open_for_sending(self):
        """Opens a connection and channel if one doesn't exist or it was closed, reuse channel otherwise

        Must be called with _send_lock held.
        """
        if self._connection is None or self._connection.is_closed:
            self._channel = None
            self._connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=self._rabbit_host,
                # Fail fast rather than blocking the caller for a long time if rabbitmq is unavailable
                # (socket_timeout / stack_timeout only cover establishing the connection)
                connection_attempts=1,
                socket_timeout=5,
                stack_timeout=10,
                # Give up if the broker is refusing publishes (memory/disk alarm) rather than blocking forever
                blocked_connection_timeout=10,
            ))

        if self._channel is None or self._channel.is_closed:
            channel = self._connection.channel()

            # Publisher confirms make basic_publish wait for the broker to accept the message,
            # so errors (lost connection, missing exchange, etc.) are raised by the send that caused them
            # rather than surfacing later on an unrelated send. Note that a message sent directly to a
            # queue that doesn't exist is still accepted and silently dropped, as before.
            channel.confirm_delivery()

            # The exchange is not durable, so it disappears whenever rabbitmq restarts.
            # Re-declare it here so sending does not depend on the consumer thread having done so.
            channel.exchange_declare(self.BROADCAST_EXCHANGE_NAME, exchange_type="fanout")

            self._channel = channel

        return self._channel


    def _reset_sending_connection(self):
        """Discards the sending connection so the next send opens a fresh one

        Must be called with _send_lock held.
        """
        connection = self._connection
        self._connection = None
        self._channel = None
        if connection is not None and connection.is_open:
            try:
                connection.close()
            except Exception:
                pass


    def close(self):
        """Closes this SocketManager's connections and stops its consumer thread, if any

        After this, sending raises an exception. Calling close() more than once is harmless.
        This blocks briefly while connections shut down; use close_async() from async code.
        """
        self._closed.set()

        # The consumer thread notices within a second (or once it finishes connecting), then cleans up its connection
        if self.thread is not None and self.thread is not threading.current_thread():
            self.thread.join(timeout=15)
            if self.thread.is_alive():
                logger.warning("Rabbitmq consumer thread for queue %s did not stop within 15 seconds of close()", self._queue_name)

        # Pending refresh requests would fail anyway, since sending is rejected after close()
        if self._refresh_executor is not None:
            self._refresh_executor.shutdown(wait=False, cancel_futures=True)

        with self._send_lock:
            self._reset_sending_connection()


    async def close_async(self):
        """Same as close(), but runs in a worker thread so it does not block the asyncio event loop"""
        await asyncio.to_thread(self.close)


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


    async def __aenter__(self):
        return self


    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        await self.close_async()


    def send_heartbeat(self):
        """Sends a heartbeat packet, assuming no other data needs to be sent at the moment.

        This does not need to be called when regularly sending data faster than the heartbeat interval.
        """
        self.send_packet("*", self.HEARTBEAT_CHANNEL, {})


    async def send_heartbeat_async(self):
        """Same as send_heartbeat(), but runs in a worker thread so it does not block the asyncio event loop"""
        await self.send_packet_async("*", self.HEARTBEAT_CHANNEL, {})


    def remote_heartbeats(self):
        """Get heartbeat information about all remote servers"""
        result = {}
        with self._remote_heartbeats_lock:
            for source, full_heartbeat_data in self._remote_heartbeats.items():
                result[source] = copy.deepcopy(full_heartbeat_data.get("heartbeat_data", None))
        return result


    def remote_heartbeat(self, source):
        """Get the full remote heartbeat data for a server"""
        with self._remote_heartbeats_lock:
            return copy.deepcopy(self._remote_heartbeats.get(source, {}).get("heartbeat_data", None))


    def shard_type(self, source):
        """Get the type of a remote server

        Expected values include, but are not limited to, "minecraft", "proxy", and "bot"
        """
        with self._remote_heartbeats_lock:
            return copy.deepcopy(self._remote_heartbeats.get(source, {}).get("heartbeat_data", {}).get("server-type", "minecraft"))


    def remote_player_counts(self):
        """Get the number of players (including hidden players) on each server

        Servers without players are not included. Returns None if this SocketManager does not track remote players.
        """
        if self._remote_players is None:
            return None
        return self._remote_players.player_counts()


    def shard_health_data(self, source):
        """Get the health data for a remote server"""
        json_data = None
        with self._remote_heartbeats_lock:
            json_data = self._remote_heartbeats.get(source, {}).get("heartbeat_data", {}).get("shard_health", None)
        if json_data:
            return ShardHealth(copy.deepcopy(json_data))
        return ShardHealth.zero_health()


    def send_packet(self, destination, operation, data, heartbeat_data=None, online=True, ttl_seconds=None):
        """Sends a json packet over RabbitMQ

        destination is the server to target, or * for all servers
        operation specifies what channel should listen for this packet
        data is json data to be processed
        heartbeat_data, if specified, includes information about the sending server
        online, if set to False, specifies the sending server is shutting down
        ttl_seconds, if specified, discards the message if it is not received within that many seconds
        """
        if destination is None or len(destination) == 0:
            logger.warning("destination can not be None!")
        if operation is None or len(operation) == 0:
            logger.warning("operation can not be None!")
        if data is None:
            logger.warning("data can not be None!")
        if heartbeat_data is None:
            heartbeat_data = {}

        packet = {
            "data": data,
            "source": self._queue_name,
            "dest": destination,
            "channel": operation,
        }

        now = datetime.utcnow()
        if operation == self.HEARTBEAT_CHANNEL or (
                now >= self._heartbeat_threshhold
                and destination == "*"
        ):
            self._heartbeat_threshhold = now + timedelta(seconds=0.5)

            network_relay_data = heartbeat_data.get("monumentanetworkrelay", None)
            if network_relay_data is None:
                network_relay_data = {}
                heartbeat_data["monumentanetworkrelay"] = network_relay_data
            heartbeat_data["monumentanetworkrelay"] = network_relay_data

            network_relay_data["server-type"] = self._server_type

            packet["pluginData"] = heartbeat_data
            packet["online"] = online

        encoded = json.dumps(packet, ensure_ascii=False).encode("utf-8")
        logger.debug("Sending Packet: %s", pformat(encoded))

        exchange = ''
        routing_key = destination
        if destination == "*":
            exchange = 'broadcast'
            routing_key = ''

        with self._send_lock:
            if self._closed.is_set():
                raise ConnectionError(f"Cannot send rabbitmq message, SocketManager for queue {self._queue_name} is closed")

            # If the existing connection has gone bad (rabbitmq restarted, idle connection timed out, etc.),
            # throw it away and try once more with a fresh one before giving up
            for attempt in range(2):
                try:
                    channel = self._ensure_channel_open_for_sending()
                    channel.basic_publish(
                        exchange=exchange,
                        routing_key=routing_key,
                        body=encoded,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # make message persistent
                            expiration=(str(int(ttl_seconds * 1000)) if ttl_seconds is not None else None),
                        )
                    )
                    return
                except Exception as e:
                    self._reset_sending_connection()
                    if attempt > 0:
                        raise
                    logger.info("Failed to send rabbitmq message, reconnecting: %r", e)


    async def send_packet_async(self, destination, operation, data, heartbeat_data=None, online=True, ttl_seconds=None):
        """Same as send_packet(), but runs in a worker thread so it does not block the asyncio event loop

        Still waits for the message to be sent (or fail) before returning, raising the same exceptions as send_packet()
        """
        await asyncio.to_thread(self.send_packet, destination, operation, data, heartbeat_data=heartbeat_data, online=online, ttl_seconds=ttl_seconds)

from datetime import datetime
from datetime import timedelta
from pprint import pformat
import json
import logging
import threading
import time
import traceback
import pika

logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)

class SocketManager():
    BROADCAST_EXCHANGE_NAME = "broadcast"
    HEARTBEAT_CHANNEL = "monumentanetworkrelay.heartbeat"

    # Default log level is INFO
    def __init__(self, rabbit_host, queue_name, durable=False, callback=None, log_level=20, server_type="bot"):
        # Used only for sending packets to RabbitMQ - receiving will open its own connection
        self._connection = None
        self._channel = None

        self._queue_name = queue_name
        self._callback = callback
        self._rabbit_host = rabbit_host
        self._durable_queue = durable
        self._server_type = server_type
        self._heartbeat_threshhold = datetime.min
        logger.setLevel(log_level)

        # Create a thread to connect to the queue and block / consume messages
        if callback is not None:
            self.thread = threading.Thread(target=self._subscriber)
            self.thread.daemon = True
            self.thread.start()

    def _subscriber(self):
        def callback(channel, method_frame, header_frame, body):
            try:
                dec = json.JSONDecoder()
                obj = dec.decode(body.decode('utf8'))

                logger.debug("Got packet: %s", pformat(obj))
                if self._callback is not None:
                    self._callback(obj)

            except Exception:
                logger.warning("Failed to process rabbitmq message: %r", body)
                logger.warning(traceback.format_exc())

            channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        while True:
            connection = None
            channel = None
            try:
                # Create the connection
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._rabbit_host))
                channel = connection.channel()

                # Create the exchange for broadcast messages
                logger.debug("Declaring exchange %s", self.BROADCAST_EXCHANGE_NAME)
                channel.exchange_declare(self.BROADCAST_EXCHANGE_NAME, exchange_type="fanout")

                # Declare the queue
                logger.debug("Declaring queue %s", self._queue_name)
                channel.queue_declare(queue=self._queue_name, durable=self._durable_queue)

                # Bind queue to the exchange
                logger.debug("Binding queue %s to exchange %s", self._queue_name, self.BROADCAST_EXCHANGE_NAME)
                channel.queue_bind(self._queue_name, self.BROADCAST_EXCHANGE_NAME, routing_key="")

                ## Start consuming messages
                logger.info("Started rabbitmq message consumer for queue %s", self._queue_name)
                channel.basic_consume(queue=self._queue_name, on_message_callback=callback)
                channel.start_consuming()
            except Exception as e:
                logger.warning("Rabbitmq consumer thread failed: %s", e)
                logger.warning(traceback.format_exc())

                if channel is not None and channel.is_open:
                    channel.close()
                if connection is not None and connection.is_open:
                    connection.close()

            logger.warning("Attempting to reconnect rabbitmq consumer...")
            time.sleep(10)

    def _ensure_channel_open_for_sending(self):
        '''
        Opens a connection and channel if one doesn't exist or it timed out, reuse channel otherwise
        '''
        if self._connection is None or self._connection.is_closed:
            self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._rabbit_host))

        if self._channel is None or self._channel.is_closed:
            self._channel = self._connection.channel()

        if self._channel.is_closed:
            raise ConnectionError("Failed to send message to rabbitmq despite attempting to reconnect")

        return self._channel


    def send_heartbeat(self):
        self.send_packet("*", self.HEARTBEAT_CHANNEL, {})

    def send_packet(self, destination, operation, data, heartbeat_data={}, online=True):
        if destination is None or len(destination) == 0:
            logger.warning("destination can not be None!")
        if operation is None or len(operation) == 0:
            logger.warning("operation can not be None!")
        if data is None:
            logger.warning("data can not be None!")

        channel = self._ensure_channel_open_for_sending()

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

            network_relay_data = heartbeat_data.get("monumentanetworkrelay", {})
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

        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=encoded,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )

        channel.close()

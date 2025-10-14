from pprint import pformat
import json
import logging
import threading
import traceback
import time
from datetime import datetime
from datetime import timedelta
import pika

logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)


class SocketManager():
    BROADCAST_EXCHANGE_NAME = "broadcast"
    HEARTBEAT_CHANNEL = "monumentanetworkrelay.heartbeat"


    # Default log level is INFO
    def __init__(self, rabbit_host, queue_name, durable=False, callback=None, log_level=20, server_type="bot"):
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
                logger.warning("Failed to process rabbitmq message: %s", repr(body))
                logger.warning(traceback.format_exc())

            channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        while True:
            try:
                # Create the connection
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._rabbit_host))
                channel = connection.channel()

                # Create the exchange for broadcast messages
                logger.debug("Declaring exchange %s", repr(self.BROADCAST_EXCHANGE_NAME))
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
                logger.warning('Rabbitmq consumer thread failed: %s', e)
                logger.warning(traceback.format_exc())

            logger.warning('Attempting to reconnect rabbitmq consumer...')
            time.sleep(10)


    def send_heartbeat(self):
        self.send_packet("*", self.HEARTBEAT_CHANNEL, {})


    def send_packet(self, destination, operation, data, heartbeat_data=None, online=True):
        if destination is None or len(destination) == 0:
            logger.warning("destination can not be None!")
        if operation is None or len(operation) == 0:
            logger.warning("operation can not be None!")
        if data is None:
            logger.warning("data can not be None!")
        if heartbeat_data is None:
            heartbeat_data = {}

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._rabbit_host))
        channel = connection.channel()

        if channel.is_closed:
            raise Exception("Failed to send message to rabbitmq despite attempting to reconnect")

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

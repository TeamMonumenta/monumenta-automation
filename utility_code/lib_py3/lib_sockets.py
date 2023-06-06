from pprint import pformat
import json
import logging
import threading
import pika
import traceback
import time

logger = logging.getLogger(__name__)

class SocketManager(object):
    # Default log level is INFO
    def __init__(self, rabbit_host, queue_name, durable=False, callback=None, log_level=20):
        self._queue_name = queue_name
        self._callback = callback
        self._rabbit_host = rabbit_host
        self._durable_queue = durable
        logger.setLevel(log_level);

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

                logger.debug("Got packet: {}".format(pformat(obj)))
                if self._callback is not None:
                    self._callback(obj)

            except Exception as e:
                logger.warn("Failed to process rabbitmq message: {!r}".format(body))
                logger.warn(traceback.format_exc())

            channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        while True:
            try:
                # Create the connection and declare the queue
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._rabbit_host))
                channel = connection.channel()
                logger.debug("Declaring queue {}".format(self._queue_name))
                channel.queue_declare(queue=self._queue_name, durable=self._durable_queue)

                ## Start consuming messages
                logger.info("Started rabbitmq message consumer for queue {}".format(self._queue_name))
                channel.basic_consume(queue=self._queue_name, on_message_callback=callback)
                channel.start_consuming()
            except Exception as e:
                logger.warn('Rabbitmq consumer thread failed: {}'.format(e))
                logger.warn(traceback.format_exc())

            logger.warn('Attempting to reconnect rabbitmq consumer...')
            time.sleep(10)

    def send_packet(self, destination, operation, data, heartbeat_data=None, online=None):
        if destination is None or len(destination) == 0:
            logger.warn("destination can not be None!")
        if operation is None or len(operation) == 0:
            logger.warn("operation can not be None!")
        if data is None or len(data) == 0:
            logger.warn("data can not be None!")

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._rabbit_host))
        channel = connection.channel()

        if channel.is_closed:
            raise Exception("Failed to send message to rabbitmq despite attempting to reconnect")

        packet = {}
        packet["source"] = self._queue_name
        packet["dest"] = destination
        packet["channel"] = operation
        packet["data"] = data
        if heartbeat_data is not None:
            packet["pluginData"] = heartbeat_data
        if online is not None:
            packet["online"] = online

        encoded = json.dumps(packet, ensure_ascii=False).encode("utf-8")
        logger.debug("Sending Packet: {}".format(pformat(encoded)))

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

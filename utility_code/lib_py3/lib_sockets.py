#!/usr/bin/env python3

from pprint import pformat
import time
import json
import socket
import logging
import threading

logger = logging.getLogger(__name__)

class SocketManager(object):
    # Default log level is INFO
    def __init__(self, host, port, name, callback=None, log_level=20):
        self.name = name
        self.callback = callback
        self.address = (host, port)
        logger.setLevel(log_level);

        # Create a thread to connect to the socket
        self.thread = threading.Thread(target=self._connect)
        self.thread.daemon = True
        self.thread.start()

        self.heart = None
        self.heart_stop_flag = False

    def _connect(self):
        logger.debug("Connect: starting")
        timeouts = 0
        while True:
            logger.debug("Connect: looping")
            try:
                # Create a new socket with a timeout of 90 seconds
                # The socket will send (and should receive back) a heartbeat every 60 seconds
                self.socket = socket.create_connection(self.address, 90)
                # Connection Successful
                timeouts = 0
                # Say Hello to Bungee
                # If this connection should be named, tell Bungee the name
                if self.name is not None:
                    self.send_packet(None, "Monumenta.Bungee.Handshake", {"name": self.name})

                # Create a thread to send a heartbeat to the socket every minute
                self.heart_stop_flag = False
                self.heart = threading.Thread(target=self._heartbeat)
                self.heart.daemon = True
                self.heart.start()

                # Start listening
                self._listen()
            except Exception as e:
                logger.warning("Socket Connection Error: {}".format(pformat(e)))

            # There was an error in either the connection or the listener

            # Forcibly close the socket, just in case it's somehow still open
            self.socket.close()

            if self.heart is not None:
                self.heart_stop_flag = True
                self.heart.join()


            # Add a delay then try to connect again
            timeouts += 1
            time.sleep(min(timeouts, 5)*2)
        logger.debug("Connect: exiting")

    def _listen(self):
        dec = json.JSONDecoder()
        raw = u''

        logger.debug("Listener: starting")
        while True:
            logger.debug("Listener: looping")
            try:
                # Read the next message whenever it is received
                # If this takes longer than 90 seconds, assume the connection was closed and reconnect

                raw = raw + self.socket.recv(4096).decode("utf-8")

                if not raw:
                    logger.warning("Socket read 0 bytes - this socket is dead. Aborting listener")
                    return

                while raw:
                    try:
                        obj, i = dec.raw_decode(raw)
                        raw = raw[i:]

                        logger.debug("Got packet: {}".format(pformat(obj)))
                        if self.callback is not None:
                            self.callback(obj)

                    except json.decoder.JSONDecodeError:
                        logger.debug("Failed to decode packet fragment: '{}'".format(raw))
                        break

            except Exception as e:
                logger.warning("Socket Read Error: {}".format(pformat(e)))
                return
        logger.debug("Listener: exiting")

    def _heartbeat(self, interval = 60, retry = 5):
        logger.debug("Heartbeat: starting")
        while not self.heart_stop_flag:
            logger.debug("Heartbeat: looping")
            try:
                self.send_packet(None, "Monumenta.Bungee.Heartbeat", None)
            except Exception as e:
                logger.debug("Heartbeat: got error, short sleep to retry")
                time.sleep(retry)
                continue
            time.sleep(interval)
        logger.debug("Heartbeat: exiting")


    def send_packet(self, destination, operation, data):
        packet = {}
        if destination is not None:
                packet["dest"] = destination
        if operation is not None:
                packet["op"] = operation
        if data is not None:
                packet["data"] = data
        raw = json.dumps(packet, ensure_ascii=False)
        encoded = raw.encode("utf-8")
        logger.debug("Sending Packet: {}".format(pformat(encoded)))

        # TODO: Block until socket has been initialized (or timeout occurs)

        self.socket.send(encoded)


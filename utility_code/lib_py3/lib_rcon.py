#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../MCRcon"))

import socket
import mcrcon

def rcon_command(host, port, password, cmd):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    try:
        # Log in
        result = mcrcon.login(sock, password)
        if not result:
            raise Exception("Incorrect rcon password")

        # Run command, return result
        return mcrcon.command(sock, cmd)
    finally:
        sock.close()

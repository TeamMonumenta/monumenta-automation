#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

#
# Shell-scripting routines which can be combined to make discord command scripts
#

import datetime
import asyncio
#import traceback
import subprocess
import os
import sys

################################################################################
# Utility Functions

def datestr():
    return datetime.datetime.now().strftime("%Y_%m_%d")

def split_string(text):
    # Maximum number of characters in a single line
    n = 1950

    splits = text.splitlines()
    result = []
    cur = None
    for i in splits:
        while True:
            if cur is None and len(i) <= n:
                cur = i;
                break # Done with i
            elif cur is None and len(i) > n:
                # Annoying case - one uber long line. Have to split into chunks
                result = result + [i[:n]]
                i = i[n:]
                pass # Repeat this iteration
            elif len(cur) + len(i) < n:
                cur = cur + "\n" + i
                break # Done with i
            else:
                result = result + [cur]
                cur = None
                pass # Repeat this iteration

    if cur is not None:
        result = result + [cur]
        cur = None

    return result

class ShellAction(object):
    ################################################################################
    # These methods should be implemented by the user

    def __init__(self, debug=False):
        self._debug = debug
        self._lock = False

        # Implementor should populate these fields:
        #self._commands = []

    async def hasPermissions(self, author):
        raise NotImplementedError("Implement Me")

    alwaysListening = False

    ################################################################################
    # These methods should be left alone

    async def sleep(self, seconds):
        await self.display("Sleeping for " + str(seconds) + " seconds")
        await asyncio.sleep(seconds)

    # TODO - make sure this raises an error if the directory doesn't exist
    async def cd(self, path):
        if self._debug:
            await self.display("Changing path to `" + path + "`")
        os.chdir(path)

    async def exit(self):
        sys.exit(1)

    async def run(self, cmd, ret=0, displayOutput=False):
        splitCmd = cmd.split(' ')
        if self._debug:
            await self.display("Executing: ```" + str(splitCmd) + "```")
        process = await asyncio.create_subprocess_exec(*splitCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        rc = process.returncode

        if self._debug:
            await self.display("Result: {}".format(rc))

        stdout = stdout.decode('utf-8')
        if stdout:
            if self._debug:
                await self.display("stdout from command '{}':".format(cmd))

            if self._debug or displayOutput:
                await self.displayVerbatim(stdout)

        stderr = stderr.decode('utf-8')
        if stderr:
            await self.display("stderr from command '{}':".format(cmd))
            await self.displayVerbatim(stderr)
            # TODO: Remove likely
            #if ret != None and ret == 0:
                #raise ValueError("Got unexpected stderr while processing '{}'".format(cmd))

        if ret != None and rc != ret:
            raise ValueError("Expected result {}, got result {} while processing '{}'".format(ret, rc, cmd))

        return stdout

    async def displayVerbatim(self, text):
        for chunk in split_string(text):
            await self.display("```" + chunk + "```")

    async def display(self, debuginfo):
        await self._channel.send(debuginfo)

    async def mention(self):
        await self._channel.send(self._author.mention)

    async def doActions(self, client, channel, author):
        self._client = client
        self._channel = channel
        self._author = author

        if self._lock:
            await self.display('Error: action ' + self.command + ' is already being performed')
            return
        else:
            if not self.alwaysListening:
                # Always listening commands are usually one-line near-instant output commands; easier to follow without clutter.
                await self.display('Performing action: ' + self.command)

        self._lock = True

        try:
            for item in self._commands:
                await item
        except Exception as e:
            await self.mention()
            await self._channel.send("**ERROR**: ```" + str(e) + "```")

        self._lock = False

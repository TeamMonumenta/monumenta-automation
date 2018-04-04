#
# Shell-scripting routines which can be combined to make discord command scripts
#

import datetime
import asyncio
#import traceback
import subprocess
import os

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

class Shell(object):
    def __init__(self, client, debug=False):
        self._client = client
        self._debug = debug

    async def sleep(self, seconds):
        await display("Sleeping for " + str(seconds) + " seconds")
        await asyncio.sleep(seconds)

    async def cd(self, path):
        if extraDebug:
            await display("Changing path to `" + path + "`")
        os.chdir(path)

    async def run(self, cmd, ret=0):
        splitCmd = cmd.split(' ')
        if extraDebug:
            await display("Executing: ```" + str(splitCmd) + "```")
        process = await asyncio.create_subprocess_exec(*splitCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        rc = process.returncode

        if extraDebug:
            stdout = stdout.decode('utf-8')
            await display("Result: {}".format(rc))
            if stdout:
                await display("stdout from command '{}':".format(cmd))
                await display_verbatim(stdout)

        stderr = stderr.decode('utf-8')
        if stderr:
            await display("stderr from command '{}':".format(cmd))
            await display_verbatim(stderr)
            # TODO: Remove likely
            #if ret != None and ret == 0:
                #raise ValueError("Got unexpected stderr while processing '{}'".format(cmd))

        if ret != None and rc != ret:
            raise ValueError("Expected result {}, got result {} while processing '{}'".format(ret, rc, cmd))

    async def display_verbatim(self, text):
        for chunk in split_string(text):
            await display("```" + chunk + "```")

    async def display(self, debuginfo):
        await self._client.send_message(self._channel, debuginfo)

    async def do_actions(self, channel, actions):
        self._channel = channel

        try:
            for item in actions:
                await item
        except Exception as e:
            await self._client.send_message(self._channel, "**ERROR**: ```" + str(e) + "```")

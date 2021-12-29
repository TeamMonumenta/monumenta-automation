#!/usr/bin/env pypy3

import os
import sys
import string
from pprint import pprint

def translate(s):
    remove = string.punctuation + string.whitespace + string.digits
    mapping = str.maketrans(dict.fromkeys(remove))
    return s.translate(mapping)

def compare(s1, s2):
    return translate(s1) == translate(s2)

def store_result(time, severity, contents):
    for ignore in whitelist_ignore:
        if ignore in contents:
            return

    key = translate(contents)
    if "WARN" in severity or "ERROR" in severity:
        if severity not in error_map:
            error_map[severity] = {}

        if key not in error_map[severity]:
            error_map[severity][key] = (contents, 1)
        else:
            error_map[severity][key] = (contents, error_map[severity][key][1] + 1)

if __name__ == '__main__':
    #
    # {
    #   "INFO": {
    #     "Giant error message": 5
    #   }
    #   "WARN": ...
    #
    error_map = {}

    whitelist_ignore = [
        "Establishing SSL connection without",
        "moved too quickly!",
        "Unknown function monumenta:on_offhand",
        "Server thread dump (Look for plugins here before reporting to Paper!)",
        "DO NOT REPORT THIS TO PAPER - THIS IS NOT A BUG OR A CRASH",
        "com.boydti.fawe.bukkit.v1_13.BukkitQueue_1_13.getCachedSection",
        "Something went wrong upgrading!",
        "it doesn't exist anymore?",
        "No operations allowed after connection closed.). Possibly consider using a shorter maxLifetime",
        "com.mojang.authlib.exceptions.Authentication",
        "moved wrongly!",
        " was kicked due to keepalive timeout!",
        " was kicked for floating too long!",
        "Skipping BlockEntity with id",
        "Could not pass event AsyncPlayerChatEvent to VentureChat",
        "org.sqlite.SQLiteException",
        "Wrong location! (",
        "com.djrapitops.plan.storage.database.MySQLDB",
        "Bukkit will attempt to fix this, but there may be additional damage that we cannot recover",
        " Unknown or incomplete command, see below for error at",
        "command denied to user 'lp_readonly'",
        "com.boydti.fawe.bukkit.util.JavaVersionCheck",
        "io.papermc.paper.util.PaperJvmChecker",
        "mineverse.Aust1n46.chat.MineverseChat.onPluginMessageReceived",
        "SERVER IS RUNNING IN OFFLINE/INSECURE MODE",
        "if they are not new, this is a serious error",
        "POI data mismatch: never registered at BlockPosition",
        " does not specify an api-version",
    ]

    log_file_list = []
    for arg in sys.argv[1:]:
        if os.path.exists(arg) and os.path.isfile(arg) and arg.endswith(".log"):
            log_file_list.append(arg)

    if (len(log_file_list) < 1):
        print("ERROR: No log files specified")
        sys.exit("Usage: " + sys.argv[0] + " <file1.log> [file2.log] [...]")

    i = 0
    for fname in log_file_list:
        i += 1
        print("Processing file {} of {}...".format(i, len(log_file_list)), end="\r")
        with open(fname, "r") as fp:
            current_time = None
            current_source = None
            current_contents = None
            current_severity = None

            for line in fp:
                if line.startswith("["):
                    part = line.split("] [", 1)
                    time = part[0][1:]

                    part = part[1].strip().split("]:", 1)
                    label = part[0]
                    contents = part[1]

                    part = label.split("/", 1)
                    source = part[0]
                    severity = part[1]

                    if current_time == time and current_source == source and current_severity == severity and not contents.strip().startswith("[") and not contents.strip().startswith("Could not pass event"):
                        # This is a continuation of a previous line
                        if compare(prev_line, contents):
                            # This is exactly the same line as previously - just ignore it
                            pass
                        else:
                            prev_line = contents.strip("\n")
                            current_contents = "{}\n{}".format(current_contents, prev_line)
                    else:
                        if current_time is not None:
                            store_result(current_time, current_severity, current_contents)

                        prev_line = contents.strip("\n")
                        current_time = time
                        current_source = source
                        current_contents = contents
                        current_severity = severity
                else:
                    # This is a continuation of a previous line
                    prev_line = line.strip("\n")
                    current_contents = "{}\n{}".format(current_contents, line.strip("\n"))

    for level in error_map:
        print("################################################################################")
        print("# {}\n".format(level))
        for error in error_map[level]:
            errval = error_map[level][error]
            print("{}\n{}\n".format(errval[1], errval[0]))


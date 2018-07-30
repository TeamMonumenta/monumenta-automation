#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
This is the list of all shell actions available to the discord bots;
Please keep this list in alphabetical order within each category
"""

import os
_file_depth = 3
_file = os.path.abspath(__file__)
_top_level = os.path.abspath( os.path.join( _file, '../'*_file_depth ) )

from shell_common import ShellAction, datestr

commandPrefix = '~'
dangerousCharacters = ';<>*|`&$!#()[]{}:\'"'
def escapeDangerous(dangerString):
    if not any(c in dangerString for c in dangerousCharacters):
        return dangerString
    safeString = dangerString
    for c in dangerousCharacters:
        safeString.replace(c,'\\'+c)
    return safeString

allActions = []
allActionsDict = {}

class listening():
    def __init__(self):
        self._set = set()

    def isListening(self,key):
        if type(key) is not tuple:
            key = (key.channel.id,key.author.id)
        return key in self._set

    def select(self,key):
        if type(key) is not tuple:
            key = (key.channel.id,key.author.id)
        self._set.add(key)

    def deselect(self,key):
        if type(key) is not tuple:
            key = (key.channel.id,key.author.id)
        self._set.remove(key)

    def set(self,key,value):
        if value:
            self.select(key)
        else:
            self.deselect(key)

    def toggle(self,key):
        if type(key) is not tuple:
            key = (key.channel.id,key.author.id)
        if self.isListening(key):
            self.deselect(key)
        else:
            self.select(key)

################################################################################
# Common privilege code

privUsers = {
    "302298391969267712": {"name": "Combustible", "rights": [ "@root" ]},
    "228226807353180162": {"name": "NickNackGus", "rights": [ "@root" ]},
    "158655519588876288": {"name": "rockenroll4life", "rights": [ "@moderator" ]},
    "144306298811318272": {"name": "Chipmunk", "rights": [ "@moderator" ]},
    "163457917658333185": {"name": "masterchris92", "rights": [ "@moderator" ]},
    "164199966242373632": {"name": "Kaladun", "rights": [ "@moderator" ]},
    #"257887001834029056": {"name": "rayman520", "rights": [ "@moderator" ]},
}

groupByRole = {
    # Bot Moderator (TE)
    "464571038613766146": "@moderator",
    # Bot Skill Info (TE)
    "464598658449670145": "+skill info",
    # Moderator (Public)
    "313067199579422722": "+view scores",
}

permissionGroups = {
    "@root": [
        "+*",
        "-testunpriv",
    ],
    "@moderator": [
        "+debug",
        "+help",
        "+list bots",
        "+list shards",
        "+r1address to english",
        "+select",
        "+start shard",
        "+test",
        "+testpriv",
        "+whitelist",
    ],
    "@everyone": [
        "+debug",
        "+help",
    ],
    "@restricted": [
        "-*",
    ],
}

def checkPermissions(selfAct,author):
    result = False
    target = selfAct.command

    userInfo = privUsers.get( author.id, {"rights":["@everyone"]} )
    # This is a copy, not a reference
    userRights = list(userInfo.get("rights",["@everyone"]))
    alreadyChecked = set()
    for role in author.roles:
        permGroupName = groupByRole.get(role.id,None)
        if permGroupName is not None:
            userRights = [permGroupName] + userRights
    while len(userRights) > 0:
        perm = userRights.pop(0)
        if perm[0] == "@":
            # Permission group
            if perm not in alreadyChecked:
                alreadyChecked.add(perm)
                userRights = permissionGroups[perm] + userRights
            continue
        givenPerm = ( perm[0] == "+" )
        if (
            perm[1:] == target or
            perm[1:] == "*"
        ):
            result = givenPerm
    return result

################################################################################
# Simple test functions

class DebugAction(ShellAction):
    '''Prints debugging information about the requestor'''
    command = "debug"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

    async def doActions(self, client, channel, author):
        self._client = client
        self._channel = channel
        self._author = author

        message = "Your user ID is: " + author.id + "\n\nYour roles are:"
        for role in author.roles:
            message += "\n`" + role.name + "`: " + role.id

        message += "\n\nYour access rights are:\n```\n"
        userInfo = privUsers.get( author.id, {"rights":["@everyone"]} )
        userRights = userInfo.get("rights",["@everyone"])

        for role in author.roles:
            permGroupName = groupByRole.get(role.id,None)
            if permGroupName is not None:
                userRights = [permGroupName] + userRights

        groupStack = [ {"index":0,"rights":userRights} ]
        alreadyChecked = set()
        while len(groupStack) > 0:
            depth = len(groupStack)
            group = groupStack[depth-1]
            if group["index"] == len(group["rights"]):
                groupStack.pop()
                continue
            aRight = group["rights"][ group["index"] ]
            group["index"] += 1
            message += "  "*depth + aRight + "\n"
            if (
                aRight[0] == "@" and
                aRight not in alreadyChecked
            ):
                alreadyChecked.add(aRight)
                groupStack.append({"index":0,"rights":permissionGroups[aRight]})
        message += "```"

        await self.display(message),
allActions.append(DebugAction)

class TestAction(ShellAction):
    '''Simple test action that does nothing'''
    command = "test"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Testing successful!"),
        ]
allActions.append(TestAction)

class TestPrivilegedAction(ShellAction):
    '''Test if user has permission to use restricted commands'''
    command = "testpriv"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("You've got the power"),
        ]
allActions.append(TestPrivilegedAction)

class TestUnprivilegedAction(ShellAction):
    '''Test that a restricted command fails for all users'''
    command = "testunpriv"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("BUG: You definitely shouldn't have this much power"),
        ]
allActions.append(TestUnprivilegedAction)

################################################################################
# Always listening actions

class HelpAction(ShellAction):
    '''Lists commands available with this bot'''
    command = "help"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()
        # any -v style arguments should go here
        targetCommand = " ".join(commandArgs)
        if len(commandArgs) == 0:
            helptext = '''__Available Actions__'''
            for actionClass in botConfig["actions"].values():
                if actionClass.hasPermissions(actionClass,message.author):
                    helptext += "\n**" + commandPrefix + actionClass.command + "**"
                else:
                    helptext += "\n~~" + commandPrefix + actionClass.command + "~~"
            helptext += "\nRun `~help <command>` for more info."
        else:
            helptext = '''__Help on:__'''
            for actionClass in botConfig["actions"].values():
                if not (
                    actionClass.command == targetCommand or
                    commandPrefix + actionClass.command == targetCommand
                ):
                    continue
                if actionClass.hasPermissions(actionClass,message.author):
                    helptext += "\n**" + commandPrefix + actionClass.command + "**"
                else:
                    helptext += "\n~~" + commandPrefix + actionClass.command + "~~"
                helptext += "```" + actionClass.__doc__.replace('{cmdPrefix}',commandPrefix) + "```"
        self._commands = [
            self.display(helptext),
        ]
allActions.append(HelpAction)

class ListBotsAction(ShellAction):
    '''Lists currently running bots'''
    command = "list bots"
    hasPermissions = checkPermissions
    alwaysListening = True

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display('`' + botConfig["name"] + '`'),
        ]
allActions.append(ListBotsAction)

class SelectBotAction(ShellAction):
    '''Make specified bots start listening for commands; unlisted bots stop listening.
Syntax:
`{cmdPrefix}select [botName] [botName2] ...`
Examples:
`{cmdPrefix}select` - deselect all bots
`{cmdPrefix}select build` - select only the build bot
`{cmdPrefix}select play play2` - select both the play bots
`{cmdPrefix}select *` - select all bots'''
    command = "select"
    hasPermissions = checkPermissions
    alwaysListening = True

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()
        self._commands = []
        if (
            (
                '*' in commandArgs or
                botConfig["name"] in commandArgs
            ) ^
            botConfig["listening"].isListening(message)
        ):
            botConfig["listening"].toggle(message)
            if botConfig["listening"].isListening(message):
                self._commands = [
                    self.display(botConfig["name"] + " is now listening for commands."),
                ]
            else:
                self._commands = [
                    self.display(botConfig["name"] + " is no longer listening for commands."),
                ]
        elif botConfig["listening"].isListening(message):
            self._commands = [
                self.display(botConfig["name"] + " is still listening for commands."),
            ]
allActions.append(SelectBotAction)

################################################################################
# Useful actions start here

class FetchResetBundleAction(ShellAction):
    '''Dangerous!
Deletes in-progress terrain reset info on the play server
Downloads the terrain reset bundle from the build server and unpacks it'''
    command = "fetch reset bundle"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Unpacking reset bundle..."),
            self.run("rm -rf /home/rock/5_SCRATCH/tmpreset", None),
            self.run("mkdir -p /home/rock/5_SCRATCH/tmpreset"),
            self.cd("/home/rock/5_SCRATCH/tmpreset"),
            self.run("tar xzf /home/rock/4_SHARED/project_epic_build_template_pre_reset_" + datestr() + ".tgz"),
            self.display("Build server template data retrieved and ready for reset."),
            self.mention(),
        ]
allActions.append(FetchResetBundleAction)

class GitAction(ShellAction):
    '''Dangerous!
Doesn't have a good way to tell if changes are in progress.
Check in #server-ops before using.

Currently exposes all valid git syntax, including syntax that *will* softlock this action.'''
    command = "git"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix):]
        if len(commandArgs) > 3 and commandArgs[3] != ' ':
            self._commands = [
                self.display("Space expected at 4th character past prefix: " + repr(commandArgs)),
            ]
            return
        self._commands = [
            self.cd(_top_level),
            self.display("Running `" + commandArgs + "`"),
            self.run(commandArgs, displayOutput=True),
        ]
allActions.append(GitAction)

class GenerateInstancesAction(ShellAction):
    '''Dangerous!
Deletes previous terrain reset data
Temporarily brings down the dungeon shard to generate dungeon instances.
Must be run before preparing the build server reset bundle'''
    command = "generate instances"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Cleaning up old terrain reset data..."),
            self.run("rm -rf /home/rock/5_SCRATCH/tmpreset", None),
            self.run("mkdir -p /home/rock/5_SCRATCH/tmpreset"),

            self.display("Stopping the dungeon shard..."),
            self.run("mark2 send -n dungeon ~stop", None),
            self.sleep(5),
            self.run("mark2 send -n dungeon test", 1),

            self.display("Copying the dungeon master copies..."),
            self.run("cp -a /home/rock/project_epic/dungeon/Project_Epic-dungeon /home/rock/5_SCRATCH/tmpreset/Project_Epic-dungeon"),

            self.display("Restarting the dungeon shard..."),
            self.cd("/home/rock/project_epic/dungeon"),
            self.run("mark2 start"),

            self.display("Unpacking the dungeon template..."),
            self.cd("/home/rock/5_SCRATCH/tmpreset"),
            self.run("tar xzf /home/rock/assets/dungeon_template.tgz"),

            self.display("Generating dungeon instances (this may take a while)..."),
            self.run("python2 " + _top_level + "/utility_code/dungeon_instance_gen.py"),
            self.run("mv /home/rock/5_SCRATCH/tmpreset/dungeons-out /home/rock/5_SCRATCH/tmpreset/TEMPLATE"),

            self.display("Cleaning up instance generation temp files..."),
            self.run("rm -rf /home/rock/5_SCRATCH/tmpreset/Project_Epic-dungeon /home/rock/5_SCRATCH/tmpreset/Project_Epic-template"),
            self.display("Dungeon instance generation complete!"),
            self.mention(),
        ]
allActions.append(GenerateInstancesAction)

class ListShardsAction(ShellAction):
    '''Lists currently running shards on this server'''
    command = "list shards"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.run("mark2 list", displayOutput=True),
        ]
allActions.append(ListShardsAction)

class RepairBlockEntitiesAction(ShellAction):
    '''Repair Block Entities in specified worlds.
Syntax:
{cmdPrefix}repair block entities *
{cmdPrefix}repair block entities region_1 region_2 orange'''
    command = "repair block entities"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:]

        baseShellCommand = _top_level + "/utility_code/repair_block_entities.py"
        shellCommand = baseShellCommand
        allShards = botConfig["shards"]
        if '*' in commandArgs:
            for shard in allShards.keys():
                if shard != "bungee":
                    shellCommand += " " + allShards[shard]["path"] + "Project_Epic-" + shard + "/"
        else:
            for shard in allShards.keys():
                if shard in commandArgs:
                    if shard != "bungee":
                        shellCommand += " " + allShards[shard]["path"] + "Project_Epic-" + shard + "/"

        if shellCommand == baseShellCommand:
            self._commands = [
                self.display("No specified shards on this server."),
            ]
        else:
            self._commands = [
                self.run(shellCommand, displayOutput=True),
                self.mention(),
            ]
allActions.append(RepairBlockEntitiesAction)

class PrepareResetBundleAction(ShellAction):
    '''Dangerous!
Temporarily brings down the region_1 shard to prepare for terrain reset
Packages up all of the pre-reset server components needed by the play server for reset
Must be run before starting terrain reset on the play server'''
    command = "prepare reset bundle"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Stopping the region_1 shard..."),
            self.run("mark2 send -n region_1 ~stop", None),
            self.sleep(5),
            self.run("mark2 send -n region_1 test", 1),

            self.display("Copying region_1..."),
            self.run("mkdir -p /home/rock/5_SCRATCH/tmpreset/POST_RESET"),
            self.run("mkdir -p /home/rock/5_SCRATCH/tmpreset/TEMPLATE/region_1"),
            self.run("cp -a /home/rock/project_epic/region_1/Project_Epic-region_1 /home/rock/5_SCRATCH/tmpreset/TEMPLATE/region_1/"),

            self.display("Restarting the region_1 shard..."),
            self.cd("/home/rock/project_epic/region_1"),
            self.run("mark2 start"),

            self.display("Copying bungee..."),
            self.run("cp -a /home/rock/project_epic/bungee /home/rock/5_SCRATCH/tmpreset/TEMPLATE/"),

            self.display("Copying purgatory..."),
            self.run("cp -a /home/rock/project_epic/purgatory /home/rock/5_SCRATCH/tmpreset/TEMPLATE/"),

            self.display("Copying server_config..."),
            self.run("cp -a /home/rock/project_epic/server_config /home/rock/5_SCRATCH/tmpreset/TEMPLATE/"),

            self.display("Packaging up reset bundle..."),
            self.cd("/home/rock/5_SCRATCH/tmpreset"),
            self.run("tar czf /home/rock/4_SHARED/project_epic_build_template_pre_reset_" + datestr() + ".tgz POST_RESET TEMPLATE"),

            self.display("Reset bundle ready!"),
            self.mention(),
        ]
allActions.append(PrepareResetBundleAction)

class R1AddressToEnglishAction(ShellAction):
    '''Convert R1Address scores to a human-readable format
Syntax:
~r1address to english address1 [address2] ...'''
    command = "r1address to english"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()
        cmdString = _top_level + "/utility_code/r1address_to_english.py"
        self._commands = []
        while len(commandArgs) > 0:
            newVal = commandArgs.pop(0)
            try:
                newVal = int(newVal)
                cmdString = cmdString + " " + str(newVal)
            except:
                self.display(repr(newVal) + " is not a number."),
        self._commands = [
            self.run(cmdString, displayOutput=True),
            self.display("Done."),
        ]
allActions.append(R1AddressToEnglishAction)

class RestartBotAction(ShellAction):
    '''Restart this bot. Used to update to the latest version.
Do not use while the bot is running actions.
Syntax:
`{cmdPrefix}restart bot` restart bot with no arguements
`{cmdPrefix}restart bot ...` restart bot with arguements <...>
'''
    command = "restart bot"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

        commandArgs = message.content[len(commandPrefix + self.command)+1:]
        shellCommand = _top_level + "/discord_bots/server_shell_bots/bin/restart_bot.sh"
        self._commands = [
            self.run("{cmd} {pid} {arg} &".format(cmd=shellCommand,pid=botConfig["main_pid"],arg=commandArgs)),
        ]
allActions.append(RestartBotAction)

class SkillInfoAction(ShellAction):
    '''Print out skill info; used to update the public Google spreadsheet.
This will be updated to use the Google Sheets API at some point so it won't need to be updated manually.'''
    command = "skill info"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.run(_top_level + "/utility_code/skill_info.py", displayOutput=True),
        ]
allActions.append(SkillInfoAction)

class StageAction(ShellAction):
    '''List and restore pre-terrain reset backups. Intended for use with
the stage servers. NOT YET WORKING.

Syntax:
```
{cmdPrefix}stage list
{cmdPrefix}stage restore <file>
```'''
    command = "stage"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()
        usage = [
            self.display('''Syntax:
```
{cmdPrefix}stage list
{cmdPrefix}stage restore <file>
```'''.replace('{cmdPrefix}',cmdPrefix)),
        ]
        botName = botConfig["name"]
        playName = botName.replace("stage","play")
        if len(commandArgs) == 0:
            self._commands = usage
        elif commandArgs[0] == 'list':
            self._commands = [
                self.cd("/home/rock/4_SHARED/"),
                self.run("ls project_epic_pre_reset_{server}_* | sed 's/project_epic_pre_reset_{server}_//' | sed 's/.tgz//'".replace('{server}',playName), displayOutput=True),
            ]
        elif commandArgs[0] == 'restore':
            if len(commandArgs) < 2:
                self._commands = usage
            else:
                self._commands = [
                    self.cd("/home/rock/"),
                    self.run("rm -rf /home/rock/project_epic"),
                    self.run("tar xzf 4_SHARED/project_epic_pre_reset_{server}_{file}.tgz".replace('{server}',playName).replace('{file}',commandArgs[1])),
                    self.display("Restored {file}".replace('{file}',commandArgs[1])),
                ]
        else:
            self._commands = usage
allActions.append(StageAction)

class StartShardAction(ShellAction):
    '''Start specified shards.
Syntax:
{cmdPrefix}start shard *
{cmdPrefix}start shard region_1 region_2 orange'''
    command = "start shard"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()

        baseShellCommand = _top_level + "/discord_bots/server_shell_bots/bin/start_shards.sh"
        shellCommand = baseShellCommand
        allShards = botConfig["shards"]
        if '*' in commandArgs:
            for shard in allShards.keys():
                shellCommand += " " + allShards[shard]["path"]
        else:
            for shard in allShards.keys():
                if shard in commandArgs:
                    shellCommand += " " + allShards[shard]["path"]

        if shellCommand == baseShellCommand:
            self._commands = [
                self.display("No specified shards on this server."),
            ]
        else:
            self._commands = [
                self.run(shellCommand, displayOutput=True),
            ]
allActions.append(StartShardAction)

class StopAndBackupAction(ShellAction):
    '''Dangerous!
Brings down all play server shards and backs them up in preparation for terrain reset.
DELETES TUTORIAL AND PURGATORY AND DUNGEON CORE PROTECT DATA'''
    command = "stop and backup"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        allShards = botConfig["shards"].keys()
        self._commands = [
            self.display("Stopping all shards..."),
            self.run("mark2 sendall ~stop", None),
            self.sleep(10),
            # TODO: These three commands need to be replaced with one that actually checks everything is down
            self.run("mark2 list", displayOutput=True),
            self.run("mark2 send -n region_1 test", 1),
            self.sleep(5),

            self.display("Removing unneeded large files..."),
            self.run("rm -rf /home/rock/project_epic/white/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/orange/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/magenta/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/lightblue/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/yellow/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/nightmare/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/r1bonus/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/tutorial/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/purgatory/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/roguelike/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/purgatory /home/rock/project_epic/tutorial"),

            self.display("Performing backup..."),
        ]
        if "region_1" in allShards:
            self._commands += [
                self.run("cp -a /home/rock/project_epic/region_1/banned-ips.json /home/rock/4_SHARED/op-ban-sync/region_1/"),
                self.run("cp -a /home/rock/project_epic/region_1/banned-players.json /home/rock/4_SHARED/op-ban-sync/region_1/"),
                self.run("cp -a /home/rock/project_epic/region_1/ops.json /home/rock/4_SHARED/op-ban-sync/region_1/"),
            ]
        self._commands += [
            self.cd("/home/rock"),
            self.run("tar czf /home/rock/1_ARCHIVE/project_epic_pre_reset_" + botConfig["name"] + "_" + datestr() + ".tgz project_epic"),

            self.display("Backups complete! Ready for reset."),
            self.mention(),
        ]
allActions.append(StopAndBackupAction)

class StopIn10MinutesAction(ShellAction):
    '''Dangerous!
Starts a bungee shutdown timer for 10 minutes. Returns immediately.'''
    command = "stop in 10 minutes"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Telling bungee it should stop in 10 minutes..."),
            self.run("mark2 send -n bungee ~stop 10m;5m;3m;2m;1m;30s;10s", None),
            self.run("mark2 send -n region_1 co purge t:30d", None),
            self.run("mark2 send -n r1plots co purge t:30d", None),
            self.run("mark2 send -n betaplots co purge t:30d", None),
            # TODO: Something to wait for bungee to shut down
            self.display("Bungee will shut down in 10 minutes."),
            self.sleep(10*60),
            self.display("Bungee should be shutting down."),
            self.mention(),
        ]
allActions.append(StopIn10MinutesAction)

class TerrainResetAction(ShellAction):
    '''Dangerous!
Performs the terrain reset on the play server. Requires StopAndBackupAction.'''
    command = "terrain reset"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

        resetdir = "/home/rock/5_SCRATCH/tmpreset"
        allShards = botConfig["shards"].keys()

        self._commands = [
            # TODO: Check that all shards are stopped
            self.display("Moving the project_epic directory to PRE_RESET"),
            self.run("cp -a /home/rock/5_SCRATCH/tmpreset/TEMPLATE/server_config /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
            self.run("cp -a /home/rock/5_SCRATCH/tmpreset/TEMPLATE/purgatory /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
            self.run("mv /home/rock/project_epic /home/rock/5_SCRATCH/tmpreset/PRE_RESET"),
        ]

        if "bungee" in allShards:
            self._commands += [
                self.display("Copying bungeecord..."),
                self.run("mv /home/rock/5_SCRATCH/tmpreset/PRE_RESET/bungee /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
                # TODO: Update automatically
                self.display("TODO: You must manually update the version number in bungee's config.yml!"),
            ]

        self._commands += [
            self.display("Removing pre-reset server_config..."),
            self.run("rm -rf /home/rock/5_SCRATCH/tmpreset/PRE_RESET/server_config"),

            self.display("Running actual terrain reset (this will take a while!)..."),
            self.run("python2 " + _top_level + "/utility_code/terrain_reset.py " + " ".join(allShards)),
        ]

        for shard in ["r1plots", "betaplots", "region_1"]:
            if shard in allShards:
                self._commands += [
                    self.display("Preserving coreprotect, and easywarp data for {0}...".format(shard)),
                    self.run("mkdir -p {0}/POST_RESET/{1}/plugins/CoreProtect".format(resetdir, shard)),
                    self.run("mv {0}/PRE_RESET/{1}/{2} {0}/POST_RESET/{1}/{2}".format(resetdir, shard, "plugins/CoreProtect/database.db")),
                    self.run("mkdir -p {0}/POST_RESET/{1}/plugins/EasyWarp".format(resetdir, shard)),
                    self.run("mv {0}/PRE_RESET/{1}/{2} {0}/POST_RESET/{1}/{2}".format(resetdir, shard, "plugins/EasyWarp/warps.yml")),
                ]

        if "region_1" in allShards:
            self._commands += [
                self.run("mkdir -p {0}/POST_RESET/{1}/plugins/Monumenta_Speedruns/speedruns".format(resetdir, "region_1")),
                self.run("mv {0}/PRE_RESET/{1}/{2} {0}/POST_RESET/{1}/{2}".format(resetdir, "region_1", "plugins/Monumenta_Speedruns/speedruns/leaderboards")),
                self.run("mv {0}/PRE_RESET/{1}/{2} {0}/POST_RESET/{1}/{2}".format(resetdir, "region_1", "plugins/Monumenta_Speedruns/speedruns/playerdata")),
            ]

        if "build" in allShards:
            self._commands += [
                self.display("Moving the build shard..."),
                self.run("mv /home/rock/5_SCRATCH/tmpreset/PRE_RESET/build /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
            ]

        if "tutorial" in allShards:
            self._commands += [
                self.display("Copying the tutorial shard..."),
                self.run("cp -a /home/rock/5_SCRATCH/tmpreset/TEMPLATE/tutorial /home/rock/5_SCRATCH/tmpreset/POST_RESET/"),
            ]

        for shard in allShards:
            if shard in ["build","bungee"]:
                continue
            self._commands += [
                self.run("cp -af /home/rock/4_SHARED/op-ban-sync/region_1/banned-ips.json /home/rock/5_SCRATCH/tmpreset/POST_RESET/{}/".format(shard)),
                self.run("cp -af /home/rock/4_SHARED/op-ban-sync/region_1/banned-players.json /home/rock/5_SCRATCH/tmpreset/POST_RESET/{}/".format(shard)),
                self.run("cp -af /home/rock/4_SHARED/op-ban-sync/region_1/ops.json /home/rock/5_SCRATCH/tmpreset/POST_RESET/{}/".format(shard)),
            ]

        self._commands += [
            self.display("Generating per-shard config..."),
            self.cd("/home/rock/5_SCRATCH/tmpreset/POST_RESET"),
            self.run("python2 " + _top_level + "/utility_code/gen_server_config.py --play " + " ".join(allShards)),

            # TODO: This should probably print a warning and proceed anyway if some are found
            self.display("Checking for broken symbolic links..."),
            self.run("find /home/rock/5_SCRATCH/tmpreset/POST_RESET -xtype l", displayOutput=True),

            self.display("Renaming the reset directory..."),
            self.run("mv /home/rock/5_SCRATCH/tmpreset/POST_RESET /home/rock/5_SCRATCH/tmpreset/project_epic"),

            self.display("Backing up post-reset artifacts..."),
            self.cd("/home/rock/5_SCRATCH/tmpreset"),
            self.run("tar czf /home/rock/1_ARCHIVE/project_epic_post_reset_" + botConfig["name"] + "_" + datestr() + ".tgz project_epic"),

            self.display("Moving the project_epic result back where it should be..."),
            self.run("mv /home/rock/5_SCRATCH/tmpreset/project_epic /home/rock/"),

            self.display("Done."),
            self.mention(),
        ]
allActions.append(TerrainResetAction)

class ViewScoresAction(ShellAction):
    '''View player scores on Region 1. Run without arguements for syntax.
Note: the values from this command could be 15 minutes behind the play server.
Do not use for debugging quests or other scores that are likely to change often.'''
    command = "view scores"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:].split()
        cmdString = _top_level + "/utility_code/view_scores.py"
        while len(commandArgs) > 0:
            cmdString = cmdString + " " + commandArgs.pop(0)
        self._commands = [
            self.run(cmdString, displayOutput=True),
            self.display("Done."),
        ]
allActions.append(ViewScoresAction)

class WhitelistAction(ShellAction):
    '''Control server whitelists
`{cmdPrefix}whitelist enable *` - enable all shard whitelists, allows players to enter
`{cmdPrefix}whitelist disable *` - disables all shard whitelists, allows only opped players to enter
`{cmdPrefix}whitelist enable nightmare` - enable whitelist on only nightmare shard'''
    command = "whitelist"
    hasPermissions = checkPermissions

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(commandPrefix + self.command)+1:]

        enableString = "enable"
        disableString = "disable"

        if commandArgs[:len(enableString)] == enableString:
            header = "Enabling"
            baseShellCommand = "whitelist on"
            targetShards = commandArgs[len(enableString)+1:]

        elif commandArgs[:len(disableString)] == disableString:
            header = "Disabling"
            baseShellCommand = "whitelist off"
            targetShards = commandArgs[len(disableString)+1:]

        shellCommand = baseShellCommand
        allShards = botConfig["shards"].keys()
        self._commands = []

        if '*' in targetShards:
            for shard in allShards:
                self._commands.append(self.display(header + " whitelist for " + shard))
                self._commands.append(self.run("mark2 send -n " + shard + " " + baseShellCommand))
        else:
            for shard in allShards:
                if shard in targetShards:
                    self._commands.append(self.display(header + " whitelist for " + shard))
                    self._commands.append(self.run("mark2 send -n " + shard + " " + baseShellCommand))

        if len(self._commands) <= 0:
            self._commands = [
                self.display("No specified shards on this server."),
            ]
allActions.append(WhitelistAction)

################################################################################
# No actions past here!

for action in allActions:
    allActionsDict[action.command] = action

def findBestMatch(botConfig,message):
    '''Find the best matching command for a target message, igoring permissions.'''
    target = message.content
    bestMatch = ""
    actions = botConfig["actions"]
    for command in actions.keys():
        prefixedCommand = commandPrefix + command
        actionClass = actions[command]
        if not (
            botConfig["listening"].isListening(message) or
            actionClass.alwaysListening
        ):
            continue
        if (
            target[:len(prefixedCommand)] == prefixedCommand and
            len(command) > len(bestMatch)
        ):
            bestMatch = command
    if bestMatch == "":
        return None
    return actions[bestMatch]


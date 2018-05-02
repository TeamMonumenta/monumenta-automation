#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
This is the list of all shell actions available to the discord bots;
Please keep this list in alphabetical order within each category
"""

from shell_common import ShellAction, datestr

allActions = []
allActionsDict = {}

################################################################################
# Common privilege code

privUsers = {
    "302298391969267712": {"name": "Combustible", "rights": [ "root" ]},
    "228226807353180162": {"name": "NickNackGus", "rights": [ "root" ]},
    "158655519588876288": {"name": "rockenroll4life", "rights": [ "normal" ]},
    "144306298811318272": {"name": "Chipmunk", "rights": [ "normal" ]},
    "163457917658333185": {"name": "masterchris92", "rights": [ "normal" ]},
    "164199966242373632": {"name": "Kaladun", "rights": [ "normal" ]},
    #"257887001834029056": {"name": "rayman520", "rights": [ "normal" ]},
}

def rootPrivileged(selfIgnored,author):
    userInfo = privUsers.get( author.id, {"rights":[]} )
    userRights = userInfo.get("rights",[])
    if "root" in userRights:
        return True
    return False

def normalPrivileged(selfIgnored,author):
    userInfo = privUsers.get( author.id, {} )
    userRights = userInfo.get("rights",[])
    if (
        "normal" in userRights or
        "root" in userRights
    ):
        return True
    return False

def alwaysPrivileged(selfIgnored,author):
    return True

def neverPrivileged(selfIgnored,author):
    return False

commandPrefix = '~'

################################################################################
# Simple test functions

class DebugAction(ShellAction):
    '''Prints debugging information about the requestor'''
    command = commandPrefix + "debug"
    hasPermissions = alwaysPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

    async def doActions(self, client, channel, member):
        self._client = client
        self._channel = channel
        self._member = member

        message = "Your user ID is: " + member.id + "\nYour roles are:"
        for role in member.roles:
            message += "\n`" + role.name + "`: " + role.id

        userInfo = privUsers.get( author.id, {} )
        userRights = userInfo.get("rights",["None"])
        message += "Your access rights are:"
        for aRight in userRights:
            message += "\n`" + aRight + "`"

        await self.display(message),
allActions.append(DebugAction)

class TestAction(ShellAction):
    '''Simple test action that does nothing'''
    command = commandPrefix + "test"
    hasPermissions = alwaysPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Testing successful!"),
        ]
allActions.append(TestAction)

class TestPrivilegedAction(ShellAction):
    '''Test if user has permission to use restricted commands'''
    command = commandPrefix + "testpriv"
    hasPermissions = normalPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("You've got the power"),
        ]
allActions.append(TestPrivilegedAction)

class TestUnprivilegedAction(ShellAction):
    '''Test that a restricted command fails for all users'''
    command = commandPrefix + "testunpriv"
    hasPermissions = neverPrivileged

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
    command = commandPrefix + "help"
    hasPermissions = alwaysPrivileged
    alwaysListening = True

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        helptext = '''
This is the monumenta {botName} server bot.
It runs on the {botName} server's console.
It can be used to run actions on the {botName} server.
__Available Actions__'''.format(botName=botConfig["name"])
        for actionClass in botConfig["actions"].values():
            if not (
                botConfig["listening"] or
                actionClass.alwaysListening
            ):
                continue
            if actionClass.hasPermissions(message.author):
                helptext += "\n**" + actionClass.command + "**"
            else:
                helptext += "\n~~" + actionClass.command + "~~"
            helptext += "```" + actionClass.__doc__.format(cmdPrefix=commandPrefix) + "```"
        self._commands = [
            self.display(helptext),
        ]
allActions.append(HelpAction)

class ListBotsAction(ShellAction):
    '''Lists currently running bots'''
    command = commandPrefix + "list bots"
    hasPermissions = normalPrivileged
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
    command = commandPrefix + "select"
    hasPermissions = normalPrivileged
    alwaysListening = True

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(self.command)+1:]
        self._commands = []
        if (
            (
                '*' in commandArgs or
                botConfig["name"] in commandArgs
            ) ^
            botConfig["listening"]
        ):
            botConfig["listening"] = not botConfig["listening"]
            if botConfig["listening"]:
                self._commands = [
                    self.display(botConfig["name"] + " is now listening for commands."),
                ]
            else:
                self._commands = [
                    self.display(botConfig["name"] + " is no longer listening for commands."),
                ]
        elif botConfig["listening"]:
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
    command = commandPrefix + "fetch reset bundle"
    hasPermissions = rootPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Fetching reset bundle from build server..."),
            self.run("rm -rf /home/rock/4_SHARED/tmpreset"),
            self.run("mkdir -p /home/rock/4_SHARED/tmpreset"),
            self.run("sftp build:/home/rock/4_SHARED/tmpreset/project_epic_build_template_pre_reset_" + datestr() + ".tgz /home/rock/4_SHARED/tmpreset/"),
            self.display("Unpacking reset bundle..."),
            self.cd("/home/rock/4_SHARED/tmpreset"),
            self.run("tar xzf project_epic_build_template_pre_reset_" + datestr() + ".tgz"),
            self.display("Reset bundle is prepped for reset."),
        ]
allActions.append(FetchResetBundleAction)

class GenerateInstancesAction(ShellAction):
    '''Dangerous!
Deletes previous terrain reset data
Temporarily brings down the dungeon shard to generate dungeon instances.
Must be run before preparing the build server reset bundle'''
    command = commandPrefix + "generate instances"
    hasPermissions = rootPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Cleaning up old terrain reset data..."),
            self.run("rm -rf /home/rock/4_SHARED/tmpreset", None),
            self.run("mkdir -p /home/rock/4_SHARED/tmpreset"),

            self.display("Stopping the dungeon shard..."),
            self.run("mark2 send -n dungeon ~stop", None),
            self.sleep(5),
            self.run("mark2 send -n dungeon test", 1),

            self.display("Copying the dungeon master copies..."),
            self.run("cp -a /home/rock/project_epic/dungeon/Project_Epic-dungeon /home/rock/4_SHARED/tmpreset/Project_Epic-dungeon"),

            self.display("Restarting the dungeon shard..."),
            self.cd("/home/rock/project_epic/dungeon"),
            self.run("mark2 start"),

            self.display("Unpacking the dungeon template..."),
            self.cd("/home/rock/4_SHARED/tmpreset"),
            self.run("tar xzf /home/rock/assets/dungeon_template.tgz"),

            self.display("Generating dungeon instances (this may take a while)..."),
            self.run("python2 /home/rock/MCEdit-And-Automation/utility_code/dungeon_instance_gen.py"),
            self.run("mv /home/rock/4_SHARED/tmpreset/dungeons-out /home/rock/4_SHARED/tmpreset/POST_RESET"),

            self.display("Cleaning up instance generation temp files..."),
            self.run("rm -rf /home/rock/4_SHARED/tmpreset/Project_Epic-dungeon /home/rock/4_SHARED/tmpreset/Project_Epic-template"),
            self.display("Dungeon instance generation complete!"),
        ]
allActions.append(GenerateInstancesAction)

class ListShardsAction(ShellAction):
    '''Lists currently running shards on this server'''
    command = commandPrefix + "list shards"
    hasPermissions = alwaysPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.run("mark2 list", displayOutput=True),
        ]
allActions.append(ListShardsAction)

class PrepareResetBundleAction(ShellAction):
    '''Dangerous!
Temporarily brings down the region_1 shard to prepare for terrain reset
Packages up all of the pre-reset server components needed by the play server for reset
Must be run before starting terrain reset on the play server'''
    command = commandPrefix + "prepare reset bundle"
    hasPermissions = rootPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Stopping the region_1 shard..."),
            self.run("mark2 send -n region_1 ~stop", None),
            self.sleep(5),
            self.run("mark2 send -n region_1 test", 1),

            self.display("Copying region_1..."),
            self.run("mkdir -p /home/rock/4_SHARED/tmpreset/TEMPLATE/region_1"),
            self.run("cp -a /home/rock/project_epic/region_1/Project_Epic-region_1 /home/rock/4_SHARED/tmpreset/TEMPLATE/region_1/"),

            self.display("Restarting the region_1 shard..."),
            self.cd("/home/rock/project_epic/region_1"),
            self.run("mark2 start"),

            self.display("Copying bungee..."),
            self.run("cp -a /home/rock/project_epic/bungee /home/rock/4_SHARED/tmpreset/TEMPLATE/"),

            self.display("Copying purgatory..."),
            self.run("cp -a /home/rock/project_epic/purgatory /home/rock/4_SHARED/tmpreset/POST_RESET/"),

            self.display("Copying server_config..."),
            self.run("cp -a /home/rock/project_epic/server_config /home/rock/4_SHARED/tmpreset/POST_RESET/"),

            self.display("Packaging up reset bundle..."),
            self.cd("/home/rock/4_SHARED/tmpreset"),
            self.run("tar czf /home/rock/4_SHARED/tmpreset/project_epic_build_template_pre_reset_" + datestr() + ".tgz POST_RESET TEMPLATE"),

            self.display("Reset bundle ready!"),
        ]
allActions.append(PrepareResetBundleAction)

class StartShardAction(ShellAction):
    '''Start specified shards.
Syntax:
{cmdPrefix}start shard *
{cmdPrefix}start shard region_1 region_2 orange'''
    command = commandPrefix + "start shard"
    hasPermissions = normalPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(self.command)+1:]

        # TODO Should be made relative to the bot directory
        baseShellCommand = "/home/rock/MCEdit-And-Automation/discord_bots/server_shell_bots/bin/start_shards.sh"
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
    command = commandPrefix + "stop and backup"
    hasPermissions = rootPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
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
            self.cd("/home/rock"),
            self.run("tar czf /home/rock/1_ARCHIVE/project_epic_pre_reset_" + datestr() + ".tgz project_epic"),

            self.display("Backups complete! Ready for reset."),
        ]
allActions.append(StopAndBackupAction)

class StopIn10MinutesAction(ShellAction):
    '''Dangerous!
Starts a bungee shutdown timer for 10 minutes. Returns immediately.'''
    command = commandPrefix + "stop in 10 minutes"
    hasPermissions = rootPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Telling bungee it should stop in 10 minutes..."),
            self.run("mark2 send -n bungee ~stop 10m;5m;3m;2m;1m;30s;10s", None),
            # TODO: Something to wait for bungee to shut down
            self.display("Done - bungee will shut down in 10 minutes."),
        ]
allActions.append(StopIn10MinutesAction)

class TerrainResetAction(ShellAction):
    '''Dangerous!
Performs the terrain reset on the play server. Requires StopAndBackupAction.'''
    command = commandPrefix + "terrain reset"
    hasPermissions = rootPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Archiving the pre reset bundle backup..."),
            self.run("mv /home/rock/4_SHARED/tmpreset/project_epic_build_template_pre_reset_" + datestr() + ".tgz /home/rock/1_ARCHIVE/"),

            # TODO: Check that ~/4_SHARED/tmpreset exists and ~/4_SHARED/tmpreset/PRE_RESET doesn't
            self.display("Moving the project_epic directory to PRE_RESET"),
            self.run("mv /home/rock/project_epic /home/rock/4_SHARED/tmpreset/PRE_RESET"),

            self.display("Copying bungeecord..."),
            self.run("mv /home/rock/4_SHARED/tmpreset/PRE_RESET/bungee /home/rock/4_SHARED/tmpreset/POST_RESET/"),
            # TODO: Update automatically
            self.display("TODO: UPDATE BUNGEE NUMBER!"),

            # No longer need to update server versions...

            self.display("Preserving luckperms data..."),
            self.run("rm -rf /home/rock/4_SHARED/tmpreset/POST_RESET/server_config/plugins/LuckPerms/yaml-storage"),
            self.run("mv /home/rock/4_SHARED/tmpreset/PRE_RESET/server_config/plugins/LuckPerms/yaml-storage /home/rock/4_SHARED/tmpreset/POST_RESET/server_config/plugins/LuckPerms/yaml-storage"),

            self.display("Removing pre-reset server_config..."),
            self.run("rm -rf /home/rock/4_SHARED/tmpreset/PRE_RESET/server_config"),

            self.display("Running actual terrain reset (this will take a while!)..."),
            self.run("python2 /home/rock/MCEdit-And-Automation/utility_code/terrain_reset.py"),

            self.display("Preserving coreprotect and easywarp data for plots and region 1..."),
            self.run("mkdir -p /home/rock/4_SHARED/tmpreset/POST_RESET/betaplots/plugins/CoreProtect"),
            self.run("mv /home/rock/4_SHARED/tmpreset/PRE_RESET/betaplots/plugins/CoreProtect/database.db /home/rock/4_SHARED/tmpreset/POST_RESET/betaplots/plugins/CoreProtect/database.db"),
            self.run("mkdir -p /home/rock/4_SHARED/tmpreset/POST_RESET/betaplots/plugins/EasyWarp"),
            self.run("mv /home/rock/4_SHARED/tmpreset/PRE_RESET/betaplots/plugins/EasyWarp/warps.yml /home/rock/4_SHARED/tmpreset/POST_RESET/betaplots/plugins/EasyWarp/warps.yml"),
            self.run("mkdir -p /home/rock/4_SHARED/tmpreset/POST_RESET/r1plots/plugins/CoreProtect"),
            self.run("mv /home/rock/4_SHARED/tmpreset/PRE_RESET/r1plots/plugins/CoreProtect/database.db /home/rock/4_SHARED/tmpreset/POST_RESET/r1plots/plugins/CoreProtect/database.db"),
            self.run("mkdir -p /home/rock/4_SHARED/tmpreset/POST_RESET/r1plots/plugins/EasyWarp"),
            self.run("mv /home/rock/4_SHARED/tmpreset/PRE_RESET/r1plots/plugins/EasyWarp/warps.yml /home/rock/4_SHARED/tmpreset/POST_RESET/r1plots/plugins/EasyWarp/warps.yml"),
            self.run("mkdir -p /home/rock/4_SHARED/tmpreset/POST_RESET/region_1/plugins/CoreProtect"),
            self.run("mv /home/rock/4_SHARED/tmpreset/PRE_RESET/region_1/plugins/CoreProtect/database.db /home/rock/4_SHARED/tmpreset/POST_RESET/region_1/plugins/CoreProtect/database.db"),
            self.run("mkdir -p /home/rock/4_SHARED/tmpreset/POST_RESET/region_1/plugins/EasyWarp"),
            self.run("mv /home/rock/4_SHARED/tmpreset/PRE_RESET/region_1/plugins/EasyWarp/warps.yml /home/rock/4_SHARED/tmpreset/POST_RESET/region_1/plugins/EasyWarp/warps.yml"),

            self.display("Moving the build shard..."),
            self.run("mv /home/rock/4_SHARED/tmpreset/PRE_RESET/build /home/rock/4_SHARED/tmpreset/POST_RESET/"),

            # TODO: path relative to this bot folder
            self.display("Synchronizing the whitelist/opslist/banlist..."),
            self.run("/home/rock/MCEdit-And-Automation/discord_bots/server_shell_bots/bin/sync_whitelist.sh /home/rock/4_SHARED/tmpreset/PRE_RESET/region_1 /home/rock/4_SHARED/tmpreset/POST_RESET"),

            self.display("Generating per-shard config..."),
            self.cd("/home/rock/4_SHARED/tmpreset/POST_RESET"),
            self.run("python2 /home/rock/MCEdit-And-Automation/utility_code/gen_server_config.py --play build betaplots lightblue magenta nightmare orange purgatory r1bonus r1plots region_1 roguelike tutorial white yellow"),

            # TODO: This should probably print a warning and proceed anyway if some are found
            self.display("Checking for broken symbolic links..."),
            self.run("find /home/rock/4_SHARED/tmpreset/POST_RESET -xtype l"),

            self.display("Renaming the reset directory..."),
            self.run("mv /home/rock/4_SHARED/tmpreset/POST_RESET /home/rock/4_SHARED/tmpreset/project_epic"),

            self.display("Backing up post-reset artifacts..."),
            self.cd("/home/rock/4_SHARED/tmpreset"),
            self.run("tar czf /home/rock/1_ARCHIVE/project_epic_post_reset_" + datestr() + ".tgz project_epic"),

            self.display("Moving the project_epic result back where it should be..."),
            self.run("mv /home/rock/4_SHARED/tmpreset/project_epic /home/rock/"),

            self.display("Removing pre-reset artifacts..."),
            self.run("rm -r /home/rock/4_SHARED/tmpreset/PRE_RESET /home/rock/4_SHARED/tmpreset/TEMPLATE"),
        ]
allActions.append(TerrainResetAction)

class WhitelistAction(ShellAction):
    '''Control server whitelists
`{cmdPrefix}whitelist` - list shard whitelist status
`{cmdPrefix}whitelist enable *` - enable all shard whitelists, allows players to enter
`{cmdPrefix}whitelist disable *` - disables all shard whitelists, allows only opped players to enter
`{cmdPrefix}whitelist enable nightmare` - enable whitelist on only nightmare shard'''
    command = commandPrefix + "whitelist"
    hasPermissions = rootPrivileged

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        commandArgs = message.content[len(self.command)+1:]

        # TODO Should be made relative to the bot directory
        enableString = "enable"
        disableString = "disable"

        if commandArgs[:len(enableString)] == enableString:
            header = "running subcommand enable"
            baseShellCommand = "/home/rock/MCEdit-And-Automation/discord_bots/server_shell_bots/bin/whitelist_shards_enable.sh"
            targetShards = commandArgs[len(enableString)+1:]

        elif commandArgs[:len(disableString)] == disableString:
            header = "running subcommand disable"
            baseShellCommand = "/home/rock/MCEdit-And-Automation/discord_bots/server_shell_bots/bin/whitelist_shards_disable.sh"
            targetShards = commandArgs[len(disableString)+1:]

        else:
            header = "running subcommand list"
            baseShellCommand = "/home/rock/MCEdit-And-Automation/discord_bots/server_shell_bots/bin/whitelist_shards_list.sh"
            targetShards = "*"

        shellCommand = baseShellCommand
        allShards = botConfig["shards"]
        if '*' in targetShards:
            for shard in allShards.keys():
                shellCommand += " " + allShards[shard]["path"]
        else:
            for shard in allShards.keys():
                if shard in targetShards:
                    shellCommand += " " + allShards[shard]["path"]

        if shellCommand == baseShellCommand:
            self._commands = [
                self.display(header),
                self.display("No specified shards on this server."),
            ]
        else:
            self._commands = [
                self.display(header),
                self.run(shellCommand, displayOutput=True),
            ]
allActions.append(WhitelistAction)

################################################################################
# No actions past here!

for action in allActions:
    allActionsDict[action.command] = action

def findBestMatch(botConfig,target):
    '''Find the best matching command for a target message, igoring permissions.'''
    bestMatch = ""
    actions = botConfig["actions"]
    for command in actions.keys():
        actionClass = actions[command]
        if not (
            botConfig["listening"] or
            actionClass.alwaysListening
        ):
            continue
        if (
            target[:len(command)] == command and
            len(command) > len(bestMatch)
        ):
            bestMatch = command
    if bestMatch == "":
        return None
    return actions[bestMatch]


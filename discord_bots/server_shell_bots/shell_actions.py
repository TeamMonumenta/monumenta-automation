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
    "Combustible": "302298391969267712",
    "NickNackGus": "228226807353180162",
    "rockenroll4life": "158655519588876288",
    "Chipmunk": "144306298811318272",
    "masterchris92": "163457917658333185",
    "Kaladun": "164199966242373632",
    #"rayman520": "257887001834029056",
}

privIds = privUsers.values()
print(privIds)

def isPrivileged(author):
    if author.id in privIds:
        return True
    return False

commandPrefix = '~'

################################################################################
# Simple test functions

class DebugAction(ShellAction):
    '''Prints debugging information about the requestor'''
    command = commandPrefix + "debug"

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])

    def hasPermissions(self, author):
        return True

    async def doActions(self, client, channel, member):
        self._client = client
        self._channel = channel
        self._member = member

        message = "Your user ID is: " + member.id + "\nYour roles are:"
        for role in member.roles:
            message += "\n`" + role.name + "`: " + role.id
        await self.display(message),
allActions.append(DebugAction)

class TestAction(ShellAction):
    '''Simple test action that does nothing'''
    command = commandPrefix + "test"

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Testing successful!"),
        ]

    def hasPermissions(self, author):
        return True
allActions.append(TestAction)

class TestPrivilegedAction(ShellAction):
    '''Test if user has permission to use restricted commands'''
    command = commandPrefix + "testpriv"

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("You've got the power"),
        ]

    def hasPermissions(self, author):
        return isPrivileged(author)
allActions.append(TestPrivilegedAction)

class TestUnprivilegedAction(ShellAction):
    '''Test that a restricted command fails for all users'''
    command = commandPrefix + "testunpriv"

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("BUG: You definitely shouldn't have this much power"),
        ]

    def hasPermissions(self, author):
        return False
allActions.append(TestUnprivilegedAction)

################################################################################
# Useful actions start here

class FetchResetBundleAction(ShellAction):
    '''Dangerous!
Deletes in-progress terrain reset info on the play server
Downloads the terrain reset bundle from the build server and unpacks it'''
    command = commandPrefix + "fetch reset bundle"

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

    def hasPermissions(self, author):
        return isPrivileged(author)
allActions.append(FetchResetBundleAction)

class GenerateInstancesAction(ShellAction):
    '''Dangerous!
Deletes previous terrain reset data
Temporarily brings down the dungeon shard to generate dungeon instances.
Must be run before preparing the build server reset bundle'''
    command = commandPrefix + "generate instances"

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

    def hasPermissions(self, author):
        return isPrivileged(author)
allActions.append(GenerateInstancesAction)

class HelpAction(ShellAction):
    '''Lists commands available with this bot'''
    command = commandPrefix + "help"
    alwaysListening = True

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        helptext = '''
This is the monumenta {0} server bot.
It runs on the {0} server's console.
It can be used to run actions on the {0} server.
__Available Actions__'''.format(botConfig["name"])
        for actionClass in botConfig["actions"].values():
            if not (
                botConfig["listening"] or
                actionClass.alwaysListening
            ):
                continue
            action = actionClass(botConfig, message)
            if action.hasPermissions(message.author):
                helptext += "\n**" + action.command + "**"
            else:
                helptext += "\n~~" + action.command + "~~"
            helptext += "```" + action.__doc__ + "```"
        self._commands = [
            self.display(helptext),
        ]

    def hasPermissions(self, author):
        return True
allActions.append(HelpAction)

class ListBotsAction(ShellAction):
    '''Lists currently running bots'''
    command = commandPrefix + "list bots"
    alwaysListening = True

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display('`' + botConfig["name"] + '`'),
        ]

    def hasPermissions(self, author):
        return True
allActions.append(ListBotsAction)

class ListShardsAction(ShellAction):
    '''Lists currently running shards on this server'''
    command = commandPrefix + "list shards"

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.run("mark2 list", displayOutput=True),
        ]

    def hasPermissions(self, author):
        return True
allActions.append(ListShardsAction)

class PrepareResetBundleAction(ShellAction):
    '''Dangerous!
Temporarily brings down the region_1 shard to prepare for terrain reset
Packages up all of the pre-reset server components needed by the play server for reset
Must be run before starting terrain reset on the play server'''
    command = commandPrefix + "prepare reset bundle"

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

    def hasPermissions(self, author):
        return isPrivileged(author)
allActions.append(PrepareResetBundleAction)

class StartShardsAction(ShellAction):
    '''Start all shards.'''
    command = commandPrefix + "start shards"

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            # TODO: path relative to this bot folder
            # TODO: This does not work at all - likely the wrong shell used
            self.display("Starting all primary shards..."),
            self.run("/home/rock/MCEdit-And-Automation/discord_bots/server_shell_bots/bin/start_all_shards.sh"),

            self.display("Starting the vanilla shard..."),
            self.cd("/home/rock/3_VANILLA"),
            self.run("mark2 start"),

            self.display("Starting bungeecord..."),
            self.cd("/home/rock/project_epic/bungee"),
            self.run("mark2 start"),
        ]

    def hasPermissions(self, author):
        return isPrivileged(author)
allActions.append(StartShardsAction)

class SelectBotAction(ShellAction):
    '''Make specified bots start listening for commands; unlisted bots stop listening.
Syntax:
`!select [botName] [botName2] ...`
Examples:
`!select` - deselect all bots
`!select build` - select only the build bot
`!select play play2` - select both the play bots
`!select *` - select all bots'''
    command = commandPrefix + "select"
    alwaysListening = True

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = []
        if (
            (
                '*' in message.content or
                botConfig["name"] in message.content
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

    def hasPermissions(self, author):
        return isPrivileged(author)
allActions.append(SelectBotAction)

class StopAndBackupAction(ShellAction):
    '''Dangerous!
Brings down all play server shards and backs them up in preparation for terrain reset.
DELETES TUTORIAL AND PURGATORY AND DUNGEON CORE PROTECT DATA'''
    command = commandPrefix + "stop and backup"

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

    def hasPermissions(self, author):
        return isPrivileged(author)
allActions.append(StopAndBackupAction)

class StopIn10MinutesAction(ShellAction):
    '''Dangerous!
Starts a bungee shutdown timer for 10 minutes. Returns immediately.'''
    command = commandPrefix + "stop in 10 minutes"

    def __init__(self, botConfig, message):
        super().__init__(botConfig["extraDebug"])
        self._commands = [
            self.display("Telling bungee it should stop in 10 minutes..."),
            self.run("mark2 send -n bungee ~stop 10m;5m;3m;2m;1m;30s;10s", None),
            # TODO: Something to wait for bungee to shut down
            self.display("Done - bungee will shut down in 10 minutes."),
        ]

    def hasPermissions(self, author):
        return isPrivileged(author)
allActions.append(StopIn10MinutesAction)

class TerrainResetAction(ShellAction):
    '''Dangerous!
Performs the terrain reset on the play server. Requires StopAndBackupAction.'''
    command = commandPrefix + "terrain reset"

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

    def hasPermissions(self, author):
        return isPrivileged(author)
allActions.append(TerrainResetAction)

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


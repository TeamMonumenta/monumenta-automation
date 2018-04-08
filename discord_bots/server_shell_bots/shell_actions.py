
from shell_common import ShellAction, datestr

################################################################################
# Common privilege code

privUsers = {
    "Combustible": "302298391969267712",
    "NickNackGus": "228226807353180162",
    "rockenroll4life": "158655519588876288",
    "Chipmunk": "144306298811318272",
    "masterchris92": "163457917658333185",
    "Kaladun": "164199966242373632",
}

privIds = privUsers.values()
print(privIds)

def isPrivileged(author):
    if author.id in privIds:
        return True
    return False

################################################################################
# Simple test functions

class DebugAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)

    def getCommand(self):
        return "!debug"

    def hasPermissions(self, author):
        return True

    def help(self):
        return "Prints debugging information about the requestor"

    async def doActions(self, client, channel, member):
        self._client = client
        self._channel = channel
        self._member = member

        message = "Your user ID is: " + member.id + "\nYour roles are:"
        for role in member.roles:
            message += "\n`" + role.name + "`: " + role.id
        await self.display(message),

class TestAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
        self._commands = [
            self.display("Testing successful!"),
        ]

    def getCommand(self):
        return "!test"

    def hasPermissions(self, author):
        return True

    def help(self):
        return "Simple test action that does nothing"

class TestPrivilegedAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
        self._commands = [
            self.display("You've got the power"),
        ]

    def getCommand(self):
        return "!testpriv"

    def hasPermissions(self, author):
        return isPrivileged(author)

    def help(self):
        return "Test if user has permission to use restricted commands"

class TestUnprivilegedAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
        self._commands = [
            self.display("BUG: You definitely shouldn't have this much power"),
        ]

    def getCommand(self):
        return "!testunpriv"

    def hasPermissions(self, author):
        return False

    def help(self):
        return "Test that a restricted command fails for all users"

################################################################################
# Useful actions start here

class ListShardsAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
        self._commands = [
            self.run("mark2 list", displayOutput=True),
        ]

    def getCommand(self):
        return "!list shards"

    def hasPermissions(self, author):
        return True

    def help(self):
        return "Lists currently running shards on this server"

class GenerateInstancesAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
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

    def getCommand(self):
        return "!generate instances"

    def hasPermissions(self, author):
        return isPrivileged(author)

    def help(self):
        return '''Dangerous!
Deletes previous terrain reset data
Temporarily brings down the dungeon shard to generate dungeon instances.
Must be run before preparing the build server reset bundle
'''

class PrepareResetBundleAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
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

    def getCommand(self):
        return "!prepare reset bundle"

    def hasPermissions(self, author):
        return isPrivileged(author)

    def help(self):
        return '''Dangerous!
Temporarily brings down the region_1 shard to prepare for terrain reset
Packages up all of the pre-reset server components needed by the play server for reset
Must be run before starting terrain reset on the play server
'''

class StopIn10MinutesAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
        self._commands = [
            self.display("Telling bungee it should stop in 10 minutes..."),
            self.run("mark2 send -n bungee ~stop 10m;5m;3m;2m;1m;30s;10s", None),
            # TODO: Something to wait for bungee to shut down
            self.display("Done - bungee will shut down in 10 minutes."),
        ]

    def getCommand(self):
        return "!stop in 10 minutes"

    def hasPermissions(self, author):
        return isPrivileged(author)

    def help(self):
        return '''Dangerous!
Brings down all play server shards and backs them up in preparation for terrain reset.
'''
class StopAndBackupAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
        self._commands = [
            self.display("Stopping all shards..."),
            self.run("mark2 sendall ~stop", None),
            self.sleep(10),
            # TODO: These three commands need to be replaced with one that actually checks everything is down
            self.run("mark2 list", displayOutput=True),
            self.run("mark2 send -n region_1 test", 1),
            self.sleep(5),

            self.display("Performing full backup..."),
            self.cd("/home/rock"),
            self.run("tar czf /home/rock/1_ARCHIVE/project_epic_pre_reset_full_backup_" + datestr() + ".tgz project_epic"),

            self.display("Removing unneeded large files..."),
            self.run("rm -r /home/rock/project_epic/white/Project_Epic-white/region"),
            self.run("rm -rf /home/rock/project_epic/white/plugins/CoreProtect"),
            self.run("rm -r /home/rock/project_epic/orange/Project_Epic-orange/region"),
            self.run("rm -rf /home/rock/project_epic/orange/plugins/CoreProtect"),
            self.run("rm -r /home/rock/project_epic/magenta/Project_Epic-magenta/region"),
            self.run("rm -rf /home/rock/project_epic/magenta/plugins/CoreProtect"),
            self.run("rm -r /home/rock/project_epic/lightblue/Project_Epic-lightblue/region"),
            self.run("rm -rf /home/rock/project_epic/lightblue/plugins/CoreProtect"),
            self.run("rm -r /home/rock/project_epic/yellow/Project_Epic-yellow/region"),
            self.run("rm -rf /home/rock/project_epic/yellow/plugins/CoreProtect"),
            self.run("rm -r /home/rock/project_epic/r1bonus/Project_Epic-r1bonus/region"),
            self.run("rm -rf /home/rock/project_epic/r1bonus/plugins/CoreProtect"),
            self.run("rm -r /home/rock/project_epic/tutorial/Project_Epic-tutorial/region"),
            self.run("rm -rf /home/rock/project_epic/tutorial/plugins/CoreProtect"),
            self.run("rm -r /home/rock/project_epic/purgatory/Project_Epic-purgatory/region"),
            self.run("rm -rf /home/rock/project_epic/purgatory/plugins/CoreProtect"),
            self.run("rm -r /home/rock/project_epic/roguelike/Project_Epic-roguelike/region"),
            self.run("rm -rf /home/rock/project_epic/roguelike/plugins/CoreProtect"),
            self.run("rm -rf /home/rock/project_epic/purgatory /home/rock/project_epic/tutorial"),
            # TODO: Pretty sure these wildcards won't work
            #self.run("rm ~/project_epic/server_config/*.jar"),
            #self.run("rm ~/project_epic/server_config/plugins/*.jar"),

            self.display("Performing backup..."),
            self.cd("/home/rock"),
            self.run("tar czf /home/rock/1_ARCHIVE/project_epic_pre_reset_" + datestr() + ".tgz project_epic"),

            self.display("Backups complete! Ready for reset."),
        ]

    def getCommand(self):
        return "!stop and backup"

    def hasPermissions(self, author):
        return isPrivileged(author)

    def help(self):
        return '''Dangerous!
Brings down all play server shards and backs them up in preparation for terrain reset.
'''

class TerrainResetAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
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

            # TODO: This does not work as-is, doesn't see arguments for some reason...
            self.display("Generating per-shard config..."),
            self.cd("/home/rock/4_SHARED/tmpreset/POST_RESET"),
            self.run("python /home/rock/MCEdit-And-Automation/utility_code/gen_server_config.py --play build betaplots lightblue magenta orange purgatory r1bonus r1plots region_1 roguelike tutorial white yellow"),

            # TODO: This should probably fail if some are found
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

            # TODO: path relative to this bot folder
            # TODO: This does not work correctly because the files aren't copied from PRE_RESET
            self.display("Synchronizing the whitelist/opslist/banlist..."),
            self.run("/home/rock/MCEdit-And-Automation/discord_bots/server_shell_bots/bin/sync_whitelist.sh"),

            # TODO: path relative to this bot folder
            # TODO: This does not work at all - likely the wrong shell used
            self.display("Starting all primary shards..."),
            self.run("/home/rock/MCEdit-And-Automation/discord_bots/server_shell_bots/bin/start_all_shards.sh"),

            self.display("Starting the vanilla shard..."),
            self.cd("/home/rock/3_VANILLA"),
            self.run("mark2 start"),

            self.display("Starting bungeecord..."),
            self.cd("/home/rock/project_epic/vanilla"),
            self.run("mark2 start"),
        ]
    def getCommand(self):
        return "!terrain reset"

    def hasPermissions(self, author):
        return isPrivileged(author)

    def help(self):
        # TODO: More detail on how to run this
        return '''Dangerous!
Performs the terrain reset on the play server. Requires StopAndBackupAction.
'''

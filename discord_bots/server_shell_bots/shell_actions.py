
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
            self.run("rm -rf /home/rock/tmpreset", None),
            self.run("mkdir -p /home/rock/tmpreset"),

            self.display("Stopping the dungeon shard..."),
            self.run("mark2 send -n dungeon ~stop", None),
            self.sleep(5),
            self.run("mark2 send -n dungeon test", 1),

            self.display("Copying the dungeon master copies..."),
            self.run("cp -a /home/rock/project_epic/dungeon/Project_Epic-dungeon /home/rock/tmpreset/Project_Epic-dungeon"),

            self.display("Restarting the dungeon shard..."),
            self.cd("/home/rock/project_epic/dungeon"),
            self.run("mark2 start"),

            self.display("Unpacking the dungeon template..."),
            self.cd("/home/rock/tmpreset"),
            self.run("tar xzf /home/rock/assets/dungeon_template.tgz"),

            self.display("Generating dungeon instances (this may take a while)..."),
            self.run("python2 /home/rock/MCEdit-And-Automation/utility_code/dungeon_instance_gen.py"),
            self.run("mv /home/rock/tmpreset/dungeons-out /home/rock/tmpreset/POST_RESET"),

            self.display("Cleaning up instance generation temp files..."),
            self.run("rm -rf /home/rock/tmpreset/Project_Epic-dungeon /home/rock/tmpreset/Project_Epic-template"),
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
            self.run("mkdir -p /home/rock/tmpreset/TEMPLATE/region_1"),
            self.run("cp -a /home/rock/project_epic/region_1/Project_Epic-region_1 /home/rock/tmpreset/TEMPLATE/region_1/"),

            self.display("Restarting the region_1 shard..."),
            self.cd("/home/rock/project_epic/region_1"),
            self.run("mark2 start"),

            self.display("Copying bungee..."),
            self.run("cp -a /home/rock/project_epic/bungee /home/rock/tmpreset/TEMPLATE/"),

            self.display("Copying purgatory..."),
            self.run("cp -a /home/rock/project_epic/purgatory /home/rock/tmpreset/POST_RESET/"),

            self.display("Copying tutorial..."),
            self.run("mkdir -p /home/rock/tmpreset/POST_RESET/tutorial"),
            self.cd("/home/rock/tmpreset/POST_RESET/tutorial"),
            self.run("tar xzf /home/rock/assets/Project_Epic-tutorial.tgz"),

            self.display("Copying server_config..."),
            self.run("cp -a /home/rock/project_epic/server_config /home/rock/tmpreset/POST_RESET/"),

            self.display("Packaging up reset bundle..."),
            self.cd("/home/rock/tmpreset"),
            self.run("tar czf /home/rock/tmpreset/project_epic_build_template_pre_reset_" + datestr() + ".tgz POST_RESET TEMPLATE"),

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

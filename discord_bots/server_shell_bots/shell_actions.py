
from shell_common import ShellAction, datestr

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

class DebugAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)

    def getCommand(self):
        return "!debug"

    def hasPermissions(self, author):
        return True

    async def doActions(self, client, channel, member):
        self._client = client
        self._channel = channel
        self._member = member

        await self.display("Your user ID is: " + member.id),
        await self.display("Your roles are:"),
        for role in member.roles:
            await self.display("`" + role.name + "`: " + role.id),

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

class TestPrivilegedAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
        self._commands = [
            self.display("You've got the power"),
        ]

    def getCommand(self):
        return "!testpriv"

    def hasPermissions(self, author):
        if author.id in privIds:
            return True
        return False

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
            self.run("tar xzf /home/rock/dungeon_template-keep-this-12-29-2017.tgz"),

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
        if author.id in privIds:
            return True
        return False

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
            self.run("tar xzf /home/rock/Project_Epic-tutorial.good.jan-12-2018.tgz"),

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
        if author.id in privIds:
            return True
        return False

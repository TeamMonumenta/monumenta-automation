
from shell_common import ShellAction, datestr

class TestAction(ShellAction):
    def __init__(self, debug=False):
        super().__init__(debug)
        self._commands = [
            self.display("Testing successful!"),
        ]

    def getCommand(self):
        return "!test"

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

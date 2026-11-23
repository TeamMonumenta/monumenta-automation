import net.minecrell.pluginyml.bukkit.BukkitPluginDescription

plugins {
	id("com.playmonumenta.gradle-config") version "5.8.0"
}

repositories {
	mavenCentral()
	maven("https://repo.codemc.org/repository/maven-public/")
}

dependencies {
	compileOnly(libs.gson)
	compileOnly(libs.commandapi)
	testImplementation(libs.gson)
}

testing {
	suites {
		val test by getting(JvmTestSuite::class) {
			useJUnitJupiter(libs.versions.junit.get())
		}
	}
}

monumenta {
	name("MonumentaTaskBot")
	id("MonumentaTaskBot")
	paper(
		"com.playmonumenta.taskbot.TaskBotPlugin",
		BukkitPluginDescription.PluginLoadOrder.POSTWORLD,
		"1.20",
		depends = listOf("CommandAPI"),
		softDepends = listOf(),
	)
	gitPrefix("task-bot-plugin/")
}

// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.plugin.java.JavaPlugin;

/**
 * In-game access to the task bots (bug reports, suggestions). See README.md next to this
 * plugin's build file.
 */
public class TaskBotPlugin extends JavaPlugin implements Listener {
	private final List<TaskInstance> mInstances = new ArrayList<>();

	@Override
	public void onEnable() {
		PluginConfig config = PluginConfig.fromEnv(System.getenv());
		for (String problem : config.problems()) {
			getLogger().warning(problem);
		}
		if (config.instances().isEmpty()) {
			getLogger().info("No task bot instances configured (TASKBOT_INSTANCES); in-game reporting is off");
			return;
		}
		for (PluginConfig.Instance inst : config.instances()) {
			TaskInstance instance = new TaskInstance(this, config, inst, new ApiClient(inst.url(), inst.token()));
			instance.registerPermissions();
			mInstances.add(instance);
			loadInfoAndRegister(instance, 0);
		}
		Bukkit.getPluginManager().registerEvents(this, this);
	}

	/**
	 * The command is registered once the tracker has told us its wording and labels (the
	 * labels are part of /bug report), retrying in the background until it answers. Labels
	 * change about once a year and the plugin restarts daily, so they are fixed from then on.
	 */
	private void loadInfoAndRegister(TaskInstance instance, int attempt) {
		instance.loadInfo().whenComplete((ok, err) -> {
			if (!isEnabled()) {
				return;
			}
			if (err == null) {
				Bukkit.getScheduler().runTask(this, () -> {
					instance.register();
					// Players already online get the new command in their command list
					Bukkit.getOnlinePlayers().forEach(Player::updateCommands);
					getLogger().info("Registered /" + instance.command() + " with labels " + instance.info().labels());
				});
				return;
			}
			long delay = Math.min(600, 15L << Math.min(attempt, 5));
			getLogger().warning("/" + instance.command() + ": can't reach the tracker yet ("
				+ ApiClient.unwrap(err).getMessage() + "), retrying in " + delay + "s");
			Bukkit.getScheduler().runTaskLater(this, () -> loadInfoAndRegister(instance, attempt + 1), delay * 20L);
		});
	}

	/**
	 * Update notices are shown when a player joins, which happens often as they move between
	 * shards. A few seconds after joining, so the notice isn't lost in the join messages.
	 */
	@EventHandler(ignoreCancelled = true)
	public void onJoin(PlayerJoinEvent event) {
		UUID uuid = event.getPlayer().getUniqueId();
		Bukkit.getScheduler().runTaskLater(this, () -> {
			Player player = Bukkit.getPlayer(uuid);
			if (player != null) {
				mInstances.forEach(instance -> instance.deliverNotices(player));
			}
		}, 100L);
	}
}

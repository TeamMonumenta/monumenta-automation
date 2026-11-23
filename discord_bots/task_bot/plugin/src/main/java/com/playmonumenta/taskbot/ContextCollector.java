// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import com.google.gson.JsonObject;
import org.bukkit.Location;
import org.bukkit.entity.Player;

/**
 * Builds the context attached to an in-game report: named JSON sections that the task bot
 * stores privately for the team (never in the public channel).
 *
 * <p>For now this records where the report was made. More collectors (equipment, player
 * state, quest progress, ...) are meant to be added later, likely with data from redis-sync
 * or scripted quests; each adds its own section, and the bot needs no change since it
 * stores any named section. Runs on the main thread, since it reads player state.
 */
public final class ContextCollector {
	private ContextCollector() {
	}

	public static JsonObject collect(Player player, String serverName, String pluginVersion) {
		JsonObject context = new JsonObject();
		context.add("location", location(player, serverName));
		context.add("report", report(player, serverName, pluginVersion));
		return context;
	}

	static JsonObject location(Player player, String serverName) {
		Location loc = player.getLocation();
		JsonObject obj = new JsonObject();
		obj.addProperty("server", serverName);
		obj.addProperty("world", loc.getWorld() != null ? loc.getWorld().getName() : "unknown");
		obj.addProperty("x", round(loc.getX()));
		obj.addProperty("y", round(loc.getY()));
		obj.addProperty("z", round(loc.getZ()));
		obj.addProperty("yaw", round(loc.getYaw()));
		obj.addProperty("pitch", round(loc.getPitch()));
		return obj;
	}

	static JsonObject report(Player player, String serverName, String pluginVersion) {
		JsonObject obj = new JsonObject();
		obj.addProperty("source", "in-game");
		obj.addProperty("server", serverName);
		obj.addProperty("gamemode", player.getGameMode().name());
		obj.addProperty("plugin_version", pluginVersion);
		obj.addProperty("time_ms", System.currentTimeMillis());
		return obj;
	}

	private static double round(double v) {
		return Math.round(v * 100.0) / 100.0;
	}
}

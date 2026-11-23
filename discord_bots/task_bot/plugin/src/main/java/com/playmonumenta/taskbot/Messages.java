// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import java.util.ArrayList;
import java.util.List;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.event.ClickEvent;
import net.kyori.adventure.text.event.HoverEvent;
import net.kyori.adventure.text.format.NamedTextColor;
import net.kyori.adventure.text.format.TextDecoration;

/** Chat rendering of entries and results. */
public final class Messages {
	private static final int LINE_WIDTH = 60;

	private Messages() {
	}

	public static Component prefix(InstanceInfo info) {
		return Component.text("[" + info.proper() + "] ", NamedTextColor.GOLD);
	}

	public static Component error(InstanceInfo info, String message) {
		return prefix(info).append(Component.text(message, NamedTextColor.RED));
	}

	public static Component ok(InstanceInfo info, String message) {
		return prefix(info).append(Component.text(message, NamedTextColor.GREEN));
	}

	/** Clickable "#123" that shows the entry. */
	public static Component idLink(String command, int id) {
		return Component.text("#" + id, NamedTextColor.AQUA)
			.clickEvent(ClickEvent.runCommand("/" + command + " get " + id))
			.hoverEvent(HoverEvent.showText(Component.text("Show #" + id)));
	}

	public static String status(JsonObject entry) {
		if ("open".equals(str(entry, "status"))) {
			return "open";
		}
		String res = str(entry, "resolution_name");
		return res.isEmpty() ? "closed" : res;
	}

	/** One line per entry, for search results and lists. */
	public static Component line(String command, JsonObject entry) {
		int id = entry.get("id").getAsInt();
		boolean open = "open".equals(str(entry, "status"));
		return Component.text()
			.append(idLink(command, id))
			.append(Component.text(" " + status(entry) + " ", open ? NamedTextColor.GREEN : NamedTextColor.GRAY))
			.append(Component.text(labels(entry) + " ", NamedTextColor.DARK_AQUA))
			.append(Component.text(oneLine(str(entry, "description"), LINE_WIDTH), NamedTextColor.WHITE))
			.build();
	}

	/** An entry in full. */
	public static List<Component> detail(InstanceInfo info, String command, JsonObject entry) {
		List<Component> out = new ArrayList<>();
		int id = entry.get("id").getAsInt();
		out.add(prefix(info).append(Component.text(info.proper() + " ", NamedTextColor.YELLOW))
			.append(idLink(command, id))
			.append(Component.text(" " + labels(entry) + " " + str(entry, "priority") + " / " + str(entry, "complexity"),
				NamedTextColor.DARK_AQUA)));
		out.add(Component.text("By " + authorName(entry) + ", " + status(entry), NamedTextColor.GRAY));
		for (String text : str(entry, "description").split("\n")) {
			out.add(Component.text(text, NamedTextColor.WHITE));
		}
		if ("closed".equals(str(entry, "status"))) {
			out.add(Component.text("Closed: " + str(entry, "close_reason"), NamedTextColor.GRAY)
				.decoration(TextDecoration.ITALIC, true));
		}
		return out;
	}

	public static String authorName(JsonObject entry) {
		JsonElement author = entry.get("author");
		if (author == null || !author.isJsonObject()) {
			return "unknown";
		}
		String name = str(author.getAsJsonObject(), "name");
		return name.isEmpty() ? "unknown" : name;
	}

	public static String labels(JsonObject entry) {
		JsonElement labels = entry.get("labels");
		if (labels == null || !labels.isJsonArray()) {
			return "[]";
		}
		List<String> names = new ArrayList<>();
		for (JsonElement el : (JsonArray) labels) {
			names.add(el.getAsString());
		}
		return "[" + String.join(",", names) + "]";
	}

	public static String oneLine(String text, int width) {
		String flat = text.replaceAll("\\s+", " ").trim();
		return flat.length() <= width ? flat : flat.substring(0, width - 3) + "...";
	}

	/** A text field from the bot, safe to show (see {@link ApiClient#safeText}). */
	static String str(JsonObject obj, String key) {
		JsonElement el = obj.get(key);
		return el == null || el.isJsonNull() ? "" : ApiClient.safeText(el.getAsString());
	}
}

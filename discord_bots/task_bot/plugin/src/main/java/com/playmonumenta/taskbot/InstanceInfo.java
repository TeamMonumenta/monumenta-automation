// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import java.util.ArrayList;
import java.util.List;
import org.jetbrains.annotations.Nullable;

/**
 * What a task bot instance calls its entries ("bug", "suggestion") and its labels and
 * priorities, from its /api/info. The plugin, like taskctl, knows nothing about the
 * instance until it asks; the command is registered only once it has the answer. Until
 * then, the fallback (named after the command) serves notices shown on join.
 */
public record InstanceInfo(String single, String plural, String proper, List<String> labels,
	List<String> priorities) {
	public static InstanceInfo fallback(String command) {
		return new InstanceInfo(command, command + "s", Character.toUpperCase(command.charAt(0)) + command.substring(1),
			List.of(), List.of());
	}

	public static InstanceInfo fromApi(String command, @Nullable JsonObject info) {
		InstanceInfo fb = fallback(command);
		if (info == null || !info.has("descriptor") || !info.get("descriptor").isJsonObject()) {
			return fb;
		}
		JsonObject d = info.getAsJsonObject("descriptor");
		return new InstanceInfo(str(d, "single", fb.single()), str(d, "plural", fb.plural()),
			str(d, "proper", fb.proper()), strings(info, "labels"), strings(info, "priorities"));
	}

	private static List<String> strings(JsonObject obj, String key) {
		List<String> out = new ArrayList<>();
		if (obj.has(key) && obj.get(key).isJsonArray()) {
			for (JsonElement el : obj.getAsJsonArray(key)) {
				out.add(el.getAsString());
			}
		}
		return List.copyOf(out);
	}

	private static String str(JsonObject obj, String key, String fallback) {
		return obj.has(key) && obj.get(key).isJsonPrimitive() ? obj.get(key).getAsString() : fallback;
	}
}

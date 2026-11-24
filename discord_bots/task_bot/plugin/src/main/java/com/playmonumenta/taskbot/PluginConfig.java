// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import org.jetbrains.annotations.Nullable;

/**
 * Configuration from environment variables, like the exception reporter.
 *
 * <pre>
 * TASKBOT_INSTANCES        command names separated by spaces or commas, e.g. "bug suggestion"
 * TASKBOT_&lt;NAME&gt;_URL       base URL of that task bot's API, e.g. http://bug-bot.default.svc.cluster.local:8081
 * TASKBOT_&lt;NAME&gt;_TOKEN     a service token for it (python -m taskbot.tokens create ...)
 * TASKBOT_&lt;NAME&gt;_TOKEN_FILE  or a file holding it (e.g. a mounted secret), which keeps it out
 *                          of the environment that crash reports and heap dumps capture
 * TASKBOT_SERVER_NAME      this shard's name in report context (default: NETWORK_RELAY_NAME,
 *                          then EXCEPTLOG_SERVER_NAME, then hostname)
 * TASKBOT_REPORT_COOLDOWN_SECONDS   per-player cooldown between reports (default 60)
 * </pre>
 *
 * An instance without both a URL and a token is disabled and registers no command, so
 * the plugin can be installed everywhere and only report where it is configured (play).
 */
public record PluginConfig(List<Instance> instances, String serverName, int reportCooldownSeconds,
	List<String> problems) {

	public record Instance(String command, String url, String token) {
	}

	public static PluginConfig fromEnv(Map<String, String> env) {
		List<String> problems = new ArrayList<>();
		List<Instance> instances = new ArrayList<>();
		String raw = env.getOrDefault("TASKBOT_INSTANCES", "");
		for (String part : raw.split("[,\\s]+")) {
			String command = part.trim().toLowerCase(Locale.ROOT);
			if (command.isEmpty()) {
				continue;
			}
			if (!command.matches("[a-z][a-z0-9_]{0,31}")) {
				problems.add("ignoring instance '" + command + "': command names are a-z, 0-9 and _");
				continue;
			}
			String key = "TASKBOT_" + command.toUpperCase(Locale.ROOT);
			String url = blankToNull(env.get(key + "_URL"));
			String token = blankToNull(env.get(key + "_TOKEN"));
			String tokenFile = blankToNull(env.get(key + "_TOKEN_FILE"));
			if (token == null && tokenFile != null) {
				try {
					token = blankToNull(java.nio.file.Files.readString(java.nio.file.Path.of(tokenFile)));
				} catch (java.io.IOException e) {
					problems.add("instance '" + command + "': can't read " + tokenFile + ": " + e.getMessage());
				}
			}
			if (url == null || token == null) {
				problems.add("instance '" + command + "' is disabled: " + key + "_URL and " + key + "_TOKEN are both needed");
				continue;
			}
			url = url.replaceAll("/+$", "");
			if (!isHttpUrl(url)) {
				problems.add("instance '" + command + "' is disabled: " + key + "_URL '" + url + "' is not an http(s) URL");
				continue;
			}
			instances.add(new Instance(command, url, token));
		}
		String serverName = or(env.get("TASKBOT_SERVER_NAME"), or(env.get("NETWORK_RELAY_NAME"),
			or(env.get("EXCEPTLOG_SERVER_NAME"), or(env.get("HOSTNAME"), "unknown"))));
		return new PluginConfig(Collections.unmodifiableList(instances), serverName,
			intOr(env.get("TASKBOT_REPORT_COOLDOWN_SECONDS"), 60, problems),
			Collections.unmodifiableList(problems));
	}

	/** The HTTP client refuses anything else, and would do it while building each request. */
	private static boolean isHttpUrl(String url) {
		try {
			URI uri = new URI(url);
			String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase(Locale.ROOT);
			return ("http".equals(scheme) || "https".equals(scheme)) && uri.getHost() != null;
		} catch (URISyntaxException e) {
			return false;
		}
	}

	private static @Nullable String blankToNull(@Nullable String value) {
		return value == null || value.isBlank() ? null : value.trim();
	}

	private static String or(@Nullable String value, String fallback) {
		return value == null || value.isBlank() ? fallback : value.trim();
	}

	private static int intOr(@Nullable String value, int fallback, List<String> problems) {
		if (value == null || value.isBlank()) {
			return fallback;
		}
		try {
			return Integer.parseInt(value.trim());
		} catch (NumberFormatException e) {
			problems.add("'" + value + "' is not a number, using " + fallback);
			return fallback;
		}
	}
}

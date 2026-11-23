// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import java.util.Map;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PluginConfigTest {
	@Test
	void instancesNeedUrlAndToken() {
		PluginConfig c = PluginConfig.fromEnv(Map.of(
			"TASKBOT_INSTANCES", "bug, Suggestion ,bad-name",
			"TASKBOT_BUG_URL", "http://bug-bot.default.svc.cluster.local/",
			"TASKBOT_BUG_TOKEN", "tbs_x",
			"TASKBOT_SUGGESTION_URL", "http://suggestion-bot",
			"NETWORK_RELAY_NAME", "valley"));
		assertEquals(1, c.instances().size());
		assertEquals("bug", c.instances().get(0).command());
		assertEquals("http://bug-bot.default.svc.cluster.local", c.instances().get(0).url());
		assertEquals("valley", c.serverName());
		assertEquals(2, c.problems().size());
		assertTrue(c.problems().stream().anyMatch(p -> p.contains("TASKBOT_SUGGESTION_TOKEN")),
			c.problems().toString());
	}

	@Test
	void spaceSeparatedAsTheHelmChartSetsIt() {
		PluginConfig c = PluginConfig.fromEnv(Map.of("TASKBOT_INSTANCES", "bug suggestion",
			"TASKBOT_BUG_URL", "http://a", "TASKBOT_BUG_TOKEN", "t",
			"TASKBOT_SUGGESTION_URL", "http://b", "TASKBOT_SUGGESTION_TOKEN", "u"));
		assertEquals(2, c.instances().size());
		assertEquals("suggestion", c.instances().get(1).command());
	}

	@Test
	void nothingConfiguredMeansOffAndBadNumbersFallBack() {
		PluginConfig c = PluginConfig.fromEnv(Map.of());
		assertTrue(c.instances().isEmpty());
		assertEquals("unknown", c.serverName());
		assertEquals(60, c.reportCooldownSeconds());
		c = PluginConfig.fromEnv(Map.of("TASKBOT_REPORT_COOLDOWN_SECONDS", "soon"));
		assertEquals(60, c.reportCooldownSeconds());
		assertEquals(1, c.problems().size());
	}
}

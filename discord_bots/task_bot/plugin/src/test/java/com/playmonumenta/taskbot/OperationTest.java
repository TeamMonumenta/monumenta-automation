// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import java.util.OptionalInt;
import java.util.Set;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class OperationTest {
	@Test
	void nodes() {
		assertEquals("monumenta.taskbot.bug.create", Operation.CREATE.node("bug"));
		assertEquals("monumenta.taskbot.suggestion.fix.own", Operation.FIX.ownNode("Suggestion"));
	}

	@Test
	void fullNodeAssertsTheOperationsPrivilege() {
		Set<String> perms = Set.of("monumenta.taskbot.bug.fix", "monumenta.taskbot.bug.priority");
		assertEquals(OptionalInt.of(1), Operation.FIX.privilegeFor("bug", perms::contains));
		assertEquals(OptionalInt.of(2), Operation.PRIORITY.privilegeFor("bug", perms::contains));
	}

	@Test
	void ownNodeAssertsNothingSoTheBotChecksOwnership() {
		Set<String> perms = Set.of("monumenta.taskbot.bug.reject.own");
		assertTrue(Operation.REJECT.allowed("bug", perms::contains));
		assertEquals(OptionalInt.of(0), Operation.REJECT.privilegeFor("bug", perms::contains));
		assertFalse(Operation.FIX.allowed("bug", perms::contains));
		assertEquals(OptionalInt.empty(), Operation.FIX.privilegeFor("bug", perms::contains));
	}

	@Test
	void nonOwnableOperationsIgnoreOwnNodes() {
		Set<String> perms = Set.of("monumenta.taskbot.bug.priority.own");
		assertFalse(Operation.PRIORITY.allowed("bug", perms::contains));
	}
}

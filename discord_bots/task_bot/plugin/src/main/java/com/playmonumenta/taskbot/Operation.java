// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import java.util.Locale;
import java.util.OptionalInt;
import java.util.function.Predicate;

/**
 * Everything a player can do in game, each with its own permission node, so a permissions
 * plugin decides who may do what: for example everyone may report, search and read, and
 * only moderators may close other players' reports.
 *
 * <p>Nodes are {@code monumenta.taskbot.<command>.<operation>}, e.g.
 * {@code monumenta.taskbot.bug.create}. Operations that may apply to one's own reports
 * ({@link #mOwnable}) also have {@code ...<operation>.own}: holding only that, a player may
 * do it to reports they filed themselves (the task bot checks ownership).
 *
 * <p>The task bot enforces privilege levels (0-4, as in Discord); the plugin, trusted
 * through its service token, tells it which level to apply for each request. That level
 * comes from here: the level the operation needs on any entry if the player holds the
 * full node, 0 if they only hold the {@code .own} node.
 */
public enum Operation {
	CREATE("create", false, 0),
	VIEW("view", false, 0),
	NOTIFY("notify", false, 0),
	APPEND("append", true, 1),
	REJECT("reject", true, 1),
	FIX("fix", true, 1),
	REOPEN("reopen", true, 1),
	DUPE("dupe", true, 1),
	PRIORITY("priority", false, 2),
	CONTEXT("context", false, 2),
	NO_COOLDOWN("create.nocooldown", false, 0);

	public final String mNode;
	public final boolean mOwnable;
	/** Privilege the task bot requires to do this to anyone's entry. */
	public final int mPrivilege;

	Operation(String node, boolean ownable, int privilege) {
		mNode = node;
		mOwnable = ownable;
		mPrivilege = privilege;
	}

	public String node(String command) {
		return "monumenta.taskbot." + command.toLowerCase(Locale.ROOT) + "." + mNode;
	}

	public String ownNode(String command) {
		return node(command) + ".own";
	}

	/** Whether a player with these permissions may use the operation at all. */
	public boolean allowed(String command, Predicate<String> hasPermission) {
		return hasPermission.test(node(command)) || (mOwnable && hasPermission.test(ownNode(command)));
	}

	/**
	 * The privilege to assert to the task bot for this player, or empty if they may not do it.
	 * Holding only the {@code .own} node asserts 0, leaving the ownership check to the bot.
	 */
	public OptionalInt privilegeFor(String command, Predicate<String> hasPermission) {
		if (hasPermission.test(node(command))) {
			return OptionalInt.of(mPrivilege);
		}
		if (mOwnable && hasPermission.test(ownNode(command))) {
			return OptionalInt.of(0);
		}
		return OptionalInt.empty();
	}
}

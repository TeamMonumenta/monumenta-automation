// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

/** An error from the task bot API (its message is safe to show players), or a connection failure. */
public class ApiException extends Exception {
	private final int mStatus;

	public ApiException(int status, String message) {
		super(message);
		mStatus = status;
	}

	/** HTTP status, or 0 when the server could not be reached. */
	public int status() {
		return mStatus;
	}
}

// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.google.gson.JsonParser;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;
import java.util.StringJoiner;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import org.jetbrains.annotations.Nullable;

/**
 * Client for one task bot's /api (see API.md next to the bot). Every call is asynchronous
 * and completes off the server thread; callers hop back to the main thread before
 * touching Bukkit state. Requests made for a player carry the player headers, so the
 * bot attributes the change to them and applies the privilege the plugin grants.
 */
public class ApiClient {
	public static final String PLAYER_HEADER = "X-Taskbot-Player";
	public static final String PLAYER_NAME_HEADER = "X-Taskbot-Player-Name";
	public static final String PRIVILEGE_HEADER = "X-Taskbot-Privilege";

	/** A player the request is made for, with the privilege granted for this request. */
	public record Caller(UUID uuid, String name, int privilege) {
	}

	private static final Gson GSON = new Gson();
	private final HttpClient mHttp;
	private final String mBaseUrl;
	private final String mToken;
	private final Duration mTimeout;

	public ApiClient(String baseUrl, String token) {
		this(baseUrl, token, Duration.ofSeconds(10));
	}

	public ApiClient(String baseUrl, String token, Duration timeout) {
		mBaseUrl = baseUrl.replaceAll("/+$", "");
		mToken = token;
		mTimeout = timeout;
		mHttp = HttpClient.newBuilder().connectTimeout(timeout).build();
	}

	public CompletableFuture<JsonObject> info() {
		return send("GET", "/api/info", null, null);
	}

	public CompletableFuture<JsonObject> create(Caller caller, String label, String description, JsonObject context) {
		JsonObject body = new JsonObject();
		body.addProperty("description", description);
		JsonArray labels = new JsonArray();
		labels.add(label);
		body.add("labels", labels);
		body.add("context", context);
		return send("POST", "/api/entries", caller, body);
	}

	public CompletableFuture<JsonObject> get(Caller caller, int id) {
		return send("GET", "/api/entries/" + id, caller, null);
	}

	/** Open entries whose description contains every word. */
	public CompletableFuture<JsonObject> search(Caller caller, String words, int limit) {
		return send("GET", "/api/entries" + query(Map.of("q", words, "limit", String.valueOf(limit),
			"sort", "priority")), caller, null);
	}

	/** The caller's own reports, newest first, open and closed. */
	public CompletableFuture<JsonObject> mine(Caller caller, int limit) {
		return send("GET", "/api/entries" + query(Map.of("author_player", "me", "status", "all",
			"order", "desc", "limit", String.valueOf(limit))), caller, null);
	}

	/** POST /api/entries/{id}/{action}: append, fix, reject, reopen, dupe. */
	public CompletableFuture<JsonObject> act(Caller caller, int id, String action, JsonObject body) {
		return send("POST", "/api/entries/" + id + "/" + action, caller, body);
	}

	public CompletableFuture<JsonObject> patch(Caller caller, int id, JsonObject body) {
		return send("PATCH", "/api/entries/" + id, caller, body);
	}

	public CompletableFuture<JsonObject> context(Caller caller, int id) {
		return send("GET", "/api/entries/" + id + "/context", caller, null);
	}

	public CompletableFuture<JsonObject> setNotifications(Caller caller, boolean enabled) {
		JsonObject body = new JsonObject();
		body.addProperty("notifications", enabled);
		return send("POST", "/api/players/" + caller.uuid() + "/settings", caller, body);
	}

	public CompletableFuture<JsonObject> getSettings(Caller caller) {
		return send("GET", "/api/players/" + caller.uuid() + "/settings", caller, null);
	}

	/** The player's undelivered notices; the bot marks them delivered as it hands them out. */
	public CompletableFuture<JsonObject> takeNotices(Caller caller) {
		return send("POST", "/api/players/" + caller.uuid() + "/notices/take", caller, null);
	}

	/**
	 * Text from the bot made safe to show in chat: entries typed in Discord can hold section
	 * signs, which the client reads as formatting codes (hidden or fake lines), and control
	 * characters. Newlines stay.
	 */
	static String safeText(String text) {
		return text.replaceAll("[\\u00a7\\p{Cc}&&[^\\n]]", "");
	}

	static String query(Map<String, String> params) {
		StringJoiner joiner = new StringJoiner("&", "?", "");
		params.entrySet().stream().sorted(Map.Entry.comparingByKey()).forEach(e ->
			joiner.add(URLEncoder.encode(e.getKey(), StandardCharsets.UTF_8) + "="
				+ URLEncoder.encode(e.getValue(), StandardCharsets.UTF_8)));
		return joiner.toString();
	}

	CompletableFuture<JsonObject> send(String method, String path, @Nullable Caller caller,
		@Nullable JsonObject body) {
		HttpRequest.Builder req = HttpRequest.newBuilder(URI.create(mBaseUrl + path))
			.timeout(mTimeout)
			.header("Authorization", "Bearer " + mToken)
			.header("Accept", "application/json");
		if (caller != null) {
			req.header(PLAYER_HEADER, caller.uuid().toString())
				.header(PLAYER_NAME_HEADER, caller.name())
				.header(PRIVILEGE_HEADER, String.valueOf(caller.privilege()));
		}
		if (body != null) {
			req.header("Content-Type", "application/json")
				.method(method, HttpRequest.BodyPublishers.ofString(GSON.toJson(body)));
		} else {
			req.method(method, HttpRequest.BodyPublishers.noBody());
		}
		return mHttp.sendAsync(req.build(), HttpResponse.BodyHandlers.ofString())
			.handle((resp, err) -> {
				if (err != null) {
					throw new CompletionException(new ApiException(0, "could not reach the "
						+ "tracker (" + rootMessage(err) + ")"));
				}
				return parse(resp.statusCode(), resp.body());
			});
	}

	static JsonObject parse(int status, String text) {
		JsonObject json;
		try {
			JsonElement el = JsonParser.parseString(text == null || text.isEmpty() ? "{}" : text);
			json = el.isJsonObject() ? el.getAsJsonObject() : new JsonObject();
		} catch (JsonParseException e) {
			json = new JsonObject();
		}
		if (status >= 200 && status < 300) {
			return json;
		}
		String message = json.has("error") && json.get("error").isJsonPrimitive()
			? json.get("error").getAsString() : "HTTP " + status;
		throw new CompletionException(new ApiException(status, message));
	}

	/** The ApiException behind a failed future, or a generic one. */
	public static ApiException unwrap(Throwable err) {
		Throwable t = err;
		while (t != null) {
			if (t instanceof ApiException api) {
				return api;
			}
			t = t.getCause();
		}
		return new ApiException(0, rootMessage(err));
	}

	private static String rootMessage(Throwable err) {
		Throwable t = err;
		while (t.getCause() != null) {
			t = t.getCause();
		}
		return t.getMessage() != null ? t.getMessage() : t.getClass().getSimpleName();
	}
}

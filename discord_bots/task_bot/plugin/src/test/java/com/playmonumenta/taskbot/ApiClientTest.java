// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutionException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ApiClientTest {
	private static final UUID STEVE = UUID.fromString("11111111-2222-3333-4444-555555555555");
	private HttpServer mServer;
	private final Map<String, String> mSeen = new ConcurrentHashMap<>();
	private ApiClient mClient;

	@BeforeEach
	void start() throws IOException {
		mServer = HttpServer.create(new InetSocketAddress(InetAddress.getLoopbackAddress(), 0), 0);
		mServer.createContext("/", exchange -> {
			mSeen.put("method", exchange.getRequestMethod());
			mSeen.put("uri", exchange.getRequestURI().toString());
			mSeen.put("auth", String.valueOf(exchange.getRequestHeaders().getFirst("Authorization")));
			mSeen.put("player", String.valueOf(exchange.getRequestHeaders().getFirst(ApiClient.PLAYER_HEADER)));
			mSeen.put("privilege", String.valueOf(exchange.getRequestHeaders().getFirst(ApiClient.PRIVILEGE_HEADER)));
			mSeen.put("body", new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
			String path = exchange.getRequestURI().getPath();
			int status = path.endsWith("/99") ? 404 : path.endsWith("/boom") ? 500 : 200;
			String reply = status == 404 ? "{\"error\": \"Bug #99 not found\"}"
				: status == 500 ? "<html>oops</html>" : "{\"id\": 7, \"ok\": true}";
			byte[] bytes = reply.getBytes(StandardCharsets.UTF_8);
			exchange.sendResponseHeaders(status, bytes.length);
			try (OutputStream out = exchange.getResponseBody()) {
				out.write(bytes);
			}
		});
		mServer.start();
		mClient = new ApiClient("http://127.0.0.1:" + mServer.getAddress().getPort() + "/", "tbs_secret",
			Duration.ofSeconds(5));
	}

	@AfterEach
	void stop() {
		mServer.stop(0);
	}

	@Test
	void createSendsPlayerHeadersAndContext() throws Exception {
		JsonObject context = new JsonObject();
		context.add("location", JsonParser.parseString("{\"x\": 1.5}"));
		JsonObject result = mClient.create(new ApiClient.Caller(STEVE, "Steve", 0), "quest", "the door is stuck shut", context).get();
		assertEquals(7, result.get("id").getAsInt());
		assertEquals("POST", mSeen.get("method"));
		assertEquals("/api/entries", mSeen.get("uri"));
		assertEquals("Bearer tbs_secret", mSeen.get("auth"));
		assertEquals(STEVE.toString(), mSeen.get("player"));
		assertEquals("0", mSeen.get("privilege"));
		JsonObject body = JsonParser.parseString(mSeen.get("body")).getAsJsonObject();
		assertEquals("the door is stuck shut", body.get("description").getAsString());
		assertEquals("[\"quest\"]", body.get("labels").toString());
		assertEquals(1.5, body.getAsJsonObject("context").getAsJsonObject("location").get("x").getAsDouble());
	}

	@Test
	void searchEncodesTheQuery() throws Exception {
		mClient.search(new ApiClient.Caller(STEVE, "Steve", 0), "lava & fire", 8).get();
		assertEquals("/api/entries?limit=8&q=lava+%26+fire&sort=priority", mSeen.get("uri"));
	}

	@Test
	void noticesAreTakenForThePlayer() throws Exception {
		mClient.takeNotices(new ApiClient.Caller(STEVE, "Steve", 0)).get();
		assertEquals("POST", mSeen.get("method"));
		assertEquals("/api/players/" + STEVE + "/notices/take", mSeen.get("uri"));
		assertEquals(STEVE.toString(), mSeen.get("player"));
	}

	@Test
	void apiErrorsCarryTheServersMessage() {
		ExecutionException e = assertThrows(ExecutionException.class,
			() -> mClient.get(new ApiClient.Caller(STEVE, "Steve", 0), 99).get());
		ApiException api = ApiClient.unwrap(e);
		assertEquals(404, api.status());
		assertEquals("Bug #99 not found", api.getMessage());
	}

	@Test
	void nonJsonErrorsGetAStatus() {
		ExecutionException e = assertThrows(ExecutionException.class,
			() -> mClient.send("GET", "/boom", null, null).get());
		assertEquals("HTTP 500", ApiClient.unwrap(e).getMessage());
	}

	@Test
	void unreachableServer() {
		ApiClient dead = new ApiClient("http://127.0.0.1:1", "x", Duration.ofSeconds(2));
		ExecutionException e = assertThrows(ExecutionException.class, () -> dead.info().get());
		assertEquals(0, ApiClient.unwrap(e).status());
	}

	@Test
	void textFromDiscordCantFormatChat() {
		assertEquals("kHiddenr line[2J\nnext", ApiClient.safeText("\u00a7kHidden\u00a7r line\u001b[2J\nnext"));
	}
}

// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 Byron Marohn

package com.playmonumenta.taskbot;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import dev.jorel.commandapi.CommandAPICommand;
import dev.jorel.commandapi.CommandPermission;
import dev.jorel.commandapi.arguments.ArgumentSuggestions;
import dev.jorel.commandapi.arguments.GreedyStringArgument;
import dev.jorel.commandapi.arguments.IntegerArgument;
import dev.jorel.commandapi.arguments.MultiLiteralArgument;
import dev.jorel.commandapi.executors.CommandArguments;
import java.util.List;
import java.util.Map;
import java.util.OptionalInt;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;
import net.kyori.adventure.text.Component;
import net.kyori.adventure.text.format.NamedTextColor;
import org.bukkit.Bukkit;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.permissions.Permission;
import org.bukkit.permissions.PermissionDefault;
import org.bukkit.plugin.Plugin;

/**
 * One task bot (bugs, suggestions, ...) as an in-game command, e.g. /bug.
 *
 * <pre>
 * /bug report &lt;label&gt; &lt;description&gt;   file a report (location is attached for the team)
 * /bug get &lt;n&gt;                 show one
 * /bug search &lt;words&gt;          open reports containing all the words
 * /bug mine                    your own reports
 * /bug append &lt;n&gt; &lt;text&gt;      add to a report's description
 * /bug fix &lt;n&gt; [reason]        close as fixed
 * /bug reject &lt;n&gt; &lt;reason&gt;    close as rejected
 * /bug dupe &lt;n&gt; &lt;original&gt;    close as a duplicate
 * /bug reopen &lt;n&gt;
 * /bug priority &lt;n&gt; &lt;level&gt;   set priority (the priority permission)
 * /bug context &lt;n&gt;            the context attached to a report (team)
 * /bug notify on|off           notices about updates to your reports
 * </pre>
 *
 * Each subcommand checks its own permission (see {@link Operation}).
 */
public class TaskInstance {
	private final Plugin mPlugin;
	private final PluginConfig mConfig;
	private final String mCommand;
	private final ApiClient mApi;
	private volatile InstanceInfo mInfo;
	private final Map<UUID, Long> mLastReport = new ConcurrentHashMap<>();

	public TaskInstance(Plugin plugin, PluginConfig config, PluginConfig.Instance instance, ApiClient api) {
		mPlugin = plugin;
		mConfig = config;
		mCommand = instance.command();
		mApi = api;
		mInfo = InstanceInfo.fallback(mCommand);
	}

	public String command() {
		return mCommand;
	}

	public InstanceInfo info() {
		return mInfo;
	}

	/** Learn the instance's wording from /api/info; retried in the background until it works. */
	public CompletableFuture<Void> loadInfo() {
		return mApi.info().thenAccept(json -> mInfo = InstanceInfo.fromApi(mCommand, json));
	}

	// ------------------------------------------------------------------
	// Registration
	// ------------------------------------------------------------------

	/**
	 * Declares every node so permission plugins can list them. All default to op only: on a
	 * server without a permissions plugin, players get nothing until it is granted.
	 */
	public void registerPermissions() {
		for (Operation op : Operation.values()) {
			addPermission(op.node(mCommand));
			if (op.mOwnable) {
				addPermission(op.ownNode(mCommand));
			}
		}
	}

	private static void addPermission(String node) {
		if (Bukkit.getPluginManager().getPermission(node) == null) {
			Bukkit.getPluginManager().addPermission(new Permission(node, PermissionDefault.OP));
		}
	}

	/** Whether the sender may use any subcommand; without that the command stays hidden. */
	private boolean anyAllowed(CommandSender sender) {
		for (Operation op : Operation.values()) {
			if (op != Operation.NO_COOLDOWN && op.allowed(mCommand, sender::hasPermission)) {
				return true;
			}
		}
		return false;
	}

	/** Registers the command. Needs the tracker's labels, so only after {@link #loadInfo()}. */
	public void register() {
		List<String> labels = mInfo.labels().isEmpty() ? List.of("misc") : mInfo.labels();
		CommandAPICommand root = new CommandAPICommand(mCommand)
			.withRequirement(this::anyAllowed)
			.withSubcommand(sub("report", Operation.CREATE)
				.withArguments(new MultiLiteralArgument("label", labels.toArray(new String[0])),
					new GreedyStringArgument("description"))
				.executesPlayer((Player p, CommandArguments a) -> report(p, (String) a.getUnchecked("label"),
					(String) a.getUnchecked("description"))))
			.withSubcommand(sub("get", Operation.VIEW)
				.withArguments(new IntegerArgument("number", 1))
				.executesPlayer((Player p, CommandArguments a) -> get(p, (Integer) a.getUnchecked("number"))))
			.withSubcommand(sub("search", Operation.VIEW)
				.withArguments(new GreedyStringArgument("words"))
				.executesPlayer((Player p, CommandArguments a) -> search(p, (String) a.getUnchecked("words"))))
			.withSubcommand(sub("mine", Operation.VIEW)
				.executesPlayer((Player p, CommandArguments a) -> mine(p)))
			.withSubcommand(sub("append", Operation.APPEND)
				.withArguments(new IntegerArgument("number", 1), new GreedyStringArgument("text"))
				.executesPlayer((Player p, CommandArguments a) -> act(p, Operation.APPEND, (Integer) a.getUnchecked("number"),
					"append", body("text", (String) a.getUnchecked("text")), "updated")))
			.withSubcommand(sub("fix", Operation.FIX)
				.withArguments(new IntegerArgument("number", 1))
				.withOptionalArguments(new GreedyStringArgument("reason"))
				.executesPlayer((Player p, CommandArguments a) -> act(p, Operation.FIX, (Integer) a.getUnchecked("number"),
					"fix", body("reason", (String) a.getOrDefaultUnchecked("reason", "")), "closed as fixed")))
			.withSubcommand(sub("reject", Operation.REJECT)
				.withArguments(new IntegerArgument("number", 1), new GreedyStringArgument("reason"))
				.executesPlayer((Player p, CommandArguments a) -> act(p, Operation.REJECT, (Integer) a.getUnchecked("number"),
					"reject", body("reason", (String) a.getUnchecked("reason")), "rejected")))
			.withSubcommand(sub("dupe", Operation.DUPE)
				.withArguments(new IntegerArgument("number", 1), new IntegerArgument("original", 1))
				.executesPlayer((Player p, CommandArguments a) -> {
					JsonObject b = new JsonObject();
					b.addProperty("of", (Integer) a.getUnchecked("original"));
					act(p, Operation.DUPE, (Integer) a.getUnchecked("number"), "dupe", b, "closed as a duplicate");
				}))
			.withSubcommand(sub("reopen", Operation.REOPEN)
				.withArguments(new IntegerArgument("number", 1))
				.executesPlayer((Player p, CommandArguments a) -> act(p, Operation.REOPEN, (Integer) a.getUnchecked("number"),
					"reopen", new JsonObject(), "reopened")))
			.withSubcommand(sub("priority", Operation.PRIORITY)
				.withArguments(new IntegerArgument("number", 1),
					// The tracker's own priorities; it matches abbreviations too
					new GreedyStringArgument("level").replaceSuggestions(ArgumentSuggestions.strings(
						info -> mInfo.priorities().toArray(new String[0]))))
				.executesPlayer((Player p, CommandArguments a) -> setPriority(p, (Integer) a.getUnchecked("number"),
					(String) a.getUnchecked("level"))))
			.withSubcommand(sub("context", Operation.CONTEXT)
				.withArguments(new IntegerArgument("number", 1))
				.executesPlayer((Player p, CommandArguments a) -> context(p, (Integer) a.getUnchecked("number"))))
			.withSubcommand(sub("notify", Operation.NOTIFY)
				.withArguments(new MultiLiteralArgument("setting", "on", "off", "status"))
				.executesPlayer((Player p, CommandArguments a) -> notify(p, (String) a.getUnchecked("setting"))));
		root.register();
	}

	private CommandAPICommand sub(String name, Operation op) {
		CommandAPICommand cmd = new CommandAPICommand(name);
		if (op.mOwnable) {
			// Either the full node or the .own node lets the command be used
			return cmd.withRequirement((CommandSender s) -> op.allowed(mCommand, s::hasPermission));
		}
		return cmd.withPermission(CommandPermission.fromString(op.node(mCommand)));
	}

	private static JsonObject body(String key, String value) {
		JsonObject b = new JsonObject();
		b.addProperty(key, value);
		return b;
	}

	// ------------------------------------------------------------------
	// Plumbing
	// ------------------------------------------------------------------

	ApiClient.Caller caller(Player player, Operation op) {
		OptionalInt priv = op.privilegeFor(mCommand, player::hasPermission);
		return new ApiClient.Caller(player.getUniqueId(), player.getName(), priv.orElse(0));
	}

	/** Run on the main thread when the request finishes; API errors are shown to the player. */
	private <T> void then(Player who, CompletableFuture<T> future, Consumer<T> onSuccess) {
		then(who, future, onSuccess, () -> { });
	}

	private <T> void then(Player who, CompletableFuture<T> future, Consumer<T> onSuccess, Runnable onFailure) {
		UUID uuid = who.getUniqueId();
		future.whenComplete((result, err) -> runOnMain(() -> {
			if (err != null) {
				onFailure.run();
			}
			// Looked up again: the player may have relogged while the request ran
			Player player = Bukkit.getPlayer(uuid);
			if (player == null) {
				return;
			}
			if (err != null) {
				ApiException api = ApiClient.unwrap(err);
				if (api.status() == 0 || api.status() >= 500) {
					mPlugin.getLogger().warning(mCommand + ": " + api.getMessage());
					player.sendMessage(Messages.error(mInfo, "The " + mInfo.single() + " tracker can't be reached right now. Please try again later."));
				} else {
					String message = api.getMessage();
					player.sendMessage(Messages.error(mInfo, message != null ? message : "Something went wrong"));
				}
				return;
			}
			onSuccess.accept(result);
		}));
	}

	/** Run on the server thread, unless the plugin was disabled meanwhile (shutdown). */
	private void runOnMain(Runnable task) {
		if (mPlugin.isEnabled()) {
			Bukkit.getScheduler().runTask(mPlugin, task);
		}
	}

	// ------------------------------------------------------------------
	// Commands
	// ------------------------------------------------------------------

	void report(Player player, String label, String description) {
		long now = System.currentTimeMillis();
		Long last = mLastReport.get(player.getUniqueId());
		long cooldownMs = mConfig.reportCooldownSeconds() * 1000L;
		if (last != null && now - last < cooldownMs && !player.hasPermission(Operation.NO_COOLDOWN.node(mCommand))) {
			long wait = (cooldownMs - (now - last) + 999) / 1000;
			player.sendMessage(Messages.error(mInfo, "Please wait " + wait + "s before filing another " + mInfo.single() + "."));
			return;
		}
		// Taken now so a second report can't slip in while this one is sent; given back if it fails
		mLastReport.put(player.getUniqueId(), now);
		UUID uuid = player.getUniqueId();
		JsonObject context = ContextCollector.collect(player, mConfig.serverName(), mPlugin.getPluginMeta().getVersion());
		then(player, mApi.create(caller(player, Operation.CREATE), label, description, context), entry -> {
			int id = entry.get("id").getAsInt();
			player.sendMessage(Messages.prefix(mInfo).append(Component.text(mInfo.proper() + " ", NamedTextColor.GREEN))
				.append(Messages.idLink(mCommand, id))
				.append(Component.text(" filed. Thank you! You'll get a notice here when it's updated.", NamedTextColor.GREEN)));
		}, () -> mLastReport.remove(uuid, now));
	}

	void get(Player player, int id) {
		then(player, mApi.get(caller(player, Operation.VIEW), id), entry -> {
			for (Component line : Messages.detail(mInfo, mCommand, entry)) {
				player.sendMessage(line);
			}
		});
	}

	void search(Player player, String words) {
		then(player, mApi.search(caller(player, Operation.VIEW), words, 8), result -> showList(player, result,
			"open " + mInfo.plural() + " matching \"" + words + "\""));
	}

	void mine(Player player) {
		then(player, mApi.mine(caller(player, Operation.VIEW), 10), result -> showList(player, result,
			"of your " + mInfo.plural()));
	}

	private void showList(Player player, JsonObject result, String what) {
		JsonArray entries = result.getAsJsonArray("entries");
		int total = result.has("total") ? result.get("total").getAsInt() : entries.size();
		if (total == 0) {
			player.sendMessage(Messages.prefix(mInfo).append(Component.text("No " + what + ".", NamedTextColor.GRAY)));
			return;
		}
		player.sendMessage(Messages.prefix(mInfo).append(Component.text(
			(total > entries.size() ? entries.size() + " of " + total : String.valueOf(total)) + " " + what + ":",
			NamedTextColor.YELLOW)));
		for (JsonElement el : entries) {
			player.sendMessage(Messages.line(mCommand, el.getAsJsonObject()));
		}
	}

	void act(Player player, Operation op, int id, String action, JsonObject body, String done) {
		then(player, mApi.act(caller(player, op), id, action, body), entry -> {
			String said = done;
			if ("duplicate".equals(Messages.str(entry, "resolution"))) {
				// fix and reject close as a duplicate when the reason says so ("dupe of #12")
				String original = Messages.str(entry, "duplicate_of");
				said = "closed as a duplicate" + (original.isEmpty() ? "" : " of #" + original);
			}
			player.sendMessage(Messages.ok(mInfo, mInfo.proper() + " #" + id + " " + said));
		});
	}

	void setPriority(Player player, int id, String level) {
		then(player, mApi.patch(caller(player, Operation.PRIORITY), id, body("priority", level)),
			entry -> player.sendMessage(Messages.ok(mInfo, mInfo.proper() + " #" + id + " priority set to "
				+ entry.get("priority").getAsString())));
	}

	void context(Player player, int id) {
		then(player, mApi.context(caller(player, Operation.CONTEXT), id), result -> {
			JsonArray sections = result.getAsJsonArray("context");
			if (sections.isEmpty()) {
				player.sendMessage(Messages.prefix(mInfo).append(Component.text("#" + id + " has no context.", NamedTextColor.GRAY)));
			}
			for (JsonElement el : sections) {
				JsonObject sec = el.getAsJsonObject();
				player.sendMessage(Component.text(sec.get("section").getAsString() + ": ", NamedTextColor.YELLOW)
					.append(Component.text(Messages.oneLine(sec.get("data").toString(), 240), NamedTextColor.WHITE)));
			}
		});
	}

	void notify(Player player, String setting) {
		ApiClient.Caller caller = caller(player, Operation.NOTIFY);
		CompletableFuture<JsonObject> future = "status".equals(setting) ? mApi.getSettings(caller)
			: mApi.setNotifications(caller, "on".equals(setting));
		then(player, future, result -> player.sendMessage(Messages.ok(mInfo,
			result.get("notifications").getAsBoolean()
				? "You will get notices here when your " + mInfo.plural() + " are updated."
				: "You will not get notices about your " + mInfo.plural() + ".")));
	}

	/** Show the player their pending update notices, which the bot marks delivered. Main thread. */
	public void deliverNotices(Player player) {
		UUID uuid = player.getUniqueId();
		mApi.takeNotices(new ApiClient.Caller(uuid, player.getName(), 0)).whenComplete((result, err) -> {
			if (err != null) {
				mPlugin.getLogger().fine(mCommand + ": fetching notices failed: " + ApiClient.unwrap(err).getMessage());
				return;
			}
			runOnMain(() -> {
				Player online = Bukkit.getPlayer(uuid);
				if (online == null) {
					return;
				}
				for (JsonElement el : result.getAsJsonArray("notices")) {
					JsonObject n = el.getAsJsonObject();
					online.sendMessage(Messages.prefix(mInfo).append(Component.text(Messages.str(n, "text") + " ", NamedTextColor.YELLOW))
						.append(Messages.idLink(mCommand, n.get("entry_id").getAsInt())));
				}
			});
		});
	}
}

"""Interactive search sessions (isearch / iroulette), as in the old bot.

A session walks one user through a list of entries. It holds entry ids and
re-reads each entry when showing it, so changes made meanwhile (by the session
itself or anyone else) are always shown current.
"""

from typing import TYPE_CHECKING

from .matching import get_list_match

if TYPE_CHECKING:
    from .commands import CommandHandler, IncomingMessage, Responder

# Order matters to prefix matching; `dupe` is new and goes at the end
SESSION_COMMANDS = ("reject", "edit", "append", "fix", "unfix", "assign", "unassign",
                    "help", "next", "prev", "stop", "dupe")
_FORWARDED = ("reject", "edit", "append", "fix", "unfix", "assign", "unassign", "dupe")

MAX_AUTO_HELP_PROMPTS = 2
MAX_INACTIVE_SECONDS = 60 * 60 * 6


class InteractiveSession:
    def __init__(self, handler: "CommandHandler", author_id: int, entry_ids: list[int]):
        self._handler = handler
        self.author_id = author_id
        self._entries = list(entry_ids)        # still to show
        self._prev_entries: list[int] = []     # [0] is the current one
        self._current_index: int = 0
        self._num_help_prompts = 0
        self._clock = handler.service.now
        self._last_active_time = self._clock()

    def _help_text(self) -> str:
        return f"Valid responses are: ```{' '.join(SESSION_COMMANDS)}```"

    async def _show(self, entry_id: int, responder: "Responder") -> None:
        entry = self._handler.store.get(entry_id)
        if entry is not None:
            await self._handler.show(responder, entry, include_reactions=True)

    async def send_first_message(self, responder: "Responder") -> None:
        await responder.send(f"Started interactive session with {len(self._entries)} entries")
        entry_id = self._entries.pop(0)
        self._prev_entries.insert(0, entry_id)
        self._current_index = entry_id
        await self._show(entry_id, responder)

    async def _auto_help(self, responder: "Responder", closing: str) -> None:
        if self._num_help_prompts < MAX_AUTO_HELP_PROMPTS:
            await responder.send(self._help_text())
            self._num_help_prompts += 1
            if self._num_help_prompts == MAX_AUTO_HELP_PROMPTS:
                await responder.send(closing)

    async def handle_message(self, msg: "IncomingMessage", responder: "Responder") -> bool:
        """True if the message was handled here. Raises EOFError when the session ends."""
        if msg.author_id != self.author_id:
            return False

        if self._clock() - self._last_active_time > MAX_INACTIVE_SECONDS:
            await responder.send("Interactive session aborted due to inactivity")
            raise EOFError

        part = msg.content.split(maxsplit=1)
        if not msg.content or len(part) < 1:
            await self._auto_help(responder, "To see these options again, say `help`")
            return False

        match = get_list_match(part[0].strip(), SESSION_COMMANDS)
        if match is None:
            await self._auto_help(responder, "To see these options again, use 'help'")
            return False

        args = part[1].strip() if len(part) > 1 else ""
        count = 1
        if match in ("next", "prev"):
            try:
                count = max(1, int(args))
            except ValueError:
                count = 1

        if match == "stop":
            await responder.send("Iteration aborted")
            raise EOFError

        if match == "next":
            entry_id = self._current_index
            while count > 0:
                count -= 1
                if not self._entries:
                    await responder.send("No more results to display")
                    raise EOFError
                entry_id = self._entries.pop(0)
                self._prev_entries.insert(0, entry_id)
                self._current_index = entry_id
            await self._show(entry_id, responder)

        elif match == "prev":
            if len(self._prev_entries) < 2:
                await responder.send("Nothing to go back to")
            else:
                while count > 0:
                    count -= 1
                    if len(self._prev_entries) < 2:
                        await responder.send("Reached beginning of list")
                        break
                    self._entries.insert(0, self._prev_entries.pop(0))
                self._current_index = self._prev_entries[0]
                await self._show(self._current_index, responder)

        elif match == "help":
            await responder.send(self._help_text())

        else:
            assert match in _FORWARDED
            await self._handler.run(match, msg, f"{self._current_index} {args}".strip(), responder)

        self._last_active_time = self._clock()
        return True

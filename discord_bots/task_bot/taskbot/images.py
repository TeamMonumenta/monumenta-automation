"""Copies of entry images on disk, so they outlast Discord.

Discord deletes an attachment with the message it was posted in, and images attached to slash
commands expire within a day. The bot saves every image it is given under `images/` next to
the database, one directory per entry (`images/<entry>/<attachment id>-<file name>`), and
records each in `image_files`. The files are the copy of last resort: the team reads them
through the API and `taskctl images`, redacted ones privately in Discord, and `reupload`
posts them again when Discord has lost an image.
"""

import contextlib
import os
import re
import shutil
import tempfile
from collections.abc import Generator
from typing import BinaryIO

_UNSAFE_RE = re.compile(r"[^A-Za-z0-9._-]+")
# Both kinds of attachment URL: /attachments/<channel>/<id>/ and, for images attached to
# slash commands, /ephemeral-attachments/<application>/<id>/
_ATTACHMENT_ID_RE = re.compile(r"/(?:ephemeral-)?attachments/\d+/(\d+)/")
MAX_NAME = 100


def is_ephemeral(url: str) -> bool:
    """Images attached to slash commands, which Discord deletes within a day."""
    return "/ephemeral-attachments/" in url


def file_name(url: str) -> str:
    """`<attachment id>-<name>` for a Discord attachment URL, safe as a file name."""
    path = url.split("?", 1)[0]
    name = _UNSAFE_RE.sub("_", path.rsplit("/", 1)[-1]).strip("._") or "image"
    m = _ATTACHMENT_ID_RE.search(path)
    prefix = f"{m.group(1)}-" if m else ""
    return (prefix + name)[:MAX_NAME]


class ImageArchive:
    def __init__(self, root: str):
        self.root = root

    def relative_path(self, entry_id: int, url: str) -> str:
        return f"{entry_id}/{file_name(url)}"

    def absolute(self, relative: str) -> str:
        path = os.path.normpath(os.path.join(self.root, relative))
        if not path.startswith(os.path.normpath(self.root) + os.sep):
            raise ValueError(f"{relative!r} is outside the image directory")
        return path

    @contextlib.contextmanager
    def writer(self, relative: str) -> Generator[BinaryIO]:
        """A file to write, which appears under its name only once complete, so a crash or
        a failed download never leaves a partial file behind."""
        target = self.absolute(relative)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(target), prefix=".partial-")
        try:
            with os.fdopen(fd, "wb") as f:
                yield f
            os.replace(tmp, target)
        except BaseException:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise

    def write(self, relative: str, data: bytes) -> None:
        with self.writer(relative) as f:
            f.write(data)

    def size(self, relative: str) -> int:
        return os.path.getsize(self.absolute(relative))

    def read(self, relative: str) -> bytes:
        with open(self.absolute(relative), "rb") as f:
            return f.read()

    def remove_entry(self, entry_id: int) -> None:
        """Delete every saved image of an entry (`purge`)."""
        shutil.rmtree(self.absolute(str(entry_id)), ignore_errors=True)

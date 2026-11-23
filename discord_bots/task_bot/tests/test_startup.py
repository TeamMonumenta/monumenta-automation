"""main.open_store and taskbot.db init: the bot only opens a database that already exists."""

import os
import subprocess
import sys
from typing import Any

import pytest

from conftest import make_config
from taskbot import db
from taskbot.store import TaskStore

import main


def _config(tmp_path: Any) -> Any:
    cfg = make_config()
    cfg.config_dir = str(tmp_path)
    return cfg


def test_refuses_to_start_without_a_database(tmp_path: Any) -> None:
    cfg = _config(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main.open_store(cfg)
    assert "taskbot.db init" in str(exc.value)
    assert not os.path.exists(cfg.db_file)


def test_init_then_start(tmp_path: Any) -> None:
    cfg = _config(tmp_path)
    assert db.main(["init", cfg.db_file]) == 0
    store = main.open_store(cfg)
    assert store.labels() == ["misc"] and store.next_index() == 1
    store.close()
    assert db.main(["init", cfg.db_file]) == 1  # never over an existing one


def test_refuses_a_schema_left_by_a_failed_import(tmp_path: Any) -> None:
    cfg = _config(tmp_path)
    TaskStore.open(cfg.db_file).close()  # the schema, nothing else
    with pytest.raises(SystemExit) as exc:
        main.open_store(cfg)
    assert "failed part way" in str(exc.value)


def test_the_bot_needs_no_cutover_code() -> None:
    """legacy, inference and feed go once the cutover is done (README, "Cutover")."""
    code = """
import importlib, pkgutil, sys
import taskbot
CUTOVER = ("taskbot.legacy", "taskbot.inference", "taskbot.feed")
class Block:
    def find_spec(self, name, path=None, target=None):
        if name.startswith(CUTOVER):
            raise ImportError(name + " is cutover code")
sys.meta_path.insert(0, Block())
import main
for m in pkgutil.iter_modules(taskbot.__path__, "taskbot."):
    if not m.name.startswith(CUTOVER):
        importlib.import_module(m.name)
"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr

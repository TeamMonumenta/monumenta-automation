"""main.open_store and taskbot.db init: the bot only opens a database that already exists."""

import os
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


def test_refuses_a_schema_left_by_an_interrupted_init(tmp_path: Any) -> None:
    cfg = _config(tmp_path)
    TaskStore.open(cfg.db_file).close()  # the schema, nothing else
    with pytest.raises(SystemExit) as exc:
        main.open_store(cfg)
    assert "interrupted" in str(exc.value)

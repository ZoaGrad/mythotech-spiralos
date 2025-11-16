from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SDK_SRC = REPO_ROOT / "sdk" / "src"
if str(SDK_SRC) not in sys.path:
    sys.path.insert(0, str(SDK_SRC))

from spiralos_event_logger import EventLogger
from spiralos_event_logger.storage import JSONStorage


def test_logging_and_order(tmp_path: Path):
    storage_path = tmp_path / "events.json"
    logger = EventLogger(storage=JSONStorage(storage_path))

    first_id = logger.log_event("alpha", {"value": 1})
    second_id = logger.log_event("beta", {"value": 2})

    events = logger.retrieve_events()

    assert events[0]["id"] == second_id
    assert events[1]["id"] == first_id
    assert events[0]["name"] == "beta"
    assert events[1]["metadata"]["value"] == 1


def test_json_export(tmp_path: Path):
    storage_path = tmp_path / "events.json"
    export_path = tmp_path / "exported.json"
    logger = EventLogger(storage=JSONStorage(storage_path))

    logger.log_event("alpha", {"value": 1})
    logger.log_event("beta", {"value": 2})

    logger.export_to_json(export_path)

    assert export_path.exists()

    data = json.loads(export_path.read_text())
    assert len(data) == 2
    assert data[0]["name"] == "beta"
    assert data[1]["metadata"]["value"] == 1

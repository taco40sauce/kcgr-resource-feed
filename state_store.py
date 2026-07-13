"""
state_store.py

The pipeline's own internal "database" - a single JSON file on disk,
keyed by identity (callsign:category, e.g. "AA4TE-10:KCGR-FUEL").
"""

import json
from pathlib import Path

STORE_PATH = Path.home() / "kcgr-pipeline" / "data" / "records.json"


def _ensure_store_exists() -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text("{}")


def load_records() -> dict:
    _ensure_store_exists()
    with open(STORE_PATH, "r") as f:
        return json.load(f)


def save_records(records: dict) -> None:
    _ensure_store_exists()
    with open(STORE_PATH, "w") as f:
        json.dump(records, f, indent=2)


def upsert_record(record: dict) -> None:
    records = load_records()
    records[record["identity"]] = record
    save_records(records)


def remove_record(identity: str) -> bool:
    records = load_records()
    if identity in records:
        del records[identity]
        save_records(records)
        return True
    return False


def list_records() -> list:
    return list(load_records().values())

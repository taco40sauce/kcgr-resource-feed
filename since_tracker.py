"""
since_tracker.py

Tracks the timestamp of the last successful pipeline run, so graywolf_client.py
can poll with `since=<last_run>` instead of a fixed `limit=20`.

Why this exists: the fixed-count poll window can miss reports if the shared
APRS-IS feed is busy — a real report can age out of the last 20 packets before
the script gets to it. Tracking an actual timestamp closes that gap.

Usage from graywolf_client.py:

    from since_tracker import get_last_run, set_last_run

    since = get_last_run()  # returns an ISO8601 string, or None on first run
    packets = fetch_packets(since=since, direction="RX")  # your existing API call
    # ... process packets ...
    set_last_run()  # call this only after a successful, fully-processed run
"""

import json
import os
from datetime import datetime, timezone

STATE_FILE = os.path.expanduser("~/kcgr-pipeline/data/last_run.json")


def get_last_run():
    """Returns the ISO8601 timestamp of the last successful run, or None
    if this is the first run ever (no file yet)."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        return data.get("last_run")
    except (json.JSONDecodeError, OSError):
        # Corrupt or unreadable state file — treat as first run rather than crash.
        # Worth a manual look if this ever actually happens.
        return None


def set_last_run(timestamp=None):
    """Records the current time (or a specific timestamp) as the last
    successful run. Call this ONLY after packets were fetched AND fully
    processed (parsed, written to GeoJSON, pushed) — not right after the
    fetch itself. If you stamp it right after fetching, a failure in
    parsing or pushing would silently skip those packets forever."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()

    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    tmp_file = STATE_FILE + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump({"last_run": timestamp}, f)
    os.replace(tmp_file, STATE_FILE)  # atomic write, avoids a half-written file
    return timestamp

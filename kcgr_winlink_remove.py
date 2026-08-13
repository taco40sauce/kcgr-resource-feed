"""
kcgr_winlink_remove.py

Removes one record from the Winlink channel's own record store
(winlink/records.json) - the Winlink-side counterpart to remove_record.py,
which only ever touches the APRS side's data/records.json and has no
visibility into Winlink records at all.

WHY THIS EXISTS: until this script, there was no way to remove a bad
Winlink-sourced report from the public map - not clunky, genuinely
missing. A duplicate, stale, or wrong Winlink report had no removal
path, at any skill level.

WHY IT RUNS HERE (GitHub Actions), NOT THE PI:
Winlink records already live in the repo (written by
kcgr_winlink_poller.py), never on the Pi at all - there's nothing on the
Pi to SSH into for this. Keeping removal off the Pi entirely too, same
direction as everything else moving off Pi-only infrastructure.

ACCESS CONTROL: triggered via GitHub Actions workflow_dispatch, which
already requires write access to the repo to trigger at all - the same
access boundary as anyone else's push permissions. No separate password
system needed, unlike the Pi's admin app (which needs its own because
it's exposed to multiple devices over Tailscale).

This script deliberately does NOT touch git at all - same separation of
concerns as kcgr_winlink_poller.py: this file only reads/writes the JSON
data; the GitHub Actions workflow (winlink-removal.yml) handles
commit/push as its own step.

USAGE (normally via the "KCGR Winlink Report Removal" workflow's inputs,
not run directly):
    python3 kcgr_winlink_remove.py --list
    python3 kcgr_winlink_remove.py <identity>
"""
import json
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
RECORDS_PATH = REPO_DIR / "winlink" / "records.json"


def load_records() -> dict:
    if not RECORDS_PATH.exists():
        return {}
    with open(RECORDS_PATH, "r") as f:
        return json.load(f)


def write_records(records: dict) -> None:
    tmp_path = RECORDS_PATH.with_suffix(".json.tmp")
    with open(tmp_path, "w") as f:
        json.dump(records, f, indent=2)
    tmp_path.replace(RECORDS_PATH)  # atomic write, same pattern as since_tracker.py


def list_records() -> None:
    records = load_records()
    if not records:
        print("No Winlink records currently stored.")
        return
    print(f"{len(records)} Winlink record(s) currently stored:\n")
    for identity, r in records.items():
        print(
            f"  {identity}  |  {r.get('status_mapped', '?')}  |  "
            f"{r.get('location', '?')}  |  received {r.get('received_time', '?')}"
        )


def remove_one(identity: str) -> bool:
    identity = identity.strip()  # guard against a copy-pasted leading/trailing space
    records = load_records()
    if identity not in records:
        return False
    del records[identity]
    write_records(records)
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 kcgr_winlink_remove.py <identity>")
        print("       python3 kcgr_winlink_remove.py --list")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_records()
        return

    identity = sys.argv[1].strip()
    if remove_one(identity):
        print(f"[winlink_remove] Removed: {identity}")
    else:
        print(f"[winlink_remove] No Winlink record found matching identity: {identity}")
        print("Run with action=list first to see all current identities.")
        sys.exit(1)  # non-zero exit -> workflow step shows as failed, not a silent no-op


if __name__ == "__main__":
    main()

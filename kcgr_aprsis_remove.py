"""
kcgr_aprsis_remove.py

Removes one record from the APRS-IS poller's own record store
(backups/records_backup_aprsis.json) - the APRS-IS-side counterpart to
kcgr_winlink_remove.py (Winlink) and remove_record.py (the Pi's own
Graywolf-local-API pipeline, data/records.json). Each of the three
channels now has its own dedicated removal path, matching the
single-writer principle already used for writing these files (§2.3 in
CORE): each channel owns exactly one file, and now each channel also
owns exactly one way to remove from that file.

WHY THIS EXISTS: until this script, there was no way to remove a bad
APRS-IS-sourced report from the public map at all - not clunky,
genuinely missing. This became a real, live-data problem during
testing (8/13-8/14/2026): a test beacon and a leftover debug record
both ended up stuck on the actual public safety feed with only a
manual JSON edit as a stopgap, because no dedicated removal tool
existed for this channel. See CORE §7 and §11 for the incident this
script closes out.

WHY IT RUNS HERE (GitHub Actions), NOT THE PI:
APRS-IS records already live in the repo (written by
kcgr_aprsis_poller.py, itself a GitHub Actions job, not a Pi process) -
there's nothing on the Pi to SSH into for this, same reasoning as
kcgr_winlink_remove.py.

ACCESS CONTROL: triggered via GitHub Actions workflow_dispatch, which
already requires write access to the repo to trigger at all - the same
access boundary as anyone else's push permissions. No separate
password system needed, unlike the Pi's admin app.

This script deliberately does NOT touch git at all - same separation
of concerns as kcgr_winlink_remove.py: this file only reads/writes the
JSON data; the GitHub Actions workflow (aprsis-removal.yml) handles
commit/push as its own step, which is what actually gets
merge-and-publish.yml to auto-trigger and republish the map.

IDENTITY LOOKUP NOTE (added 8/14/2026, per the real padding bug found
this session - see CORE §2.4/§7): identities built before the
parser.py .strip() fix may still contain trailing whitespace in their
stored key (e.g. "AA4TE-10:KCGR-HW  ", two trailing spaces). This
script's own identity argument is stripped before lookup, same as
kcgr_winlink_remove.py already does - but note that stripping the
*input* does NOT let you match a *stored* key that still has trailing
spaces baked into it from before the fix. Use --list first in every
case to copy the exact stored identity string, spaces and all, rather
than typing/assuming what it should be.

USAGE (normally via the "KCGR APRS-IS Report Removal" workflow's
inputs, not run directly):
    python3 kcgr_aprsis_remove.py --list
    python3 kcgr_aprsis_remove.py <identity>
"""

import json
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
RECORDS_PATH = REPO_DIR / "backups" / "records_backup_aprsis.json"


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
        print("No APRS-IS records currently stored.")
        return
    print(f"{len(records)} APRS-IS record(s) currently stored:\n")
    for identity, r in records.items():
        print(
            f"  {identity!r}  |  {r.get('status_mapped', '?')}  |  "
            f"{r.get('location', '?')}  |  received {r.get('received_time', '?')}"
        )
    print(
        "\nNote: identity is printed with repr() (quotes shown) so any "
        "trailing whitespace baked into an older stored key is visible - "
        "copy the identity exactly as shown, including any trailing "
        "spaces inside the quotes, when removing."
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
        print("Usage: python3 kcgr_aprsis_remove.py <identity>")
        print("       python3 kcgr_aprsis_remove.py --list")
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_records()
        return

    identity = sys.argv[1].strip()
    if remove_one(identity):
        print(f"[aprsis_remove] Removed: {identity}")
    else:
        print(f"[aprsis_remove] No APRS-IS record found matching identity: {identity}")
        print("Run with action=list first to see all current identities exactly as stored.")
        sys.exit(1)  # non-zero exit -> workflow step shows as failed, not a silent no-op


if __name__ == "__main__":
    main()

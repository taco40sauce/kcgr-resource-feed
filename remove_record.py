"""
remove_record.py

A small command-line tool to delete one record from the pipeline's own
records store - the fix for a real gap: once the automated pipeline is
running, Grist is bypassed entirely, so there was no way for a human to
remove a forgotten, resolved, or erroneous report. This script is that
missing "delete" button, just as a command instead of a webpage.

(A proper web-based admin page - usable by a future Hub Operator who
isn't comfortable on the command line - is the planned next step after
this. This CLI is the fast, works-today version.)

USAGE:
    python3 remove_record.py AA4TE-10:KCGR-FUEL

    List everything currently stored, if you're not sure of the exact
    identity string to remove:
    python3 remove_record.py --list

CHANGED 8/9/2026: as of 7/13/2026 this regenerated and pushed the
public GeoJSON directly and immediately. As of 8/9/2026, publishing the
public map moved to a separate merge step that runs on GitHub Actions
(see kcgr_merge_and_publish.py) - so removal now pushes the updated
BACKUP, which automatically TRIGGERS that merge step, rather than
rebuilding the map in this same process. In practice this is still
fast (one Actions run, typically under a minute) but it's no longer
instant/synchronous the way it was before - worth knowing if you're
watching the map right after a removal and it doesn't update the
instant this command finishes.
"""

import sys

from state_store import list_records, remove_record
from geojson_writer import run as backup_and_push


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 remove_record.py <identity>")
        print("       python3 remove_record.py --list")
        sys.exit(1)

    if sys.argv[1] == "--list":
        records = list_records()
        if not records:
            print("No records currently stored.")
            return
        print(f"{len(records)} record(s) currently stored:\n")
        for r in records:
            print(
                f"  {r['identity']}  |  {r.get('status_mapped', '?')}  |  "
                f"{r.get('location', '?')}  |  received {r.get('received_time', '?')}"
            )
        return

    identity = sys.argv[1]
    removed = remove_record(identity)

    if removed:
        print(f"Removed: {identity}")
        print("Pushing updated backup to GitHub...")
        backup_and_push()
        print(
            "Done - the merge-and-publish workflow will pick this up "
            "automatically (usually within a minute) and update the "
            "live public map."
        )
    else:
        print(f"No record found matching identity: {identity}")
        print("Run with --list to see all current identities.")


if __name__ == "__main__":
    main()

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

As of 7/13/2026: removing a record now also regenerates the public
GeoJSON file and pushes it to GitHub immediately - so a deletion here
actually disappears from the live map, not just the internal store.
"""

import sys

from state_store import list_records, remove_record
from geojson_writer import run as regenerate_and_push_map


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
        print("Regenerating public map and pushing to GitHub...")
        regenerate_and_push_map()
        print("Done - the public map now reflects this removal.")
    else:
        print(f"No record found matching identity: {identity}")
        print("Run with --list to see all current identities.")


if __name__ == "__main__":
    main()

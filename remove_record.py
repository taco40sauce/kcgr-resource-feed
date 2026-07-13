"""
remove_record.py

A small command-line tool to delete one record from the pipeline's own
records store.

USAGE:
    python3 remove_record.py AA4TE-10:KCGR-FUEL
    python3 remove_record.py --list
"""

import sys

from state_store import list_records, remove_record


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
        print(
            "NOTE: this only updates the internal store for now - the "
            "GeoJSON/GitHub push step isn't wired up yet."
        )
    else:
        print(f"No record found matching identity: {identity}")
        print("Run with --list to see all current identities.")


if __name__ == "__main__":
    main()

"""
kcgr_merge_and_publish.py

Runs on GitHub Actions (NOT the Pi). Reads all three committed record
stores - backups/records_backup.json (Pi-hosted APRS pipeline, backed
up by geojson_writer.py), backups/records_backup_aprsis.json (the
independent APRS-IS poller, added 8/13/2026), and winlink/records.json
(Winlink, written by kcgr_winlink_poller.py) - merges them, and
builds/pushes the one public kcgr_resource_feed.geojson that uMap
actually reads.

WHY THIS RUNS HERE, NOT ON THE PI:
Keeping the final map-build step off the Pi means the public map can
still update even if the Pi/shack loses power - the same reasoning
that already drove the Winlink poller off the Pi. Before this script
existed, geojson_writer.py did this job directly on the Pi; see that
file's docstring for what changed and why (8/9/2026).

WHY IT READS THE *BACKUP*, NOT data/records.json DIRECTLY (Pi-APRS):
data/records.json (the Pi-hosted APRS pipeline's live store) is
.gitignore-excluded - it only ever exists on the Pi's local disk and
is never pushed. backups/records_backup.json is the only Pi-APRS data
that actually reaches the repo, so it's the only copy a GitHub Actions
runner can read at all. This means Pi-APRS data here is always at most
one backup cycle old - a small, known, honest staleness, not a
silent gap. APRS-IS-poller-sourced data has no such staleness, since
it's written directly by the same kind of GitHub Actions runner that
reads it here.

IDENTITY COLLISIONS:
APRS records (both Pi-APRS and APRS-IS) use "callsign:category_wire"
as their identity. Winlink records use
"callsign:category_wire:report_num" (an extra segment, since one
Winlink message can carry up to 3 reports). Winlink's shape can never
collide with either APRS source. Pi-APRS and APRS-IS *can* share the
same identity shape, since both are APRS - so the same real beacon
heard independently by both paths, during any period both are active,
can appear as two entries with the same identity. This is accepted,
not deduplicated: clustering is by geographic proximity, not identity,
so this is treated the same as any other multi-station corroboration
(see CORE §2.3).

Reuses cluster_records() and build_geojson() from geojson_writer.py
directly (imported, not reimplemented) - clustering logic exists in
exactly one place, so every source is always treated identically once
it reaches this step.
"""

import json
import subprocess
from pathlib import Path

from geojson_writer import cluster_records, build_geojson, write_geojson_file

REPO_DIR = Path(__file__).resolve().parent
APRS_BACKUP_PATH = REPO_DIR / "backups" / "records_backup.json"
APRSIS_BACKUP_PATH = REPO_DIR / "backups" / "records_backup_aprsis.json"
WINLINK_RECORDS_PATH = REPO_DIR / "winlink" / "records.json"
GEOJSON_PATH = REPO_DIR / "kcgr_resource_feed.geojson"


def _load_records_dict(path: Path) -> dict:
    """All source files are {identity: record} dicts, same shape
    state_store.py's load_records() produces. Missing file (e.g. no
    Winlink reports have ever come in yet, or the APRS-IS poller
    hasn't heard anything yet) is not an error - just treated as
    empty, same graceful-default pattern used elsewhere."""
    if not path.exists():
        print(f"[merge] {path} doesn't exist yet - treating as empty.")
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[merge] WARNING: {path} is corrupt ({e}) - treating as "
              f"empty rather than crashing. Worth a manual look.")
        return {}


def merge_all_records() -> list:
    aprs_records = _load_records_dict(APRS_BACKUP_PATH)
    aprsis_records = _load_records_dict(APRSIS_BACKUP_PATH)
    winlink_records = _load_records_dict(WINLINK_RECORDS_PATH)
    print(f"[merge] {len(aprs_records)} APRS record(s), "
          f"{len(aprsis_records)} APRS-IS record(s), "
          f"{len(winlink_records)} Winlink record(s).")
    # Identity namespaces can't collide between APRS (either source)
    # and Winlink (see module docstring) - a plain concatenation is
    # correct, not a simplification that happens to work. Pi-APRS and
    # APRS-IS can share identity shape; that's an accepted overlap,
    # not a bug (see module docstring).
    all_records = (
        list(aprs_records.values())
        + list(aprsis_records.values())
        + list(winlink_records.values())
    )
    return all_records


def git_commit_and_push(message: str) -> None:
    try:
        subprocess.run(["git", "add", str(GEOJSON_PATH)], cwd=REPO_DIR, check=True)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=REPO_DIR, capture_output=True, text=True,
        )
        if "nothing to commit" in result.stdout:
            print("[merge] No changes to the public map this run.")
            return
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
        print("[merge] Pushed updated public map to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"[merge] Git operation failed: {e}")
        raise


def run() -> None:
    all_records = merge_all_records()
    clusters = cluster_records(all_records)
    geojson = build_geojson(clusters)
    write_geojson_file(geojson, GEOJSON_PATH)
    git_commit_and_push("Merge step: update public map (APRS + APRS-IS + Winlink)")


if __name__ == "__main__":
    run()

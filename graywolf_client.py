"""
geojson_writer.py

CHANGED 8/9/2026 — role narrowed as part of moving the public map build
off the Pi (see CORE, "merge step" design). This script used to do all
three jobs below; it now does only the first two. The third (CLUSTER +
TRANSLATE + WRITE the actual public GeoJSON) moved to
kcgr_merge_and_publish.py, which runs on GitHub Actions instead of the
Pi — so the public map can still update even if the Pi/shack loses
power, the same reasoning that already drove the Winlink poller off
the Pi.

What this script still does:
  1. BACKUP records.json into the repo (backups/records_backup.json),
     so it survives an SD card failure, per CORE's backup design.
  2. PUSH that backup to GitHub in one commit.

That push is also the trigger for the merge step (see
.github/workflows/merge-and-publish.yml, which fires on any push that
touches backups/records_backup.json OR winlink/records.json) — so a
report still reaches the public map promptly, just via an Actions run
instead of this script doing it directly.

The CLUSTER/TRANSLATE/build_geojson functions below are kept in this
file (not deleted) because kcgr_merge_and_publish.py imports and reuses
them directly — clustering logic exists in exactly one place, so the
two channels can never drift out of sync with each other. This file
just no longer CALLS write_geojson_file() or pushes the .geojson file
itself.

Run this file directly to do a one-time manual backup+push, useful for
testing:
    python3 geojson_writer.py
"""
import json
import math
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from state_store import load_records
from parser import STATUS_MAP, CATEGORY_MAP, SPECIFIER_LABELS

# --- Config --------------------------------------------------------------
REPO_DIR = Path.home() / "kcgr-pipeline"
GEOJSON_PATH = REPO_DIR / "kcgr_resource_feed.geojson"
BACKUP_PATH = REPO_DIR / "backups" / "records_backup.json"
CLUSTER_RADIUS_METERS = 100

# --- Distance helper -------------------------------------------------------
def _haversine_meters(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance between two lat/lon points, in meters."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))

# --- Clustering (Corroboration & Duplicate-Report Handling) ---------------
# Kept here for kcgr_merge_and_publish.py to import - single source of
# truth for clustering logic, used regardless of which channel(s) a
# record came from.
def cluster_records(records: list) -> list:
    clusters = []
    sorted_records = sorted(
        records, key=lambda r: r.get("received_time", ""), reverse=True
    )
    for record in sorted_records:
        placed = False
        for cluster in clusters:
            if cluster["category_wire"] != record["category_wire"]:
                continue
            if record.get("lat") is None or record.get("lon") is None:
                continue
            dist = _haversine_meters(
                cluster["lat"], cluster["lon"], record["lat"], record["lon"]
            )
            if dist <= CLUSTER_RADIUS_METERS:
                cluster["members"].append(record)
                placed = True
                break
        if not placed:
            clusters.append(
                {
                    "category_wire": record["category_wire"],
                    "lat": record["lat"],
                    "lon": record["lon"],
                    "status_mapped": record["status_mapped"],
                    "members": [record],
                }
            )
    for cluster in clusters:
        cluster["report_count"] = len(cluster["members"])
    return clusters

# --- GeoJSON construction ---------------------------------------------------
# Also kept here for kcgr_merge_and_publish.py to import.
def build_geojson(clusters: list) -> dict:
    features = []
    for cluster in clusters:
        category_wire = cluster["category_wire"]
        most_recent = cluster["members"][0]
        contributors = [
            {
                "callsign": m["callsign"],
                "received_time": m.get("received_time"),
                "status_mapped": m["status_mapped"],
                "location": m.get("location", ""),
            }
            for m in cluster["members"]
        ]
        category_labels = SPECIFIER_LABELS.get(category_wire, {})
        specifier_raw = most_recent.get("specifier")
        specifier_mapped = category_labels.get(specifier_raw, specifier_raw or "")
        object_name_mapped = CATEGORY_MAP.get(category_wire, "KCGR-UNKNOWN-unknown")
        name_text = f"{object_name_mapped} — {most_recent.get('location', '')}"
        description_text = (
            f"{cluster['status_mapped']} | {specifier_mapped} | "
            f"Reported: {most_recent.get('timestamp_field', '?')} | "
            f"By: {most_recent.get('callsign', '?')}"
        )
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [cluster["lon"], cluster["lat"]],
            },
            "properties": {
                "ObjectName": object_name_mapped,
                "Status": cluster["status_mapped"],
                "Specifier": specifier_mapped,
                "DateTime": most_recent.get("timestamp_field", ""),
                "ReportedBy": most_recent.get("callsign", ""),
                "ReportCount": cluster["report_count"],
                "Location": most_recent.get("location", ""),
                "Comment": most_recent.get("raw_comment", ""),
                "name": name_text,
                "description": description_text,
                "Contributors": contributors,
            },
        }
        features.append(feature)
    return {
        "type": "FeatureCollection",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "features": features,
    }

def write_geojson_file(geojson: dict, path: Path = GEOJSON_PATH) -> None:
    """Kept for kcgr_merge_and_publish.py's use, and for local manual
    testing - NOT called by run() below anymore as of 8/9/2026."""
    with open(path, "w") as f:
        json.dump(geojson, f, indent=2)
    print(f"[geojson_writer] Wrote {len(geojson['features'])} feature(s) to {path}")

# --- Backup + push (this script's actual job now) ---------------------------
def backup_records_file() -> None:
    BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    records = load_records()
    with open(BACKUP_PATH, "w") as f:
        json.dump(records, f, indent=2)
    print(f"[geojson_writer] Backed up records store to {BACKUP_PATH}")

def git_commit_and_push(message: str) -> None:
    try:
        subprocess.run(
            ["git", "add", str(BACKUP_PATH)],
            cwd=REPO_DIR, check=True,
        )
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=REPO_DIR, capture_output=True, text=True,
        )
        if "nothing to commit" in result.stdout:
            print("[geojson_writer] No changes to commit.")
            return
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=REPO_DIR, check=True,
        )
        print("[geojson_writer] Pushed backup to GitHub - this triggers "
              "the merge-and-publish workflow automatically.")
    except subprocess.CalledProcessError as e:
        print(f"[geojson_writer] Git operation failed: {e}")
        raise

# --- Full pipeline step ------------------------------------------------------
def run() -> None:
    """As of 8/9/2026: backs up + pushes records.json only. Does NOT
    build or push the public kcgr_resource_feed.geojson anymore - that
    now happens in kcgr_merge_and_publish.py, triggered automatically
    by the push this function makes. See module docstring."""
    backup_records_file()
    git_commit_and_push("Update KCGR records backup")

if __name__ == "__main__":
    run()

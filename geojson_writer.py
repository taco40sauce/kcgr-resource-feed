"""
geojson_writer.py

Takes everything currently in the pipeline's record store and turns it
into the one GeoJSON file uMap's Remote Data layer reads. This is the
piece that actually makes reports show up on the public map.

Three jobs, done in order:
  1. CLUSTER corroborating reports (same category, physically close
     together) into a single map pin, per CORE's "Corroboration &
     Duplicate-Report Handling" design - so 3 operators reporting the
     same shelter show as ONE pin with a count, not 3 overlapping pins.
  2. TRANSLATE wire-format codes (e.g. "OP", "KCGR-FUEL") into the exact
     property strings uMap's conditional style rules require (e.g.
     "OP-open", "KCGR-FUEL-fuel"). Property names ("Status", "ObjectName")
     must match exactly what the style rules check against.
  3. WRITE the GeoJSON file, back up records.json into the repo (so it
     survives an SD card failure, per CORE's backup design), and PUSH
     both to GitHub in one commit.

Run this file directly to do a one-time manual write+push, useful for
testing before it's wired into a continuously-running service:
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


# --- Write + backup + push --------------------------------------------------

def write_geojson_file(geojson: dict) -> None:
    with open(GEOJSON_PATH, "w") as f:
        json.dump(geojson, f, indent=2)
    print(f"[geojson_writer] Wrote {len(geojson['features'])} feature(s) to {GEOJSON_PATH}")


def backup_records_file() -> None:
    BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    records = load_records()
    with open(BACKUP_PATH, "w") as f:
        json.dump(records, f, indent=2)
    print(f"[geojson_writer] Backed up records store to {BACKUP_PATH}")


def git_commit_and_push(message: str) -> None:
    try:
        subprocess.run(
            ["git", "add", str(GEOJSON_PATH), str(BACKUP_PATH)],
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
        print("[geojson_writer] Pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"[geojson_writer] Git operation failed: {e}")
        raise


# --- Full pipeline step ------------------------------------------------------

def run() -> None:
    records = list(load_records().values())
    clusters = cluster_records(records)
    geojson = build_geojson(clusters)

    write_geojson_file(geojson)
    backup_records_file()
    git_commit_and_push("Update KCGR resource feed")


if __name__ == "__main__":
    run()

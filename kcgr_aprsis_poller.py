"""
kcgr_aprsis_poller.py

Runs on GitHub Actions (not the Pi). Connects to APRS-IS directly -
the shared, internet-accessible regional APRS feed - instead of
Graywolf's local REST API, which only exists on the Pi's LAN and can't
be reached from a GitHub-hosted runner.

WHY THIS EXISTS (per CORE Sec 2.4 / 8/13/2026 planning):
Right now, APRS capture has a single point of failure: if the Pi is
down, capture stops entirely, even though other stations nearby may
still be hearing the same beacon. Reading from APRS-IS instead means
capture keeps working as long as ANY nearby iGate hears the report -
not just this club's own Pi. Radio reception itself (Graywolf <->
IC-7100) is physically tied to the Pi by hardware and cannot move;
this script does not touch that. It's a second, independent capture
path for the same over-the-air beacons, not a replacement for Graywolf.

WHY IT REUSES parser.py UNCHANGED:
is_kcgr_object() and build_record() already encode the real, tested
KCGR grammar and translation tables. Rather than re-implement that
logic against a different data source, this script only adapts
aprslib's parsed packet shape into the same
{"decoded": {"Object": {...}, "Source": ...}, "lat", "lon", "timestamp"}
shape parser.py already expects (see _adapt_packet below) - confirmed
field-for-field against a real aprslib.parse() call before writing
this, not assumed. This is the same "reuse, don't reinvent" principle
CORE already used for the Winlink side, so the three channels can't
drift out of sync with each other.

WHY A SEPARATE OUTPUT FILE (operator decision, 8/13/2026):
This script writes ONLY backups/records_backup_aprsis.json - a new,
separate file from the Pi's own backups/records_backup.json. This is
deliberate: it lets the new APRS-IS path run in parallel with the
Pi's live, working pipeline for a real side-by-side comparison, with
zero risk to the live public map. This file is NOT yet read by
kcgr_merge_and_publish.py and NOT yet wired into that workflow's
`workflow_run` trigger list - both of those are the intentional,
separate "cutover" step, to be done only once the operator has
compared this file's output against the Pi's for a real report and
is satisfied it's working correctly. Do not wire this in without that
decision being made on purpose.

APRS-IS LOGIN:
Uses APRS-IS's standard receive-only convention: passcode -1, which
is deliberately unverified and requires no real credential - so this
script needs NO repository secret at all. APRSIS_CALLSIGN is not a
secret; it's just the identifier this listen-only client presents to
the network, and defaults to the club's own callsign as a courtesy.
Override via the APRSIS_CALLSIGN environment variable if needed.

FILTER:
Uses APRS-IS's server-side range filter (r/lat/lon/km) centered on
Kershaw County rather than pulling the entire national feed - keeps
the connection light while still catching the neighboring iGates
already identified in CORE as real coverage. Adjust CENTER_LAT/
CENTER_LON/RADIUS_KM below if real-world coverage testing shows it
needs to be wider.

LISTEN WINDOW:
GitHub Actions runs this on a schedule, not continuously, so the
script connects, listens for a fixed window, then disconnects and
writes whatever it collected - same run-cadence idea as the Winlink
poller, just with an active listen instead of a mailbox search.

USAGE:
    python3 kcgr_aprsis_poller.py                  # normal run
    python3 kcgr_aprsis_poller.py --dry-run         # listen and print
                                                       only, write nothing
    python3 kcgr_aprsis_poller.py --listen-seconds 30  # override window,
                                                          useful for local
                                                          testing
"""

import argparse
import json
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

import aprslib

from parser import is_kcgr_object, build_record

# --- Config ------------------------------------------------------------

APRSIS_HOST = "rotate.aprs.net"
APRSIS_PORT = 14580
# MUST be 14580, not aprslib's own default of 10152: per aprs-is.net's
# own documentation, 10152 is the UNFILTERED full global feed - the
# filter set below is silently ignored there (the server's own login
# response literally says "# No user-specified filters on this port").
# 14580 is the user-defined filter port, where the r/lat/lon/km filter
# below actually takes effect. Confirmed live 8/13/2026: a real run on
# 10152 received an out-of-region packet (a station in South America)
# despite the Kershaw-County-only filter being set, which is exactly
# what "filter silently ignored" looks like in practice.
APRSIS_PASSCODE = "-1"  # receive-only, unverified - no credential needed.
# MUST be the string "-1", not the integer -1: aprslib's own login-success
# check does `self.passwd != "-1"` (a string comparison), so an integer
# -1 never equals it and every login attempt fails with "Password is
# incorrect" - confirmed against the real aprslib source (0.7.2) after a
# real failed run showed exactly that message, 8/13/2026.

# Kershaw County, SC (Camden, the county seat) - adjust if real-world
# coverage testing shows a different center/radius makes more sense.
CENTER_LAT = 34.2497
CENTER_LON = -80.6073
RADIUS_KM = 50

LISTEN_SECONDS_DEFAULT = 75  # comfortably under the 15-min run cadence

REPO_DIR = Path(__file__).resolve().parent
BACKUP_PATH = REPO_DIR / "backups" / "records_backup_aprsis.json"


# --- JSON helpers (same atomic-write pattern as kcgr_winlink_poller.py) ---

def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[aprsis_poller] WARNING: couldn't read {path} ({e}) - "
              f"treating as empty. Worth a manual look if this persists.")
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)  # atomic write


# --- Adapter: aprslib's parsed shape -> the shape parser.py expects -----

def _adapt_packet(parsed: dict) -> dict:
    """
    Reshapes an aprslib-parsed object-beacon dict into the same
    {"decoded": {"Object": {"Name", "Comment"}, "Source"}, "lat", "lon",
    "timestamp"} shape parser.py's is_kcgr_object()/build_record()
    already expect from Graywolf's API - confirmed field-for-field
    against a real aprslib.parse() call (raw APRS object beacon string)
    before this was written:
        object_name -> decoded.Object.Name
        comment     -> decoded.Object.Comment  (already extracted by
                        aprslib - no manual parsing needed here)
        from        -> decoded.Source  (includes SSID, e.g. "AA4TE-10",
                        matching the format parser.py already expects)
        latitude/longitude -> lat/lon
    received_time is stamped as "now" (when THIS script saw the packet),
    not the beacon's own embedded DDHHMM timestamp - consistent with how
    the Winlink side stamps received_time as poll time, not report time.
    """
    return {
        "type": "object",
        "decoded": {
            "Object": {
                "Name": parsed.get("object_name", ""),
                "Comment": parsed.get("comment", ""),
            },
            "Source": parsed.get("from", "UNKNOWN"),
        },
        "lat": parsed.get("latitude"),
        "lon": parsed.get("longitude"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# --- Listening ------------------------------------------------------------

def listen_for_kcgr_objects(listen_seconds: int, callsign: str) -> list:
    """
    Connects to APRS-IS, listens for `listen_seconds`, and returns a
    list of built KCGR records for every KCGR-* object beacon seen.
    Deliberately does NOT filter on the object's alive/killed flag -
    per CORE, a kill message has never affected this pipeline's data
    (parser.py has no kill-signal handling at all; kill messages only
    affect the APRS/aprs.fi RF display side), so this stays consistent
    with that existing, deliberate behavior rather than introducing a
    new filtering rule the rest of the pipeline doesn't share.
    """
    collected = []

    def _on_packet(raw_packet):
        try:
            parsed = aprslib.parse(raw_packet)
        except (aprslib.exceptions.ParseError, aprslib.exceptions.UnknownFormat):
            return  # not every packet on the feed is well-formed - skip, don't crash
        if parsed.get("format") != "object":
            return
        adapted = _adapt_packet(parsed)
        if not is_kcgr_object(adapted):
            return
        record = build_record(adapted)
        collected.append(record)
        flag = "" if record["parsed_cleanly"] else " (DEGRADED - needs review)"
        print(f"[aprsis_poller] Heard: {record['identity']}{flag}")

    ais = aprslib.IS(callsign, passwd=APRSIS_PASSCODE, host=APRSIS_HOST, port=APRSIS_PORT)
    ais.set_filter(f"r/{CENTER_LAT}/{CENTER_LON}/{RADIUS_KM}")

    # window_elapsed distinguishes an EXPECTED end-of-listen-window
    # shutdown from a REAL connection failure. Closing a socket out from
    # under a blocking read (from this Timer, on a separate thread) is
    # inherently a race: depending on exactly where the main thread is
    # when the close happens, aprslib/the OS can raise different
    # exception types - ConnectionDrop most of the time, but a real run
    # (8/13/2026) instead hit a ValueError from select() on a torn-down
    # file descriptor, which a narrower except clause didn't catch and
    # crashed the whole run. Rather than enumerate every exception type
    # this race could possibly produce, the flag below just checks WHEN
    # the exception happened: after the window elapsed, any exception is
    # the expected shutdown; before it, any exception is a real problem.
    window_elapsed = threading.Event()

    def _end_listen_window():
        window_elapsed.set()
        ais.close()

    timer = threading.Timer(listen_seconds, _end_listen_window)
    timer.start()
    try:
        ais.connect(blocking=True)
        ais.consumer(_on_packet, raw=True, blocking=True, immortal=False)
    except Exception as e:
        if window_elapsed.is_set():
            print(f"[aprsis_poller] Listen window ended ({type(e).__name__}) - normal.")
        else:
            print(f"[aprsis_poller] APRS-IS connection problem before the "
                  f"listen window elapsed: {type(e).__name__}: {e}. "
                  f"Returning whatever was collected before the failure "
                  f"({len(collected)} record(s)) rather than discarding it.")
    finally:
        timer.cancel()

    return collected


# --- Main -------------------------------------------------------------

def run(dry_run: bool = False, listen_seconds: int = LISTEN_SECONDS_DEFAULT) -> int:
    callsign = os.environ.get("APRSIS_CALLSIGN", "KC4RC")

    print(f"[aprsis_poller] Connecting to {APRSIS_HOST}:{APRSIS_PORT} as {callsign}, "
          f"filter r/{CENTER_LAT}/{CENTER_LON}/{RADIUS_KM}, "
          f"listening {listen_seconds}s...")

    new_records = listen_for_kcgr_objects(listen_seconds, callsign)

    if not new_records:
        print("[aprsis_poller] No KCGR-* object beacons heard this run.")
        return 0

    if dry_run:
        print(f"[aprsis_poller] DRY RUN - {len(new_records)} record(s) heard, "
              f"nothing written.")
        return 0

    records_store = _load_json(BACKUP_PATH, {})
    for record in new_records:
        records_store[record["identity"]] = record

    _write_json(BACKUP_PATH, records_store)
    print(f"[aprsis_poller] Wrote {len(records_store)} total record(s) to "
          f"{BACKUP_PATH.relative_to(REPO_DIR)}.")
    return 0


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--dry-run", action="store_true")
    arg_parser.add_argument("--listen-seconds", type=int, default=LISTEN_SECONDS_DEFAULT)
    args = arg_parser.parse_args()

    sys.exit(run(dry_run=args.dry_run, listen_seconds=args.listen_seconds))

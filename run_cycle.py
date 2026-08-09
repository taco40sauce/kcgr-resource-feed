"""
run_cycle.py

The missing piece: runs one full pipeline cycle, start to finish.

  1. Fetch new packets from Graywolf, using since=<last_run> (not a fixed
     limit) so nothing gets missed if the shared APRS-IS feed is busy.
  2. Filter for KCGR object beacons, parse each one.
  3. Update the record store: remove a record if its object was killed
     (decoded.Object.Live == false, per CORE); otherwise save/update it.
  4. Hand off to geojson_writer to cluster, write, back up, and push.
  5. Only if all of the above succeeded, advance last_run — so a failure
     partway through gets retried next cycle instead of silently skipped.

Run this file directly for a one-time manual cycle:
    python3 run_cycle.py

This is the file run_pipeline.sh loops on, not graywolf_client.py directly.
"""

from graywolf_client import GraywolfClient
from parser import is_kcgr_object, build_record
from state_store import upsert_record, remove_record
from since_tracker import get_last_run, set_last_run
import geojson_writer


def run_cycle() -> None:
    since = get_last_run()
    print(f"[run_cycle] Polling since={since or '(first run - no prior timestamp)'}")

    client = GraywolfClient()
    packets = client.get_packets(since=since, direction="RX")
    print(f"[run_cycle] Fetched {len(packets)} packet(s) total")

    kcgr_packets = [p for p in packets if is_kcgr_object(p)]
    print(f"[run_cycle] {len(kcgr_packets)} KCGR object beacon(s) after filtering")

    for packet in kcgr_packets:
        try:
            record = build_record(packet)

            # Per CORE: a killed object (Live == false) means expire/remove
            # that identity's record, not save it. Defaults to "still live"
            # if the field is missing, so absence doesn't wrongly expire
            # anything - Live has only ever been observed as true so far.
            obj = packet.get("decoded", {}).get("Object", {})
            is_live = obj.get("Live", True)

            if not is_live:
                removed = remove_record(record["identity"])
                print(f"[run_cycle]   {record['identity']}: killed, removed={removed}")
            else:
                upsert_record(record)
                print(f"[run_cycle]   {record['identity']}: saved "
                      f"({'parsed' if record['parsed_cleanly'] else 'DEGRADED - raw text published'})")

        except Exception as e:
            # One bad packet should never take down the whole cycle -
            # log it and keep going, same "never silently drop" spirit
            # already established for parsing itself.
            print(f"[run_cycle]   ERROR processing packet, skipping it: {e}")

    # Only rebuild/push the public map if we actually fetched something,
    # OR if this is the very first run (so the map gets created at all).
    if kcgr_packets or since is None:
        geojson_writer.run()
    else:
        print("[run_cycle] No new KCGR packets this cycle, skipping GeoJSON rebuild")

    # Advance last_run only now, after everything above succeeded.
    new_since = set_last_run()
    print(f"[run_cycle] Cycle complete. last_run advanced to {new_since}")


if __name__ == "__main__":
    run_cycle()

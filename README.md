# KCGR Resource Feed / KCGR-Resource Statu

Automated pipeline turning ham radio APRS and Winlink ground reports (KCGR: Kershaw
County Ground Report) into a real-time public emergency resource map —
shelters, roads, water, fuel, power, and more.


Built for KC4RC / Kershaw County EmComm on a Raspberry Pi running
[Graywolf](https://github.com/chrissnell/graywolf) APRS software.
**Open source for any ARES/EmComm group to use or adapt.**

## Why this exists

During Hurricane Helene, ham-collected situational reports mostly went
to agencies and disappeared from public view. This project's goal:
have a pipeline in place *before* the next major hurricane, so ground
reports are visible to formal agencies and the public at the same time
— no gatekeeper, no single point of failure.

## How it works

```
Ham radio operator sends an APRS object beacon (e.g. "KCGR-FUEL")
        │
        ▼
Graywolf (on the Pi) receives it, exposes it via a local REST API
        │
        ▼
This pipeline polls the API, parses the report, translates codes
        │
        ▼
Corroborating reports (same site, different operators) are merged
into a single map pin with a "reported by N operators" count
        │
        ▼
A GeoJSON file is written and pushed to this GitHub repo
        │
        ▼
uMap's "Remote Data" layer reads that file and renders it on the
public KCGR map
```

No spreadsheet, no manual data entry, no gatekeeper between a report
being radioed in and it appearing on the public map.

## Status (as of Augus 2026)

Working end-to-end for a multiple manual test runs. Not yet tested as an
unattended, continuously-scheduled service under diress — currently triggered by
hand, on the Pi, via the commands below. Turning this into a proper
always-on service (likely `systemd`) is the next planned step.

## Files

| File | Purpose |
|---|---|
| `graywolf_client.py` | Logs into Graywolf's local API, polls for packets |
| `parser.py` | Filters for KCGR object beacons, parses the report grammar, translates wire codes into map-ready values |
| `state_store.py` | The pipeline's own simple "database" - one JSON file, keyed by `callsign:category` |
| `geojson_writer.py` | Clusters corroborating reports, builds the GeoJSON, backs up the record store, pushes to GitHub |
| `remove_record.py` | Manual admin tool - deletes a record and republishes the map |
| `credentials.env.example` | Template for the (never-committed) real credentials file |

## Setup

1. Clone this repo onto the Pi running Graywolf.
2. Copy `credentials.env.example` to `~/.kcgr_secrets/credentials.env`
   (**outside** this repo) and fill in your real Graywolf login.
3. Install dependencies:
   ```
   pip install -r requirements.txt --break-system-packages
   ```
4. Set up a GitHub deploy key scoped to this one repo, with write
   access, so the Pi can push updates without needing broader account
   access. (SSH host alias example: add a `github-kcgr` entry to
   `~/.ssh/config` pointing at the deploy key.)

## Running it manually (current state)

```bash
# Pull recent packets, store any new KCGR reports:
python3 -c "
from graywolf_client import GraywolfClient
from parser import is_kcgr_object, build_record
from state_store import upsert_record

c = GraywolfClient()
c.login()
packets = c.get_packets(packet_type='object', limit=20)
for p in packets:
    if is_kcgr_object(p):
        upsert_record(build_record(p))
"

# Build and publish the map:
python3 geojson_writer.py
```

To remove a record (e.g. a resolved or erroneous report):
```bash
python3 remove_record.py --list
python3 remove_record.py <identity>
```

## KCGR report format

Reports are APRS object beacons named `KCGR-<CATEGORY>` (e.g.
`KCGR-FUEL`, `KCGR-SHLT`, `KCGR-ROAD`), with a comment field formatted
as:

```
ST SPEC LOCATION DDHHMM
```

- `ST` — 2-letter status code (OP/CL/LM/CA/UK)
- `SPEC` — 2-letter category-specific specifier code
- `LOCATION` — free-text place description
- `DDHHMM` — day/hour/minute timestamp (optional, can be shortened or omitted)

- ## Winlink report format

Reports can also be filed via Winlink, using a three-file form set stored
in `winlink_forms/`:

- `KCGR_ResourceStatus.txt` — the message template. Defines the subject
  line and plain-text message body, with `<var FieldName>` placeholders
  that get filled in from the entry form. This is what a receiving
  station sees if it doesn't have the entry/display forms installed —
  nothing is lost, it just isn't rendered prettily.
- `KCGR_ResourceStatus_Entry.html` — the fillable form a sender fills
  out and submits. Supports up to 3 report blocks per message (same
  category/status/specifier/location/date/time/notes/lat/long fields as
  the APRS grammar above), so multiple observations can go in one
  message.
- `KCGR_ResourceStatus_Display.html` — a read-only rendering shown to
  the *receiving* station once a report comes in, formatted to match
  the entry form.
- `KCGR_FormStyle.css` — legacy external stylesheet, kept for reference.
  Current entry/display forms embed their CSS directly instead
  (avoids a `{FormFolder}` path-substitution bug in some clients), so
  this file is no longer referenced by them.

**To install (Pat):** copy all files into
`~/.local/share/pat/Standard_Forms/kcgr_forms/`.

**To install (Winlink Express):** copy all files into
`C:\RMS Express\Global Folders\Templates\KCGR\`.

Once installed, select the KCGR Resource Status template from the
client's message-template picker when composing a new message. Reports
should be addressed to `KCGR-OPS`, a Winlink tactical address that
auto-forwards incoming reports to the Hub Operator without requiring
anyone to check in via telnet or RF. Per KCGR's vetting policy, Winlink
reports from any FCC-licensed amateur callsign are auto-vetted and
posted on receipt, same as APRS.

A report that doesn't fully match this format is never discarded — it
still gets published, with status forced to "unknown," so a report
from an untrained operator is always better than no report at all.

## License

MIT — see `LICENSE`.


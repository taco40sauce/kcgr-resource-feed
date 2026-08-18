# KCGR Resource Feed / KCGR-Resource Status

Automated pipeline turning ham radio APRS and Winlink ground reports (KCGR: Kershaw
County Ground Report) into a real-time public emergency resource map —
shelters, roads, water, fuel, power, and more.

Built for KC4RC / Kershaw County EmComm, originally on a Raspberry Pi running
[Graywolf](https://github.com/chrissnell/graywolf) APRS software.
**Open source for any ARES/EmComm group to use or adapt.**

## Relationship to the manual

This README documents the *code repository* — what's here, how to set
it up, and how the pieces fit together technically. It is not the
operations manual. If you're looking for how to actually run this
system day to day — activation/wind-down procedures, data entry
standards, validator workflow, troubleshooting, succession planning, or
how to adapt this for your own county or region — see
`FULL-KCGR-MANUAL.md` in this repo instead. That manual assumes this
README as background, not the other way around.

## Why this exists

During Hurricane Helene, ham-collected situational reports mostly went
to agencies and disappeared from public view. This project's goal:
have a pipeline in place *before* the next major hurricane, so ground
reports are visible to formal agencies and the public at the same time
— no gatekeeper, no single point of failure.

## How it works

This system runs **three independent automated capture channels**,
each on its own schedule, merged into one shared public map — plus a
fourth, fully independent reporting path:

1. **Pi / Graywolf** — local hardware, intended as an optional fallback
2. **APRS-IS poller** — runs on GitHub Actions, independent of any local Pi
3. **Winlink poller** — runs on GitHub Actions, polls a shared inbox via IMAP

All three feed into one shared step:

**Merge & publish** — corroborates reports across channels, writes the
GeoJSON, pushes to GitHub
       ↓
**uMap's "Remote Data" layer** renders it on the public KCGR map

**A fourth, fully independent channel** runs in parallel: hand-entered
reports in a shared Grist database, published through their own
separate uMap layer — this path doesn't touch this repo's code or
GeoJSON pipeline at all, and keeps working even if this entire repo's
infrastructure is down.

No spreadsheet, no manual data entry required for the automated
channels, no gatekeeper between a report being radioed (or Winlink'd)
in and it appearing on the public map.

## Status (as of 8/17/2026)

**Live and running automatically**, not a manually-triggered prototype:
- The **APRS-IS poller** and **Winlink poller** each run on their own
  15-minute schedule via GitHub Actions, entirely independent of any
  local hardware — confirmed end-to-end 8/12/2026 and 8/13/2026
  respectively.
- The **Pi's own local Graywolf pipeline** still exists and still
  works, but is intended to become an optional fallback rather than the
  primary path — it runs as a `systemd` service (`kcgr-pipeline`),
  toggled on/off manually via an admin web app, off by default.
- A browser-based **removal panel** (`/records` route in `admin_app.py`)
  is live and tested, covering the APRS-IS and Winlink channels; the
  Pi's own local channel still requires the manual `remove_record.py`
  script (see below).

**Still genuinely open, not yet done:**
- A real end-to-end test of the Pi's own local pipeline under its
  *unattended*, scheduled 15-minute cron (rather than a manually timed
  run) hasn't been completed yet.
- Confirming a real report reaches APRS-IS via a genuinely independent
  iGate — not this Pi's own gate — which is the actual point of that
  channel's redundancy.

## Files

| File | Purpose |
|---|---|
| `graywolf_client.py` | Logs into Graywolf's local API, polls for packets (Pi-local channel) |
| `kcgr_aprsis_poller.py` | Independent APRS-IS capture, runs on GitHub Actions, no local hardware dependency |
| `kcgr_winlink_poller.py` | Connects to the shared Gmail inbox via IMAP, polls for Winlink reports |
| `kcgr_winlink_parser.py` | Parses labeled Winlink message bodies, reusing `parser.py`'s translation tables directly |
| `parser.py` | Filters for KCGR object beacons, parses the report grammar, translates wire codes into map-ready values — shared by all radio-based channels |
| `state_store.py` | The pipeline's own simple "database" — one JSON file per channel, keyed by `callsign:category` |
| `kcgr_merge_and_publish.py` | Merges all channels' saved records, clusters corroborating reports, builds the shared GeoJSON, pushes to GitHub |
| `geojson_writer.py` | Backs up a channel's own record store as part of the merge/publish step |
| `admin_app.py` | Web-based admin app: pipeline on/off toggle, and the `/records` removal panel |
| `remove_record.py` | Manual terminal tool — the *only* removal path currently available for the Pi's own local channel |
| `setup_pat.py` | Standalone, stdlib-only tool — validates a new GitHub P.A.T. against the repo and its workflows before it's trusted; run on your own machine, not the Pi |
| `credentials.env.example` | Template for the (never-committed) real credentials file |
| `winlink_forms/` | Template Winlink reports, tested with Winlink Express and the Pat Linux client (www.getpat.io) |

## Setup

1. Clone this repo onto the machine that will run it (a Pi, if using
   the local Graywolf channel; otherwise GitHub Actions handles the
   APRS-IS and Winlink channels without any local hardware at all).
2. Copy `credentials.env.example` to `~/.kcgr_secrets/credentials.env`
   (**outside** this repo) and fill in your real credentials for
   whichever channels you're running.
3. Install dependencies:
```bash
pip install -r requirements.txt --break-system-packages
```

   4. If running the Pi-local channel: set up a GitHub deploy key scoped
   to this one repo, with write access, so the Pi can push updates
   without needing broader account access. (SSH host alias example:
   add a `github-kcgr` entry to `~/.ssh/config` pointing at the deploy
   key.) **This is separate from the GitHub Personal Access Token
   (P.A.T.) used by the admin removal panel** — the two credentials
   serve different purposes and aren't interchangeable.
5. If using the admin removal panel: generate your own P.A.T. following
   the manual's §6.8, then optionally validate it with `setup_pat.py`
   before pasting it into your credentials file.

## Running channels manually (for testing/debugging)

The APRS-IS and Winlink channels normally run unattended on their own
15-minute GitHub Actions schedule — you shouldn't need to trigger them
by hand in normal operation. The commands below are for testing a
channel directly, or for the Pi's own local channel, which still
requires the manual toggle described in the manual's Part II.

```bash
# Pull recent packets, store any new KCGR reports (Pi-local channel):
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
```

# Build and publish the map (merges all channels' current data):
```bash
python3 kcgr_merge_and_publish.py
```

To remove a record from the Pi's own local channel (the only channel
without a browser-based removal option — see the manual for the others):
```bash
python3 remove_record.py --list
python3 remove_record.py <identity>
```

## KCGR report format

Reports are APRS object beacons named `KCGR-<CATEGORY>` (e.g.
`KCGR-FUEL`, `KCGR-SHLT`, `KCGR-ROAD`), with a comment field formatted
as:
       ST  SPEC  LOCATION  DDHHMM
- `ST` — 2-letter status code (OP/CL/LM/CA/UK)
- `SPEC` — 2-letter category-specific specifier code
- `LOCATION` — free-text place description
- `DDHHMM` — day/hour/minute timestamp (optional, can be shortened or omitted)

## Winlink report format

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
  
  **No form installed?** Use `winlink_forms/KCGR_NoForm_Winlink_Template.md`
instead — a plain-text, copy/paste version of the same report that
doesn't require any client-side form software.

**To install (Pat):** copy all files into
`~/.local/share/pat/Standard_Forms/kcgr_forms/`.

**To install (Winlink Express):** copy all files into
`C:\RMS Express\Global Folders\Templates\KCGR\`.

Once installed, select the KCGR Resource Status template from the
client's message-template picker when composing a new message. Reports
should be addressed to `KCGR-OPS`, a Winlink tactical address. Incoming
messages land in a shared Gmail inbox; the automated Winlink poller
(running on its own 15-minute GitHub Actions schedule) checks that
inbox and publishes directly to the map — no one needs to check in via
telnet or RF, and no human needs to manually process each message.
Per KCGR's vetting policy, Winlink reports from any FCC-licensed
amateur callsign are auto-vetted and posted on receipt, same as APRS.

A report that doesn't fully match this format is never discarded — it
still gets published, with status forced to "unknown," so a report
from an untrained operator is always better than no report at all.

## License

MIT — see `LICENSE`.

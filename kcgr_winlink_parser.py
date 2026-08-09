"""
kcgr_winlink_parser.py

Parses the plain-text body of a KCGR_ResourceStatus Winlink message into
the same record shape parser.py already produces for APRS beacons, so
geojson_writer.py's clustering/translation logic never needs to know or
care which channel a report arrived on.

Design principle (per CORE, same as APRS side): "design for the
untrained sender." A message that's missing or garbles a field is NEVER
dropped - the affected report degrades to UK-unknown status and gets
published anyway, same as parser.py already does for a malformed APRS
comment.

Field values are NOT re-mapped here with a separate table. The Winlink
entry form uses the exact same wire codes as the APRS grammar (e.g.
Category="KCGR-FUEL", Status="OP", Specifier="GD") - confirmed directly
against KCGR_ResourceStatus.txt, which lists the same field set as "the
APRS grammar above" (see GitHubREADME.md). So this module imports and
reuses parser.py's STATUS_MAP / CATEGORY_MAP / SPECIFIER_LABELS as the
single source of truth - if a new category or specifier code is ever
added, it only needs to be added once, on the APRS side, and both
channels pick it up automatically.
"""

import re

from parser import STATUS_MAP, CATEGORY_MAP, SPECIFIER_LABELS

# Matches "Label: value" lines in the plain-text message body. Winlink's
# {FormFolder} substitution leaves the label text exactly as written in
# the template, so this is a straightforward split on the first colon.
_FIELD_RE = re.compile(r"^([A-Za-z][A-Za-z0-9 /()]*?):\s*(.*)$")

# Header fields we care about (others in the template - Precedence,
# MsgNr, IncidentName, ReporterPhone, ReporterEmail - aren't needed for
# a map record, so they're read but not carried into the output record).
_HEADER_LABELS = {
    "Reporter Callsign": "reporter_call",
    "Date of Observation": "report_date",
    "Time of Observation": "report_time",
    "Exercise": "is_exercise",
}

# Per-report fields, in the order they appear under each "--- REPORT N ---"
# block.
_REPORT_LABELS = {
    "Category": "category",
    "Status": "status",
    "Specifier": "specifier",
    "Location": "location",
    "Date": "date",
    "Time": "time",
    "Notes": "notes",
    "Latitude": "latitude",
    "Longitude": "longitude",
}


def _parse_fields(block_lines: list) -> dict:
    """Turns a list of 'Label: value' lines into {label: value}, skipping
    blank lines and anything that doesn't match the pattern."""
    fields = {}
    for line in block_lines:
        m = _FIELD_RE.match(line.strip())
        if m:
            fields[m.group(1).strip()] = m.group(2).strip()
    return fields


def _split_into_sections(body: str) -> dict:
    """Splits the message body on '--- SECTION NAME ---' headers into
    {section_name: [lines]}. Section names are normalized to upper case
    with surrounding whitespace stripped."""
    sections = {}
    current_name = None
    current_lines = []
    section_re = re.compile(r"^---\s*(.+?)\s*---$")

    for raw_line in body.splitlines():
        m = section_re.match(raw_line.strip())
        if m:
            if current_name is not None:
                sections[current_name] = current_lines
            current_name = m.group(1).strip().upper()
            current_lines = []
        elif current_name is not None:
            current_lines.append(raw_line)

    if current_name is not None:
        sections[current_name] = current_lines

    return sections


def _to_float(value: str):
    """Best-effort float parse. Returns None rather than raising - a
    blank or garbled coordinate shouldn't crash the whole message, it
    should just leave that one report un-mappable (still published,
    just without a lat/lon - geojson_writer's clustering already treats
    missing lat/lon as 'no cluster match', so it's handled safely
    downstream)."""
    if not value:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_report_record(reporter_call: str, received_time: str,
                          report_fields: dict, report_num: int) -> dict:
    """Builds one map-ready record from one '--- REPORT N ---' block's
    fields, in the same shape build_record() produces on the APRS side."""

    category_wire = (report_fields.get("category") or "").strip().upper()
    status_wire = (report_fields.get("status") or "").strip().upper()
    specifier_raw = (report_fields.get("specifier") or "").strip().upper() or None
    location = (report_fields.get("location") or "").strip()
    notes = (report_fields.get("notes") or "").strip()
    date_field = (report_fields.get("date") or "").strip()
    time_field = (report_fields.get("time") or "").strip()

    # Graceful degradation, same rule as the APRS side: an unrecognized
    # or missing status code is the one thing that forces UK-unknown.
    # An unrecognized category can't be forced to a fallback the same
    # way (there's no "UK category"), so it's kept as-is, tagged
    # unparsed, and left for a human to sort out via the removal tool -
    # never silently dropped.
    parsed_cleanly = True
    if status_wire not in STATUS_MAP:
        parsed_cleanly = False
        status_wire = "UK"
    if category_wire not in CATEGORY_MAP:
        parsed_cleanly = False

    category_mapped = CATEGORY_MAP.get(category_wire, "KCGR-UNKNOWN-unknown")
    status_mapped = STATUS_MAP[status_wire]

    timestamp_field = " ".join(p for p in (date_field, time_field) if p) or None

    identity = f"{reporter_call}:{category_wire or 'UNKNOWN'}:{report_num}"

    return {
        "identity": identity,
        "callsign": reporter_call,
        "category_wire": category_wire or "KCGR-UNKNOWN",
        "category_mapped": category_mapped,
        "lat": _to_float(report_fields.get("latitude")),
        "lon": _to_float(report_fields.get("longitude")),
        "received_time": received_time,
        "raw_comment": notes,
        "status_wire": status_wire,
        "status_mapped": status_mapped,
        "specifier": specifier_raw,
        "location": location,
        "timestamp_field": timestamp_field,
        "parsed_cleanly": parsed_cleanly,
        "source_channel": "winlink",
    }


def parse_winlink_message(body: str, received_time: str) -> list:
    """
    Parses one Winlink message body into a list of 0-3 map-ready
    records (one per non-blank REPORT block).

    A report block counts as "filed" if it has a non-blank Category -
    per the entry form's own design (up to 3 report blocks per message,
    not all necessarily used), a blank block just means the sender
    didn't file a second or third report and is skipped, not an error.

    NOTE: per operator decision (8/8/2026), the Exercise field is read
    but NEVER used to filter or suppress a report here. A message
    marked as an exercise still gets parsed and published exactly like
    a real one - a human clears any stray practice reports by hand
    using remove_record.py, the same "a person decides, the system
    doesn't guess" principle used everywhere else in KCGR. Do not add
    automatic Exercise filtering here without a deliberate design
    decision to change that.
    """
    sections = _split_into_sections(body)

    reporter_header = _parse_fields(sections.get("REPORTER INFO", []))
    reporter_call = (reporter_header.get("Reporter Callsign") or "UNKNOWN").strip().upper()

    records = []
    for n in (1, 2, 3):
        section_lines = sections.get(f"REPORT {n}")
        if not section_lines:
            continue
        raw_fields = _parse_fields(section_lines)
        # Re-key from the template's literal labels to short internal names.
        report_fields = {
            _REPORT_LABELS[label]: value
            for label, value in raw_fields.items()
            if label in _REPORT_LABELS
        }
        if not report_fields.get("category"):
            continue  # blank block - not a filed report, skip silently
        records.append(
            _build_report_record(reporter_call, received_time, report_fields, n)
        )

    return records

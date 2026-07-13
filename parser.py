"""
parser.py

Filters Graywolf /api/packets results for KCGR object beacons and parses
the compact comment grammar:

    ST SPEC LOCATION DDHHMM

Design principle (per CORE): "design for the untrained sender." A comment
that doesn't cleanly match the grammar is NEVER dropped - it's published
with status forced to UK-unknown and the raw text shown verbatim.
"""

import re

STATUS_MAP = {
    "OP": "OP-open",
    "CL": "CL-closed",
    "LM": "LM-limited",
    "CA": "CA-caution",
    "UK": "UK-unknown",
}

CATEGORY_MAP = {
    "KCGR-SHLT": "KCGR-SHLT-shelter",
    "KCGR-MED": "KCGR-MED-medical",
    "KCGR-ROAD": "KCGR-ROAD-road/bridge",
    "KCGR-H2O": "KCGR-H2O-water",
    "KCGR-FOOD": "KCGR-FOOD-food",
    "KCGR-FUEL": "KCGR-FUEL-fuel",
    "KCGR-PWR": "KCGR-PWR-power",
    "KCGR-CELL": "KCGR-CELL-cell",
    "KCGR-ATM": "KCGR-ATM-atm",
    "KCGR-HW": "KCGR-HW-health/welfare",
}

SPECIFIER_CODES = {
    "KCGR-SHLT": {"CA", "NP", "PP", "MO"},
    "KCGR-MED": {"ER", "UC", "PH", "OP", "CL"},
    "KCGR-ROAD": {"OP", "CL", "CA", "BR", "FL", "TR"},
    "KCGR-H2O": {"DP", "BO", "UK"},
    "KCGR-FOOD": {"HF", "GR", "BT"},
    "KCGR-FUEL": {"GS", "DS", "PP", "GD", "AL"},
    "KCGR-PWR": {"GN", "CH", "UT"},
    "KCGR-CELL": {"AT", "VZ", "TM", "AL"},
    "KCGR-ATM": {"OP", "CL", "LM"},
    "KCGR-HW": {"OP", "HR", "NM"},
}

_TIMESTAMP_RE = re.compile(r"^\d{2}(\d{2}(\d{2})?)?$")


def is_kcgr_object(packet: dict) -> bool:
    if packet.get("type") != "object":
        return False
    obj = packet.get("decoded", {}).get("Object") or {}
    name = obj.get("Name", "")
    return name.upper().startswith("KCGR-")


def parse_comment(comment: str, category_wire: str) -> dict:
    tokens = comment.strip().split()

    if not tokens:
        return _degraded(comment)

    status_wire = tokens[0].upper()
    if status_wire not in STATUS_MAP:
        return _degraded(comment)

    remaining = tokens[1:]

    timestamp_field = None
    if remaining and _TIMESTAMP_RE.match(remaining[-1]):
        timestamp_field = remaining[-1]
        remaining = remaining[:-1]

    specifier = None
    valid_specs = SPECIFIER_CODES.get(category_wire.upper(), set())
    if remaining and remaining[0].upper() in valid_specs:
        specifier = remaining[0].upper()
        remaining = remaining[1:]

    location = " ".join(remaining).strip()

    return {
        "status_wire": status_wire,
        "status_mapped": STATUS_MAP[status_wire],
        "specifier": specifier,
        "location": location,
        "timestamp_field": timestamp_field,
        "parsed_cleanly": True,
    }


def _degraded(raw_comment: str) -> dict:
    return {
        "status_wire": "UK",
        "status_mapped": STATUS_MAP["UK"],
        "specifier": None,
        "location": raw_comment.strip(),
        "timestamp_field": None,
        "parsed_cleanly": False,
    }


def build_record(packet: dict) -> dict:
    obj = packet["decoded"]["Object"]
    category_wire = obj["Name"].upper()
    callsign = packet.get("decoded", {}).get("Source", "UNKNOWN")
    comment = obj.get("Comment", "")

    parsed = parse_comment(comment, category_wire)

    return {
        "identity": f"{callsign}:{category_wire}",
        "callsign": callsign,
        "category_wire": category_wire,
        "category_mapped": CATEGORY_MAP.get(category_wire, "KCGR-UNKNOWN-unknown"),
        "lat": packet.get("lat"),
        "lon": packet.get("lon"),
        "received_time": packet.get("timestamp"),
        "raw_comment": comment,
        **parsed,
    }

"""
parser.py

Filters Graywolf /api/packets results for KCGR object beacons and parses
the compact comment grammar:

    ST SPEC LOCATION DDHHMM

Design principle (per CORE): "design for the untrained sender." A comment
that doesn't cleanly match the grammar is NEVER dropped - it's published
with status forced to UK-unknown and the raw text shown verbatim.

Field paths below are confirmed against a REAL test beacon (KCGR-FUEL,
7/12/2026) - not assumed. In particular: the comment lives at
decoded.Object.Comment, NOT decoded.Comment (which is always empty for
object packets) - this was a real bug caught by testing before building.
"""

import re

# --- Translation tables (from CORE) --------------------------------------

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

# Specifier codes per category - used for validation AND translated into
# the "CODE-label" popup format (e.g. "GD" -> "GD-gas+diesel"), matching
# how Grist's own Specifier column displays (confirmed 7/13/2026 via
# popup comparison between manual and automated entries).
SPECIFIER_CODES = {
    "KCGR-SHLT": {"CA", "NP", "PP", "MO"},
    "KCGR-MED": {"ER", "UC", "PH", "OP", "CL"},
    "KCGR-ROAD": {"OP", "CL", "CA", "BR", "FL", "TR"},
    "KCGR-H2O": {"DP", "BO", "UK"},
    "KCGR-FOOD": {"HF", "GR", "BT"},
    "KCGR-FUEL": {"GS", "DS", "PP", "GD", "AL"},  # GD added 7/12/2026
    "KCGR-PWR": {"GN", "CH", "UT"},
    "KCGR-CELL": {"AT", "VZ", "TM", "AL"},
    "KCGR-ATM": {"OP", "CL", "LM"},
    "KCGR-HW": {"OP", "HR", "NM"},
}

SPECIFIER_LABELS = {
    "KCGR-SHLT": {"CA": "CA-capacity available", "NP": "NP-no pets", "PP": "PP-pets ok", "MO": "MO-medical only"},
    "KCGR-MED": {"ER": "ER-emergency room", "UC": "UC-urgent care", "PH": "PH-pharmacy", "OP": "OP-open", "CL": "CL-closed"},
    "KCGR-ROAD": {"OP": "OP-passable", "CL": "CL-closed", "CA": "CA-caution", "BR": "BR-bridge", "FL": "FL-flooding", "TR": "TR-trees/debris"},
    "KCGR-H2O": {"DP": "DP-distribution point", "BO": "BO-boil order", "UK": "UK-unknown quality"},
    "KCGR-FOOD": {"HF": "HF-hot food", "GR": "GR-grocery", "BT": "BT-both"},
    "KCGR-FUEL": {"GS": "GS-gasoline", "DS": "DS-diesel", "PP": "PP-propane", "GD": "GD-gas+diesel", "AL": "AL-all three"},
    "KCGR-PWR": {"GN": "GN-generator", "CH": "CH-device charging", "UT": "UT-utility restored"},
    "KCGR-CELL": {"AT": "AT-AT&T", "VZ": "VZ-Verizon", "TM": "TM-T-Mobile", "AL": "AL-all carriers"},
    "KCGR-ATM": {"OP": "OP-operational", "CL": "CL-closed", "LM": "LM-cash limited"},
    "KCGR-HW": {"OP": "OP-relay available", "HR": "HR-hours follow", "NM": "NM-no message limit"},
}

# A timestamp token is 2, 4, or 6 digits: DD, DDHH, or DDHHMM.
_TIMESTAMP_RE = re.compile(r"^\d{2}(\d{2}(\d{2})?)?$")


# --- Filtering -------------------------------------------------------------

def is_kcgr_object(packet: dict) -> bool:
    """True if this packet is an APRS object beacon named KCGR-*."""
    if packet.get("type") != "object":
        return False
    obj = packet.get("decoded", {}).get("Object") or {}
    name = obj.get("Name", "")
    return name.upper().startswith("KCGR-")


# --- Parsing ----------------------------------------------------------------

def parse_comment(comment: str, category_wire: str) -> dict:
    """
    Parses a KCGR comment against `ST SPEC LOCATION DDHHMM`, degrading
    gracefully. Returns a dict with keys:
        status_wire, status_mapped, specifier, location, timestamp_field,
        parsed_cleanly (bool)
    """
    tokens = comment.strip().split()

    if not tokens:
        return _degraded(comment)

    status_wire = tokens[0].upper()
    if status_wire not in STATUS_MAP:
        # Missing/invalid status code -> per spec, this is the one case
        # that's truly invalid. Degrade fully.
        return _degraded(comment)

    remaining = tokens[1:]

    # Detect a trailing timestamp token (DD, DDHH, or DDHHMM).
    timestamp_field = None
    if remaining and _TIMESTAMP_RE.match(remaining[-1]):
        timestamp_field = remaining[-1]
        remaining = remaining[:-1]

    specifier = None
    valid_specs = SPECIFIER_CODES.get(category_wire.upper(), set())
    if remaining and remaining[0].upper() in valid_specs:
        specifier = remaining[0].upper()
        remaining = remaining[1:]
    # If the first remaining token isn't a recognized specifier for this
    # category, we don't fail the whole parse - we just don't extract a
    # specifier, and everything remaining (including that token) becomes
    # part of the free-text location. This keeps the record structured
    # (valid status, real coordinates) rather than throwing it all away
    # over one bad token - consistent with "design for the untrained sender."

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
    """The graceful-degradation fallback: never drop, always publish as UK."""
    return {
        "status_wire": "UK",
        "status_mapped": STATUS_MAP["UK"],
        "specifier": None,
        "location": raw_comment.strip(),
        "timestamp_field": None,
        "parsed_cleanly": False,
    }


# --- Full record builder ----------------------------------------------------

def build_record(packet: dict) -> dict:
    """
    Turns a raw Graywolf packet (already confirmed to be a KCGR object,
    via is_kcgr_object) into a fully structured KCGR record.
    """
    obj = packet["decoded"]["Object"]
    category_wire = obj["Name"].strip().upper()
    # NOTE: packet["source"] is the ingest CHANNEL (e.g. "modem" or
    # "igate-is"), NOT the reporting station - a real bug caught by testing
    # against live data (7/13/2026). The actual originating callsign is at
    # decoded.Source.
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


# --- Manual test, using the real KCGR-FUEL packet confirmed 7/12/2026 -------

if __name__ == "__main__":
    real_test_packet = {
        "type": "object",
        "source": "AA4TE-10",
        "timestamp": "2026-07-13T02:29:31.271879445+01:00",
        "lat": 34.1715,
        "lon": -80.7905,
        "decoded": {
            "Object": {
                "Name": "KCGR-FUEL",
                "Comment": "OP GD Elgin 2458 Main 122047",
            }
        },
    }

    assert is_kcgr_object(real_test_packet)
    record = build_record(real_test_packet)
    import json
    print(json.dumps(record, indent=2))


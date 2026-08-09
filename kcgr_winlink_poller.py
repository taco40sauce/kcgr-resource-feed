"""
kcgr_winlink_poller.py

Polls kc4rc.fd@gmail.com over IMAP for new KCGR-RS Winlink reports,
parses them (via kcgr_winlink_parser.py), and writes them to this
channel's OWN state file - never the APRS pipeline's data/records.json.

WHY A SEPARATE STATE FILE (single-writer principle):
This script is designed to run on a schedule via GitHub Actions, not on
the Pi. A GitHub Actions runner is fresh and disposable every run -
nothing persists locally the way it does on the Pi - so state has to be
committed back into the repo to survive between runs. If this script
and the Pi's APRS pipeline both tried to write the same file, two
uncoordinated, independently-scheduled processes racing to git-push the
same path is exactly the kind of rare, hard-to-reproduce conflict
that's easy to build and hard to debug. Giving each channel exactly one
owner for its own data removes that whole class of problem by
construction rather than needing to detect and resolve it after the
fact.

This script writes ONLY:
    winlink/records.json            - this channel's report records
    winlink/processed_message_ids.json  - dedup tracking

It does NOT write kcgr_resource_feed.geojson and does NOT touch the
Pi's data/records.json at all. Merging this channel's records with the
APRS pipeline's into one combined public map is a deliberately separate,
not-yet-built step (flagged in CORE as an open design question) - do
not bolt that logic onto this script without deciding that on purpose.

CREDENTIALS:
Reads the Gmail App Password from the GMAIL_APP_PASSWORD environment
variable - never hardcoded, never logged. In GitHub Actions this comes
from a repository secret; for a local test run, export it in your shell
first and don't commit it anywhere.

USAGE:
    python3 kcgr_winlink_poller.py          # normal run
    python3 kcgr_winlink_poller.py --dry-run  # parse and print only,
                                                 write nothing
"""

import email
import email.message
import imaplib
import json
import os
import sys
from datetime import datetime, timezone
from email.header import decode_header
from pathlib import Path

from kcgr_winlink_parser import parse_winlink_message

IMAP_HOST = "imap.gmail.com"
IMAP_USER = "kc4rc.fd@gmail.com"
SUBJECT_FILTER = "KCGR-RS"

REPO_DIR = Path(__file__).resolve().parent
RECORDS_PATH = REPO_DIR / "winlink" / "records.json"
PROCESSED_IDS_PATH = REPO_DIR / "winlink" / "processed_message_ids.json"

# How many days back to search each run. This is a search-scope bound
# for efficiency, NOT the actual dedup mechanism - true dedup is via
# Message-ID against processed_message_ids.json below. A generous
# window here means a missed run (GitHub Actions delay, an extended
# outage, whatever) still self-heals on the next successful run,
# without needing anyone to notice and intervene.
SEARCH_WINDOW_DAYS = 7


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[winlink_poller] WARNING: couldn't read {path} ({e}) - "
              f"treating as empty. Worth a manual look if this persists.")
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)  # atomic write


def _decode_subject(raw_subject) -> str:
    if not raw_subject:
        return ""
    parts = decode_header(raw_subject)
    decoded = ""
    for part, enc in parts:
        if isinstance(part, bytes):
            decoded += part.decode(enc or "utf-8", errors="replace")
        else:
            decoded += part
    return decoded


def _extract_plain_body(msg: email.message.Message) -> str:
    """Pulls the plain-text body out of a (possibly multipart) email.
    The Winlink form is plain-text only by design (per operator
    decision, 8/8/2026 - no HTML rendering path to account for), so
    this deliberately does not attempt to parse HTML at all."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(charset, errors="replace")
        return ""
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        return payload.decode(charset, errors="replace") if payload else ""


def fetch_new_messages(imap_password: str):
    """Connects to Gmail, searches for KCGR-RS subject messages in the
    search window, and returns a list of (message_id, subject, body,
    received_time) tuples for any not already in processed_ids."""
    processed_ids = set(_load_json(PROCESSED_IDS_PATH, []))

    conn = imaplib.IMAP4_SSL(IMAP_HOST)
    try:
        conn.login(IMAP_USER, imap_password)
        conn.select("INBOX", readonly=True)  # never mutate the mailbox itself

        since_date = (
            datetime.now(timezone.utc).date()
        )
        # IMAP SINCE wants DD-Mon-YYYY and only takes a date, not a
        # precise window, so this is an approximation - fine, since the
        # real dedup guard is processed_ids, not this search bound.
        since_str = (since_date.replace(
            day=max(1, since_date.day - SEARCH_WINDOW_DAYS)
        )).strftime("%d-%b-%Y")

        status, data = conn.search(
            None, f'(SUBJECT "{SUBJECT_FILTER}" SINCE {since_str})'
        )
        if status != "OK":
            print(f"[winlink_poller] IMAP search failed: {status}")
            return []

        uids = data[0].split()
        results = []

        for uid in uids:
            status, msg_data = conn.fetch(uid, "(RFC822)")
            if status != "OK" or not msg_data or msg_data[0] is None:
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            message_id = msg.get("Message-ID", "").strip()
            if not message_id:
                # No Message-ID at all is unusual but not impossible.
                # Fall back to a subject+date composite so this message
                # still gets a stable-enough identity to dedup against,
                # rather than being silently skipped forever.
                message_id = f"{msg.get('Subject', '')}|{msg.get('Date', '')}"

            if message_id in processed_ids:
                continue

            subject = _decode_subject(msg.get("Subject"))
            body = _extract_plain_body(msg)
            received_time = datetime.now(timezone.utc).isoformat()

            results.append((message_id, subject, body, received_time))

        return results
    finally:
        try:
            conn.logout()
        except Exception:
            pass


def run(dry_run: bool = False) -> int:
    imap_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not imap_password:
        print("[winlink_poller] GMAIL_APP_PASSWORD is not set. "
              "In GitHub Actions, add it under Settings > Secrets and "
              "variables > Actions. For a local test, export it in "
              "your shell first - never hardcode it here.")
        return 1

    try:
        new_messages = fetch_new_messages(imap_password)
    except imaplib.IMAP4.error as e:
        print(f"[winlink_poller] IMAP login/fetch failed: {e}")
        return 1

    if not new_messages:
        print("[winlink_poller] No new KCGR-RS messages.")
        return 0

    records_store = _load_json(RECORDS_PATH, {})
    processed_ids = _load_json(PROCESSED_IDS_PATH, [])

    total_reports = 0
    for message_id, subject, body, received_time in new_messages:
        reports = parse_winlink_message(body, received_time)
        for record in reports:
            records_store[record["identity"]] = record
            total_reports += 1
            flag = "" if record["parsed_cleanly"] else " (DEGRADED - needs review)"
            print(f"[winlink_poller] Stored: {record['identity']}{flag}")

        # Mark processed even if this message produced zero clean
        # reports - it was still successfully read and decoded, so
        # retrying it every run forever would just be noise. A message
        # that fails to decode at all (exception below) is NOT marked
        # processed, and will be retried next run.
        processed_ids.append(message_id)

        if not reports:
            print(f"[winlink_poller] {subject!r} - no report blocks found "
                  f"(all 3 blank, or fields didn't match expected labels)")

    if dry_run:
        print(f"[winlink_poller] DRY RUN - {total_reports} report(s) parsed, "
              f"nothing written.")
        return 0

    _write_json(RECORDS_PATH, records_store)
    _write_json(PROCESSED_IDS_PATH, processed_ids)
    print(f"[winlink_poller] Wrote {len(records_store)} total record(s), "
          f"{len(processed_ids)} message(s) marked processed.")
    return 0


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    sys.exit(run(dry_run=dry_run))

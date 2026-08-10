"""
graywolf_client.py

Thin client for Graywolf's local REST API:
  - Logs in via POST /api/auth/login (session-cookie auth)
  - Polls GET /api/packets for new APRS traffic

Credentials are loaded from ~/.kcgr_secrets/credentials.env (NOT part of
this git repo) via python-dotenv, so nothing sensitive ever touches a
tracked file.

Run this file directly for a quick manual test:
    python3 graywolf_client.py
"""

import os
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

# --- Config -----------------------------------------------------------

# Graywolf's own web UI/API, reachable locally since this runs on the Pi.
GRAYWOLF_BASE_URL = "http://127.0.0.1:8080"

# Credentials live outside the repo entirely - see CORE "Deployment setup".
SECRETS_PATH = Path.home() / ".kcgr_secrets" / "credentials.env"


# --- Client -------------------------------------------------------------

class GraywolfClient:
    """Handles auth + packet polling against a local Graywolf instance."""

    def __init__(self, base_url: str = GRAYWOLF_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self._logged_in = False

    def login(self) -> None:
        """
        Authenticates against Graywolf, storing the graywolf_session
        cookie on self.session for subsequent requests.

        NOTE: field names below (username/password) are a best-effort
        guess based on common conventions - if Graywolf's actual login
        endpoint expects different field names, check the Swagger/OpenAPI
        page served from http://10.0.0.58:8080/ (per CORE: must be viewed
        from the Pi's own address, not the chrissnell.com handbook copy)
        and adjust the `payload` dict below accordingly.
        """
        load_dotenv(SECRETS_PATH)
        username = os.environ.get("GRAYWOLF_USER")
        password = os.environ.get("GRAYWOLF_PASS")

        if not username or not password:
            raise RuntimeError(
                f"GRAYWOLF_USER / GRAYWOLF_PASS not found - check {SECRETS_PATH}"
            )

        payload = {"username": username, "password": password}
        resp = self.session.post(f"{self.base_url}/api/auth/login", json=payload)
        resp.raise_for_status()

        if "graywolf_session" not in self.session.cookies.get_dict():
            raise RuntimeError(
                "Login request succeeded (HTTP OK) but no graywolf_session "
                "cookie was set - check the login payload field names against "
                "the Pi-hosted Swagger UI."
            )

        self._logged_in = True
        print(f"[graywolf_client] Logged in OK as {username}")

    def get_packets(
        self,
        since: str | None = None,
        direction: str = "RX",
        packet_type: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """
        Fetches packets from GET /api/packets.

        Args:
            since: ISO-8601 timestamp string - only packets after this time.
            direction: "RX" (received) or "TX" (transmitted). Defaults to RX,
                since the KCGR pipeline only cares about incoming reports.
            packet_type: optional filter, e.g. "object" for object beacons.
            limit: optional max number of results.

        Returns:
            List of packet dicts as returned by the API.
        """
        if not self._logged_in:
            self.login()

        params = {"direction": direction}
        if since:
            params["since"] = since
        if packet_type:
            params["type"] = packet_type
        if limit:
            params["limit"] = limit

        resp = self.session.get(f"{self.base_url}/api/packets", params=params)

        # If the session expired, try one re-login + retry before giving up.
        if resp.status_code == 401:
            print("[graywolf_client] Session expired, re-logging in...")
            self._logged_in = False
            self.login()
            resp = self.session.get(f"{self.base_url}/api/packets", params=params)

        resp.raise_for_status()
        return resp.json()


# --- Manual test entry point --------------------------------------------

if __name__ == "__main__":
    client = GraywolfClient()
    client.login()

    # Quick smoke test: pull the last few RX packets and print a summary.
    packets = client.get_packets(limit=10)
    print(f"\nFetched {len(packets)} packet(s):\n")
    for p in packets:
        ts = p.get("timestamp", "?")
        src = p.get("source", "?")
        ptype = p.get("type", "?")
        display = p.get("display", "")
        print(f"  [{ts}] {src} ({ptype}): {display}")

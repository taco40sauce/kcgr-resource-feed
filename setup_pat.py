#!/usr/bin/env python3
"""
setup_pat.py — KCGR GitHub Personal Access Token (P.A.T.) setup & validator

Run this once when setting up a new GitHub P.A.T. for the admin
removal panel (see Part VI, 6.8 of the manual for how to generate the
token itself on GitHub's site first).

Not to be confused with *Pat*, the separate Winlink client program —
this checks a GitHub credential, unrelated to Winlink entirely.

What this script does:
  1. Prompts you to paste a fine-grained GitHub P.A.T. (hidden as you
     type, like a password).
  2. Confirms the token actually works by making real, harmless calls
     against the real repo and the real workflows the removal panel
     depends on — not just trusting what GitHub's setup screen claims
     the token can do.
  3. Prints the exact line to paste into the Pi's credentials file
     yourself — this script never connects to the Pi at all. Run it
     on whatever computer already has your saved token.

Requires only Python's standard library — nothing to pip install,
and nothing to install on the Pi.
"""

import getpass
import json
import os
import sys
import urllib.request
import urllib.error

# ---- Configuration ---------------------------------------------------
# If you're running this for your own forked repo (see Part VI),
# change these two lines to match your own fork.
REPO_OWNER = "taco40sauce"
REPO_NAME = "kcgr-resource-feed"

# The real workflows the admin removal panel dispatches via this
# token: one of the two removal workflows, then the shared publisher.
# A token that can't reach these can't do its actual job, even if it
# looks correctly scoped on GitHub's own setup screen.
REMOVAL_WORKFLOWS = ["aprsis-removal.yml", "winlink-removal.yml"]
PUBLISH_WORKFLOW = "merge-and-publish.yml"

# A file that should already exist in the repo, used to test real
# Contents:Read-only access (not just repo visibility, which only
# needs the always-included Metadata permission).
CONTENTS_TEST_PATH = "README.md"

CREDENTIALS_PATH = os.path.expanduser("~/.kcgr_secrets/credentials.env")


def api_get(url, token):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "kcgr-pat-setup-script",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode())
        except Exception:
            body = {}
        return e.code, body
    except urllib.error.URLError as e:
        return None, {"message": str(e.reason)}


def api_post(url, token, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "kcgr-pat-setup-script",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, {}
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode())
        except Exception:
            body = {}
        return e.code, body
    except urllib.error.URLError as e:
        return None, {"message": str(e.reason)}


def check_contents_access(token):
    status, body = api_get(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
        f"/contents/{CONTENTS_TEST_PATH}",
        token,
    )
    if status == 200:
        print(f"  \u2713 Can read {CONTENTS_TEST_PATH} (Contents: Read-only confirmed)")
        return True
    if status == 401:
        print("  \u2717 GitHub says this token isn't valid at all.")
        print("    Double-check you copied the whole thing, with no")
        print("    extra spaces or missing characters.")
        return False
    if status == 404:
        print(f"  \u2717 Can't read {CONTENTS_TEST_PATH} in {REPO_OWNER}/{REPO_NAME}.")
        print("    Check 'Repository access' is set to this repo, and")
        print("    that 'Contents' has at least Read-only access.")
        return False
    print(f"  \u2717 Unexpected response checking file access (HTTP {status}).")
    print(f"    {body.get('message', '')}")
    return False


def check_workflow_visibility(token, workflow):
    status, body = api_get(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
        f"/actions/workflows/{workflow}",
        token,
    )
    if status == 200:
        print(f"  \u2713 Can see workflow '{workflow}'")
        return True
    if status == 404:
        print(f"  \u2717 Can't find or see workflow '{workflow}'.")
        print("    Check that 'Actions' has at least Read access.")
        return False
    print(f"  \u2717 Unexpected response for '{workflow}' (HTTP {status}).")
    return False


def check_dispatch_write_access(token):
    """
    Actually attempts a real workflow_dispatch of the publish step.
    This is the only way to prove Actions: Read AND WRITE genuinely
    works, rather than just Read — but it's a real, live action (an
    extra, harmless, idempotent run of the map publisher), so it's
    opt-in, not automatic.
    """
    status, body = api_post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
        f"/actions/workflows/{PUBLISH_WORKFLOW}/dispatches",
        token,
        {"ref": "main"},
    )
    if status == 204:
        print(f"  \u2713 Successfully dispatched '{PUBLISH_WORKFLOW}' "
              f"(Actions: Read and write confirmed)")
        print(f"    A real run just started — check the Actions tab on GitHub")
        print(f"    if you want to watch it, though this is expected and safe.")
        return True
    if status == 403:
        print(f"  \u2717 GitHub rejected the dispatch (HTTP 403).")
        print("    'Actions' is probably set to Read-only rather than")
        print("    Read and write. Fix this on GitHub's token settings.")
        return False
    print(f"  \u2717 Unexpected response dispatching the workflow (HTTP {status}).")
    print(f"    {body.get('message', '')}")
    return False


def print_paste_instructions(token):
    print("\n" + "=" * 62)
    print("  Token validated. Nothing was changed on any remote machine —")
    print("  this script never touches the Pi.")
    print("=" * 62)
    print(f"\nOn the Pi, open (or create) this file:")
    print(f"  {CREDENTIALS_PATH}")
    print("\nAdd or replace the GITHUB_PAT line with exactly this:")
    print(f"\n  GITHUB_PAT={token}\n")
    print("If a GITHUB_PAT= line already exists in that file, replace")
    print("it -- don't add a second one. Leave every other line in the")
    print("file untouched.")
    print("\nThen restart the admin app for it to take effect:")
    print("  sudo systemctl restart kcgr-admin")


def main():
    print("=" * 62)
    print("  KCGR GitHub Personal Access Token (P.A.T.) setup")
    print("=" * 62)
    print(f"\nTarget repository: {REPO_OWNER}/{REPO_NAME}")
    print("This script runs entirely on THIS computer and only talks to")
    print("GitHub over the internet -- it never connects to the Pi.")
    print("\nPaste your fine-grained P.A.T. below. It will NOT be shown")
    print("on screen as you type or paste it -- that's normal.")

    token = getpass.getpass("\nP.A.T.: ").strip()

    if not token:
        print("\nNo token entered — nothing was changed. Run this again")
        print("when you have a token ready.")
        sys.exit(1)

    print("\nChecking the token against the real repository...\n")

    ok = check_contents_access(token)
    for wf in REMOVAL_WORKFLOWS:
        ok = check_workflow_visibility(token, wf) and ok
    ok = check_workflow_visibility(token, PUBLISH_WORKFLOW) and ok

    if not ok:
        print("\n" + "=" * 62)
        print("  Token did NOT pass validation — nothing was saved.")
        print("=" * 62)
        print("\nFix the issue(s) above on GitHub's side (Settings >")
        print("Developer settings > Fine-grained tokens), then run this")
        print("script again.")
        sys.exit(1)

    print("\n" + "=" * 62)
    print("  Basic checks passed.")
    print("=" * 62)

    dispatch_choice = input(
        "\nAlso do a live write-access test? This triggers one real,\n"
        f"harmless run of '{PUBLISH_WORKFLOW}' to confirm Actions:\n"
        "Read and write genuinely works, not just Read. [y/N] "
    ).strip().lower()

    if dispatch_choice == "y":
        if not check_dispatch_write_access(token):
            print("\n" + "=" * 62)
            print("  Write-access test failed — nothing was saved.")
            print("=" * 62)
            sys.exit(1)
    else:
        print("\n  (Skipped — Actions read access was confirmed above, but")
        print("   write access wasn't directly tested.)")

    print_paste_instructions(token)


if __name__ == "__main__":
    main()

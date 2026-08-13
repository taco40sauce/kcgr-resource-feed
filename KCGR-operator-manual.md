# KCGR Pipeline — Operator Manual (Web Toggle & Remote Access)

**Who this is for:** any trained KCGR operator who needs to turn the
automated reporting pipeline on/off, check its status, or request a
stale report be removed — from home, from an EOC, or anywhere else —
without needing to SSH into the Pi or understand the code behind it.

---

## 1. One-Time Setup (do this once, on each device you'll use)

Before you can reach the admin page remotely, your device needs to join
the same private network (Tailscale) as the Pi.

1. Go to **tailscale.com** and sign in when prompted, using the invite
   sent to you by the Hub Operator (AA4TE).
2. Install Tailscale for your device type (Windows, macOS, iPhone/iPad,
   Android, or Linux) — follow the on-screen instructions for your
   platform.
3. Once installed, log in with the account you were invited under.
4. That's it — no further configuration needed. Your device is now on
   the same private network as the Pi, and can reach the admin page from
   anywhere with an internet connection (home WiFi, cellular data, another
   network — doesn't matter).

**You only need to do this once per device**, not every time you want to
use the admin page.

---

## 2. Turning the Pipeline On or Off

1. Open a browser on any device that's joined the tailnet (see Section 1).
2. Go to:
   ```
   http://100.68.180.65:5050
   ```
3. Enter the admin password when prompted. (Get this from the Hub
   Operator if you don't have it — it's not your Tailscale login and not
   your Pi login, it's a separate password just for this page.)
4. You'll see the current status:
   - **Green "Turn ON" button** = pipeline is currently off
   - **Red "Turn OFF" button** = pipeline is currently on
5. Click the button to change it. The page will reload showing the new
   status within a couple seconds.

**When to turn it ON:** at the start of an active incident/exercise, so
incoming KCGR reports automatically reach the public map every 15 minutes
without anyone needing to run anything by hand.

**When to turn it OFF:** once the incident/exercise is over, so it's not
polling unnecessarily in the background.

---

## 3. Checking Whether It's Actually Working

After turning it on, reports can take up to **15 minutes** to appear on
the public map — that's normal, not a malfunction. The pipeline only
checks for new reports every 15 minutes while it's on.

If you want to confirm it's genuinely running (not just that the page
says so):
- Refresh the admin page — the status should stay accurate.
- Check the public map itself after waiting at least 15 minutes.
- If something seems off after a reasonable wait, contact the Hub
  Operator rather than trying to fix it yourself — the underlying system
  (the Pi, the scripts) isn't meant to be touched from this page.

---

## 4. If a Report Needs to Be Removed

**Important: deleting a marker directly on the uMap map itself does NOT
work permanently** — it will reappear, because the map is just a display
of data that lives elsewhere. Don't use the map's own delete/trash tools
for this.

Removal currently requires the Hub Operator to run a command directly on
the Pi. If you spot a report that needs to come down (stale, incorrect,
duplicate), **contact the Hub Operator with the details** rather than
attempting to remove it yourself:
- Which report (category + rough location is enough)
- Why it needs to come down

---

## 5. What NOT to Do

- **Don't share the admin password outside trained/approved operators.**
  It controls a real, live public safety data feed.
- **Don't try to access this page without Tailscale set up first** —
  the address won't load from a device that hasn't joined the tailnet.
- **Don't leave the pipeline on indefinitely "just in case"** — turn it
  off when there's no active need, to keep things simple and predictable.
- **If anything looks broken or behaves unexpectedly, stop and contact
  the Hub Operator** rather than trying to troubleshoot the underlying
  system — this page is intentionally limited to on/off and status only.

---

## 6. Inbox Visibility (`kc4rc.fd@gmail.com`)

This account is both a human inbox and the live intake point the
automated Winlink poller reads every 15 minutes — visibility into it
matters operationally, not just administratively.

**Currently forwarding everything (all incoming mail):**
- Two existing addresses
- A third address added 8/10/2026

**Currently forwarding only KCGR reports** (subject contains `KCGR-RS`, or
addressed to `KCGR-OPS`):
- A fourth address, added 8/10/2026, scoped to just Winlink resource-status
  traffic rather than the full inbox

**Why this is safe alongside the automated poller:** every forwarding
rule above only sends a copy of a matching message. None of them archive,
label, or mark messages read, so nothing interferes with the poller's own
Message-ID-based processing.

**Monitoring responsibility:** the Hub Operator checks this inbox at
least once daily during normal operations. During an active KCGR
activation, the operator currently on shift checks it as part of their
regular duties, same as any other intake channel. If the Hub Operator is
unreachable for an extended period, monitoring responsibility passes to
whoever currently holds activation authority (Part IV, Activation
Authority).

**If you need to add or change a forwarding address:** this isn't a
self-serve operator-manual task — it involves Gmail account settings, not
the admin toggle page this manual otherwise covers. Contact the Hub
Operator.

---

## 7. Who to Contact

**Hub Operator:** Dave, AA4TE
**For:** password resets, report removal, technical issues, or anything
this manual doesn't cover.

---

*KCGR / Graywolf Automated Pipeline — Kershaw County Amateur Radio Club (KC4RC)*

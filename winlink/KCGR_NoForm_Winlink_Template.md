# KCGR-RS Winlink Report — No-Form Copy/Paste Template

For anyone sending a KCGR report over Winlink **without** the
`KCGR_ResourceStatus` form installed. Copy the block below into a new
plain-text Winlink message, fill in the blanks, and send — no form
software required.

**This works because of how the automated parser actually reads a
message**: it matches on the exact section headers (the `--- ... ---`
lines) and the exact field labels (the word before each colon), not on
which software sent it. Get those two things right and it parses
exactly the same as a message sent from the real form.

---

## 1. Address and Subject

- **To:** `KCGR-OPS`
- **Subject:** `KCGR-RS - <your callsign> - <today's date>`
  (e.g. `KCGR-RS - AA4TE - 2026-08-18`) — the subject must contain
  `KCGR-RS` or it won't be picked up.

## 2. Message body — copy everything below this line

```
KERSHAW COUNTY GROUND REPORT -- RESOURCE STATUS (KCGR-RS)
==========================================================

--- REPORTER INFO ---
Reporter Callsign: YOUR_CALLSIGN
Date of Observation: YYYY-MM-DD
Time of Observation: HHMM

--- REPORT 1 ---
Category: KCGR-____
Status: __
Specifier: __
Location: 
Date: 
Time: 
Notes: 
Latitude: 34.*****
Longitude: -80.*****
```

---

## 3. Worked example

Here's the same block filled in for the shorthand you asked about
earlier — `KCGR-FUEL OP PP Elgin BP Hwy1 181033` — translated into
this labeled format:

```
KERSHAW COUNTY GROUND REPORT -- RESOURCE STATUS (KCGR-RS)
==========================================================

--- REPORTER INFO ---
Reporter Callsign: AA4TE
Date of Observation: 2026-08-18
Time of Observation: 1033

--- REPORT 1 ---
Category: KCGR-FUEL
Status: OP
Specifier: PP
Location: Elgin BP Hwy1
Date: 18
Time: 1033
Notes: 
Latitude: 34.*****
Longitude: -80.*****
```

---

## 4. What's required vs. optional

- **`Reporter Callsign`** — leave it blank and the record gets logged
  as `UNKNOWN` instead of your callsign. Always fill this in.
- **`Category`** — required. If it's blank, that whole report block is
  silently skipped (treated as "not filed," not an error). If it's
  filled in but doesn't match a real KCGR category code, the report
  still gets published, just flagged for a human to clean up.
- **`Status`** — if blank or not a recognized code, it's automatically
  published as `UK - unknown` rather than rejected. Better to fill it
  in correctly, but a mistake here won't lose the report.
- **`Specifier`, `Location`, `Date`, `Time`, `Notes`,
  `Latitude`/`Longitude`** — all optional. Blank is fine; the report
  still gets published.
- For your actual category, status, and specifier codes, use your
  Quick Start / Quick Reference card — this template doesn't repeat
  that list on purpose, so it never goes stale relative to it.

## 5. Filing more than one report in the same message

Copy a second `--- REPORT 2 ---` block (same field labels) below the
first one if you're reporting more than one thing at once — up to
`REPORT 3`. Leave any block out entirely if you only have one report;
you don't need empty placeholders for the ones you're not using.

## 6. What NOT to change

The section headers (`--- REPORTER INFO ---`, `--- REPORT 1 ---`) and
the field labels (`Category:`, `Status:`, etc.) must be typed exactly
as shown — that's literally the text the automated system searches
for. Everything **after** the colon on each line is yours to fill in
freely.

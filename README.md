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
merged into one shared public map, plus a fourth fully independent
reporting path:

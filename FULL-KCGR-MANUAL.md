# [County/Town] Emergency Ground-Report Pipeline — Full Setup & Operations Manual

**Adapted from the KCGR (Kershaw County Ground Report) system, built by
the Kershaw County Amateur Radio Club (KC4RC), South Carolina.** Every 🔧
marks something specific to Kershaw County that you'll want to think
through for your own area, not just copy as-is. A one-page worksheet for
recording your own answers will be added once the rest of this manual is
in place.

**For crisis-speed reference**, see quick_start.md / quick_start.pdf"

**Please read this whole manual once, calmly, before you ever need it.**
Everything here is written so you *can* look something up mid-emergency —
but you'll move faster and with more confidence if the ideas are already
familiar before that day comes. A short Quick Start guide will sit at the
very front of the finished manual for exactly the moment when you don't
have time to read anything else — this fuller version is what backs it up.

*Each section below has two parts: short instructions you can act on
right away, and numbered notes at the end explaining the "why" behind
them. You don't need the notes to get moving. They're there for whenever
you have a moment, or want to understand something well enough to
change it for your own location and situation.*

---

# PART I — Before You Start

### A Word for the Skeptics in the Room

If you're reading this because your club already takes emergency
preparedness seriously, feel free to skip ahead to Section 1.1 — this
short passage isn't really for you. It's for the club member, spouse, or
town official looking over your shoulder right now, thinking "we've
never needed anything like this before."

Here's something worth considering: most clubs that take
preparedness seriously didn't start out that way. Often, it took getting
caught off guard once, and deciding out loud that they never wanted that
feeling again. One of our own members, while on vacation, sat in on another town's ham  club meeting.
What he noticed was a whole club, engaged in planning, drills,
and supplies — a real, visible change, according to those members, from what that same club used to be. They explained why: they'd been caught unprepared once, and had decided never to let that happen again.

You don't have to wait for your own hard lesson to take this seriously.
That's the purpose of this whole manual — letting you
borrow someone else's hard-earned experience, instead of needing to earn
your own the same way.

---

## 1.1 The Thinking Behind This System

A handful of ideas shaped every decision in this system. Read through
these once before building anything — they'll save you from running into
the same problems we already worked through.

- **Build this for someone who's never been trained, not just for
  yourself.**[¹]
- **Expect to change things later — that's not a failure, that's planning.**[²]
- **When two people report the same thing, that's a good sign, not a
  duplicate to clean up.**[³]
- **An old report doesn't get deleted. It gets labeled as
  unconfirmed and rechecked.**[⁴]
- **A valid ham radio license is enough to trust someone's report
  automatically.**[⁵]
- **Give every password and every key only the smallest amount of access
  it actually needs.**[⁶]
- **Set this up so it still works even if you're not the one running it
  anymore.**[⁷]
- **A person checks and clears old reports by hand. The system doesn't
  try to guess when something's over.**[⁸]
- **Build a real, two-way relationship with your local Emergency
  Operations Center — don't just send information one direction.**[⁹]

---

## 1.2 Prerequisites Checklist

Before starting any technical setup, confirm you have:

**KCGR project** (Kershaw County Ground Report — ham radio emergency resource map).You can find the open source github repository at github.com/taco40sauce/kcgr-resource-feed.

- [ ] At least one licensed amateur radio operator willing to serve as
      **Hub Operator** — the person whose credentials, accounts, and
      judgment the system runs on day one 🔧
- [ ] A relationship (even informal) with your local ARES/RACES group or
      equivalent 🔧
- [ ] Awareness at your county/parish EOC or Director of Emergency
      Services level that this exists, even if informal at first 🔧

**Hardware**
- [ ] A small always-on computer to run the pipeline (a Raspberry Pi Zero
      2 W or similar is sufficient for this workload)
- [ ] An amateur radio capable of APRS operation, with a clear connection
      method identified for your specific radio model 🔧[¹⁰]
- [ ] Stable home/office internet connection for the host computer

**Accounts (create these before writing any code)**
- [ ] A **dedicated organizational email account** (not a personal one)
      to own shared services going forward[⁷] — e.g. `yourclub.emcomm@gmail.com` 🔧
- [ ] A GitHub account under that organizational identity, or a clear
      plan to transfer to one later
- [ ] A free-tier database account (Grist or equivalent) for manual entry
- [ ] A free-tier mapping account (uMap or equivalent) for public display
- [ ] A **Tailscale** (or equivalent mesh VPN) account under the
      organizational email, for remote operator access

**Decisions to make before building (don't skip — see Part III for how)**
- [ ] Your category list — what hazards matter in your area 🔧
- [ ] Your field-format grammar and prefix (e.g. `KCGR-` → your own) 🔧 
- [ ] Your vetting policy — who is auto-trusted, who needs corroboration 🔧

---

## Notes for Part I

**[¹] Build this for someone who's never been trained.**
On day one, you probably won't have any trained operators yet — just
people you tell, "send me what you're seeing." The system has to work for
that person, not just for someone who's studied the format carefully.
Every rule about how a report gets read should be checked against: "what
happens if someone who's never seen this format sends something close,
but not exact?" The answer should never be "it gets set aside for later or silently ignored."

One concrete example: the system doesn't care whether someone types their
report in capital letters or lowercase — either works. That said, we'd
still recommend typing reports in ALL CAPS as a habit. It's not required
by the system, but it's a long-standing convention in ham radio traffic
handling (formal message relay) for a good reason: it's easier to read at
a glance, especially when someone's copying it down by hand or squinting
at a screen under stress. No downside, real upside — worth teaching as a
habit even though the software doesn't demand it.

**[²] Expect to change things later — that's the plan, not a failure.**
This whole system started as a rough sketch, and real use has already
changed pieces of it more than once — that's normal, and it's actually a
sign the design is working, not a sign something's wrong. Build the
skeleton plan first, get it running, and expect the details (categories,
timing, wording) to shift once real people start using it. We found that
a system running today, getting adjusted as we went, served us better
than waiting for a perfect plan before starting — your own experience
might look a little different, and that's fine. The point isn't "do it
exactly this way," it's "don't let waiting for perfect stop you from
starting."

This same "don't wait for perfect" idea also applies to individual
reports, not just the system as a whole. During Hurricane Helene, real
information from the ground existed, but it mostly reached emergency
agencies and never reached the public — the problem wasn't a lack of
data, it was good information sitting unused. So this system is built to
show a report even when it doesn't perfectly match the expected format —
labeled as "unconfirmed" or "unclear," rather than thrown away.
A grey, imperfect pin on a map still tells someone "something's happening
here" — which is more than they had before, and doesn't waste the effort
someone put into sending it.

**[³] Two matching reports are worth more than one.**
Picture this: two different operators, who don't know each other, both
report the same bridge as washed out. Is that a duplicate to clean up, or
is it actually the most reassuring thing that could happen — real
confirmation from two independent sources? We treat it as real confirmation.
Every report still gets saved on its own, under the name or email of the person who
sent it — nothing gets merged or overwritten — but the map data entry shows a count,
like "confirmed by 3 operators," so anyone looking at it can judge for
themselves how solid a report is, rather than the system automatically deciding
that for them.

(If you're curious where this idea comes from: established disaster-
mapping projects, most notably one called Ushahidi — used after events
like the 2010 Haiti earthquake — arrived at this same approach well
before we did. We didn't set out to copy it; we found it after the fact
and were glad to see our own reasoning matched real, tested practice.)

**[⁴] An old report doesn't get deleted — it just gets labeled.**
Here's the actual idea: just because nobody's re-confirmed a report
doesn't mean it's wrong. Say someone reports a road closed on Monday, and
by Thursday nobody's heard anything more about it — that doesn't mean the
road reopened, it might just mean the operator who reported it lost power
or moved on to something else. So instead of deleting that report, or
pretending it's still fresh, the map marks it "unconfirmed" after
a certain amount of time. The original information stays visible the
whole time — it's just being labeled as older. How long that takes
before something gets marked unconfirmed is different for every type of
report, and should be based on how fast things actually tend to change in
your area (see Part III for how to work that out for yourself).

**[⁵] Why a license alone is enough to trust a report.**
Any licensed ham radio operator's report gets posted automatically,
without needing a second person to confirm it first — and that's a
deliberate choice, not something we skipped by accident. A ham radio
license means the government has already verified who that person really
is and that they can be held accountable for what they transmit — the
same reason the U.S. Geological Survey trusts amateur radio operators 
using Winlink' "Did You Feel it" reports without needing anyone to 
double-check them first.A callsign works the same way here: it's already 
a form of trusted ID. [see https://winlink.org/tags/dyfi]

This doesn't extend automatically to *every* possible source of
information, though, since it could mean two different things:

- If a report comes in through a completely different system — say, a
  future version of this pipeline that also accepts reports over a
  citizens-band mesh network, or a web form open to the general public —
  that source doesn't carry the same built-in ID-checking a ham license
  does. That doesn't mean it gets held back and hidden, though — same as
  everywhere else in this system, it still goes on the map right away,
  just labeled "unconfirmed," until either a second, independent
  report backs it up, or a licensed operator is able to check it out and
  vouch for it personally. This is not intended to imply belief in the report.

- On the other hand, if a *licensed ham* hears something secondhand —
  from a scanner, a neighbor, social media — and chooses to relay it as
  their own report, that's still coming in through the ham radio system,
  under their own callsign, and their license still vouches for them
  personally. It's on that operator to only relay what they're confident
  enough to put their own callsign behind — same as any other report they
  send.

In short: it's the *path the report came in on* that determines the
trust level, not the *original source* of what an operator personally
chose to pass along. Unconfirmed reports can easily become confirmed
with the report of a second witness.

**[⁶] Only ever give a password or a key the smallest job it needs.**
Think of it like giving out house keys: you wouldn't hand someone a
master key just so they can water your plants — you'd give them a key
that only opens the side door. This system follows that same idea
everywhere. Logins are used to update the public map and each only allows
that one thing, but doesn't access everything else in the account it lives
in. Someone checking the shared database can be given a "look but don't
touch" version of access unless they specifically need to make changes.

This isn't about being suspicious of anyone — it's just good sense. If
any one password or key is ever lost, guessed, or misused, the damage
stays small and contained, instead of spreading to everything else.

**[⁷] Set this up so it doesn't depend on just you.**
Someday, you might be busy, unreachable, or simply ready to hand this off
to someone else — and this system should keep working when that happens,
not fall apart because one person's personal logins were holding
everything together. That's the whole reason for using a shared club
email account (not your own personal one) for things like the map service
and the shared file storage — so a future leader can be handed the keys
cleanly, without needing your personal accounts at all. Write things down
assuming the person reading them later might be far less technical than
you are right now, not as technical as you'll be after building all of
this yourself.

One real wrinkle worth flagging, not glossing over: a shared
club account is great for succession, but it does raise a practical
question once Winlink becomes part of this system — someone still has to
actually log in and check that shared account regularly, the same way you
might check your own personal one out of habit. That's not automatic just
because it's a shared account. Checking a Winlink account usually means
connecting to it directly (for example, over telnet), not glancing at a
regular inbox — so this needs its own clear answer: who checks it, and
how often, especially during an actual event. We don't have a perfect 
answer to that ourselves. At present, we're using a google account 
owned by the club in which we can set up "email rules" that allow 
forwarding of messages with the "KCGR-RS" subject line.— it's 
flagged here on purpose as something to work out together with your 
team when you get to that part of the system, not something fully solved.

**[⁸] A person clears old reports by hand — the system doesn't guess.**
There's no fully reliable way for the system to know on its own when a
situation is truly over — a shelter closing, a road reopening — versus
just quiet for a while. Rather than let a computer guess wrong and remove
a report that's still true, a real person checks and clears things out
after an event has settled down. Getting this wrong in the safer
direction (a report such as "road-closed" stays visible a little longer 
than it needs to) is far better than getting it wrong in the other direction 
(a still-true report disappears on its own). The corroboration count mentioned earlier
is a helpful clue for *where* to look when doing this cleanup — a report
that many people confirmed, but that's gone silent for a while, is worth a
second look — but a person always makes the actual call. Confirming by 
various avenues is the way to go.

**[⁹] Build a real relationship with your local EOC — not just a feed
going out.**
It's worth thinking about your local Emergency Operations Center as a
partner, not just an audience for your public map. One concrete way to do
this: encourage your operators to also send significant reports directly
to your local (or state) emergency management using the standard format
they already use for this — called an **ICS-213 General Message form**.
It's a simple, widely-recognized way of relaying a message during an
emergency, already familiar to most EOC and ARES/RACES people, so using
it tends to be taken seriously right away.

Covering both bases can create a genuine two-way street: official
information the EOC has — that may never would have been relayed from a ham
operator on the ground — can end up getting added to your public map by
your Hub Operator or those associated with the EOC leadership, filling 
in gaps your own reports alone couldn't cover.

There's a real trade-off worth naming: ask every field operator to fill 
out a second, more formal message on top of their
quick radio report adds real effort, right when they're busiest. Two
reasonable ways to handle this, and it's worth picking one on purpose
rather than leaving it vague:
- Ask operators to send both, for reports they judge important enough —
  simple but adds workload to the person out in the field.
- Have your Hub Operator (or someone else in that role) periodically
  gather up the notable reports already coming in and relay *those* to
  the EOC as ICS-213 messages — keeps the field side simple and fast, at
  the cost of a little delay and one more task for whoever runs the hub.
- The bottom line is ask for reports to the Hb, then file a similar report
 to the EOC and/or ARES.

Either can work. What matters most is deciding this on purpose, together
with your team, rather than leaving it to chance — see Part IV, section
4.4, for how this plays out during an actual activation.

**[¹⁰] Does your radio already have a sound card built in? Start here.**
The single most useful question to answer first is: **does your radio
already have its own built-in sound card?** This matters because of
what a radio interface actually has to do — carry audio (what the radio
hears and transmits) and carry control commands (telling the radio when
to transmit, called PTT, and sometimes other settings) between the
radio and your computer.

Some newer radios — this system runs on an **Icom IC-7100**, which is
one example — have that sound card built directly into the radio
itself. That means both audio and control travel over a single plain
USB cable straight from the radio to your computer, with nothing extra
to buy, configure, or wire up. If your radio has this, you're done —
skip the rest of this note.

Older or simpler radios usually don't have a built-in sound card, and
need a small separate box in between the radio and the computer to do
that same job — handling audio and switching the radio to transmit — a
**Signalink** is a well-known example of this kind of box. It does the
same job as a built-in sound card, just with an extra piece of hardware
and a bit more cabling. Another option is **digirig** ham radio cabling
[https://digirig.net/] — mentioned as a possible solution, not an
endorsement.

Neither setup is "better" than the other for this system — you're not
missing out either way. You just need to know which one you have, since
the setup steps in Part II (2.1) differ slightly depending on the
answer. If you're not sure, check your radio's manual for the words
"USB audio" or "built-in sound card" — that'll tell you which category
you're in. The advantage of a small Raspberry Pi is that very little
energy is used, which could affect your power bill less than the
alternatives.

---

*Part II (Building It) picks up next — hardware interfacing, software
pipeline setup, database/map setup, and remote access.*

---

# PART II — Building It

A quick heads-up before you start: this part has real technical steps in
it — typing commands, creating accounts, connecting things together.
None of it requires being a programmer. Where a term might be unfamiliar,
we'll try to explain it plainly the first time it comes up — if something
still doesn't make sense, that's worth a note for whoever maintains this
manual next, not a sign you're missing something obvious. Take it one
section at a time, and test each piece before moving to the next — this
system was actually built and debugged that way in real life, one piece
at a time, not all at once.

---

## 2.1 Hardware & Radio Interfacing

**What you need:**
- [ ] A small always-on computer. Two paths work equally well — pick
      based on what you already have on hand:
      - A **Raspberry Pi** — the reference build this system's setup
        steps assume; a credit-card-sized computer that sips very
        little power and is relatively inexpensive.
      - An **older computer running a Linux distro** — this project's
        actual original build was a repurposing project like this,
        which then grew into what's documented here. Still a
        completely valid starting point.
- [ ] Your amateur radio, connected using whichever method matches your
      radio (see Part I, note 10 — either a single USB cable, or a
      separate interface box like a Signalink) 🔧
- [ ] APRS software installed on the small computer — this system was
      built and tested using software called **Graywolf**; if you use
      different APRS software, the steps below will need to be adapted 🔧

**Steps:**
1. Connect your radio to the small computer using the method you
   identified in Part I.
2. Install your chosen APRS software and confirm your radio's control
   settings match your radio's actual settings (the exact port name, the
   control address, and the connection speed are specific to your radio
   model — check your radio's manual) 🔧
3. Set your station's callsign, beacon message, and how often it
   transmits, inside the APRS software's settings.
4. **Test before moving on:** trigger a manual beacon from the software,
   and confirm it shows up on a public site like **aprs.fi** within a
   few minutes. We'd recommend confirming this works before moving to
   Section 2.2 — every later piece assumes this first step is solid, so a
   problem here tends to show up as something confusing further down the
   line, rather than as an obvious error right where it started.

---

## 2.2 Software Pipeline Setup


**What "the pipeline" actually is, in plain terms:** not one path, but
several independent capture channels that each notice a new report
arriving over their own source, read what it says, and save it —
feeding into one shared step that takes everything saved across every
channel and republishes your public map together.

**Why more than one channel, on purpose.** Relying on a single capture
path ties your entire system's uptime to one radio, one piece of
software, one computer being powered on and connected. This system is
built around at least two independent ways of hearing the
same over-the-air reports — one tied to your own local hardware, and
one that keeps working even if that hardware is down — plus a separate
channel for reports that arrive by email instead of radio at all. Each
channel is deliberately built so a failure in one doesn't take the
others down with it.


Each channel breaks down into the same small set of jobs:

| Piece | Its one job | Scope |
|---|---|---|
| The **fetcher** | Logs into that channel's source (your radio software, an internet-based feed, an email account) and asks, "any new messages?" | one per channel |
| The **reader** | Takes one message and figures out what it actually says | one per channel |
| The **filing cabinet** | Saves each report — each channel writes only its own file, so no two channels ever fight over the same data | one per channel |
| The **conductor** | Runs that channel's fetcher, reader, and filing cabinet, in order, on its own schedule | one per channel |
| The **publisher** | Takes everything currently saved, across *every* channel, and updates the public map together | shared, runs once per update |


**Steps:**
1. Get the code onto your small computer. This system's code is kept on
   **GitHub**... *(unchanged)*
2. Install Python... *(unchanged)*
3. Set up a **separate file just for your passwords and logins** —
   covering every channel's credentials, not just one — kept completely
   apart from the actual program files.
4. **Build and test one channel fully before starting the next.**
   Confirm its fetcher can log in and pull messages, and that a real
   test report makes it into that channel's own file, before touching
   the next channel or wiring anything into the shared publisher.
   Don't skip this — testing one piece, and one channel, at a time is
   exactly how a real, hard-to-spot problem[¹] got caught in the system
   this manual is based on: several channels were each written and
   tested individually, and everyone assumed they were already running
   together — they weren't, and real reports never reached the
   map with no error showing up anywhere.
5. Once a channel's conductor runs cleanly by hand, set it up to run
   automatically and repeatedly on its own schedule.[²] A channel tied
   to your own hardware is a reasonable thing to gate behind the manual
   on/off switch in step 6. A channel that runs independently of your
   hardware — an internet-based feed, an email account — doesn't need
   to wait on that switch at all; it can run continuously on its own
   schedule, since it isn't tying up your local radio or keeping your
   own computer powered on.
6. Add a simple on/off switch, reachable from a web browser with a
   password, for the channel(s) tied to your own hardware — so you (or
   another trained operator) can turn that piece on before an event and
   off afterward, from anywhere. This switch is scoped to your
   hardware-tied channel only — it doesn't start or stop any channel
   that already runs on its own independent schedule.[³]

---

## 2.3 Database & Map Setup

**What this part is:** a simple online spreadsheet-style database where
reports can be entered by hand (as a backup method, and for anything
that doesn't come in over APRS), plus a public map webpage that displays
pins from both the automatic feed and the hand-entered database side by
side.

**Steps:**
1. Create a free account with a simple database service (this system
   uses one called **Grist**) under your club's shared email.
2. Create one table with a column for each piece of information a report
   needs — category, status, location, timestamp, and so on — matching
   your own field format (see Part III).
3. Create a free account with a public mapping service (this system uses
   one called **uMap**), also under your club's shared email.
4. Set up **two separate layers** on the same map: one that reads
   directly from your hand-entered database, and one that reads from the
   automatic pipeline's output. Both can show pins on the same map at the
   same time.
5. For each category and status your reports can have, set a rule on the
   map telling it what color and icon to use. **The exact spelling and
   capitalization has to match perfectly between your database, your
   pipeline, and your map's rules** — even one different character means
   a pin will show up **unstyled**, with no error or warning
   anywhere.[⁴] This one actually cost real time to track down during
   testing of the system this manual is based on — not because anyone did
   anything wrong, just because a computer treats two almost-identical
   words as completely unrelated. People are far more forgiving of a
   close match than code is. Worth testing this one carefully up front,
   so you don't lose the same time we did.
6. **Test with one real, made-up report before trusting this for real
   use:** enter a test report, confirm the correct pin, color, and popup
   text appear on the map. Do this for both layers separately.

---

## 2.4 Remote Access (So You're Not Tied to One Location)

**What this is for:** letting you, and any trained operator, reach the
small computer's on/off switch (Section 2.2, step 6) and check on things
from anywhere — home, an EOC, on the road — without needing to be
physically near it or connected to its home network.

**Steps:**
1. Create a free account with a private networking service (this system
   uses one called **Tailscale**) under your club's shared email.
2. Install it on the small computer, and log it into your account.
3. Install the same service on every device that needs access — your own
   phone or laptop, and eventually each trained operator's device too.
4. Once a device has this installed and logged in, it can reach the
   small computer's web address directly, securely, from anywhere with
   an internet connection — home WiFi, cellular data, another network
   entirely, it doesn't matter.[⁵]

---

## Notes for Part II

**[¹] Why testing one piece at a time actually matters.**
It's tempting to write all the pieces at once and only test them
together at the end. In practice, that makes it much harder to tell
which piece is actually broken when something doesn't work — and in the
real system this manual is based on, exactly that happened: several
pieces were each written and tested individually, and everyone assumed
they were already working together as one connected process. They
weren't — nothing was calling them in sequence, so real reports
went out over the radio and never made it to the map, without any
error showing up anywhere. Testing one piece at a time, and then testing
the whole chain together deliberately, catches exactly this kind of gap.

**[²] Why "runs automatically" needs an on/off switch, not just "always
on" — but only for the channel tied to your own hardware.**
It might seem simpler to have every channel checking for new messages
constantly, all the time, forever. For your hardware-tied channel,
there's rarely a need for that outside an actual emergency — and having
an explicit on/off switch means it's only using your own radio, your own
computer's uptime, and your own internet connection when there's a real
reason to. That channel defaults to **off**, and someone turns it on
deliberately when it's actually needed, then off again afterward.

Your channel(s) that run independently of your own hardware are
different on purpose. Checking continuously costs nothing extra of
yours — no local radio, no local computer staying powered on — so
there's no reason to gate them behind the same switch. Letting them run
on their own schedule around the clock is exactly what makes them a
genuine backup: if your hardware-tied channel is off, or your hardware
itself is down, those channels keep working regardless. Gating
everything behind one shared switch would silently undo the reason a
second, independent channel was built in the first place.

Worth thinking about each channel's checking interval the same
deliberate way, independent of whether it's toggled or continuous. It's
tempting to assume "more often is always better," but that's not
necessarily true — if your local APRS frequency tends to get busy or
crowded during a real event, reports may only be getting through the
shared airwaves occasionally in the first place, no matter how often any
channel checks for them. Checking faster than real reports can actually
arrive doesn't gain you anything, and just uses more of your radio,
computer, and internet resources for no benefit. A good interval is one
that matches how busy your own local frequency realistically gets —
worth a conversation with other local operators who know that frequency
well, rather than guessing.

**[³] Why the on/off switch is a separate thing from the automatic
checking itself.**
These are set up as two independent pieces on purpose, for your
hardware-tied channel specifically: the switch itself should always be
reachable, even when that channel's automatic checking is turned off —
otherwise you'd have no way to turn it back on remotely. Keeping them
separate means the switch can be "always available" while the channel it
controls is "only running when needed."

Your independently-scheduled channels don't have this switch at all, by
design (see 2.2, steps 5–6) — there's nothing to keep
reachable-but-off, since there's no cost to leaving them running
continuously.

**[⁴] Why exact spelling matters so much here.**
Computers don't understand meaning the way people do — they check
whether two pieces of text match *exactly*, character for character. To
a person, "Food-open" and "Food-Open" obviously mean the same thing. To
the map's styling rules, they're two completely different, unrelated
values — and a mismatch doesn't cause an error message, it just leaves that one pin unstyled, gray or invisible, with nothing telling you why. This exact problem happened during real testing of this system, and took real effort to track down precisely because nothing failed in an obvious way. Carefully double- and triple-check every value match exactly Don't assume close-enough is good enough, close only counts in horseshoes, hugging, and atomic warfare.

**[⁵] A free, always-on helper that isn't your computer at all.**
Two of this system's channels don't run on your Pi, your radio, or your
internet connection — they run on **GitHub**, the same free service that
stores this project's code. GitHub offers a feature called **GitHub
Actions**: you give it a small program and a schedule, and GitHub's own
computers run it for you, for free, whether or not anything of yours is
turned on. This system uses that to check for new reports every fifteen
minutes, automatically, forever, at no cost — which is a useful thing to get for free, and worth appreciating rather than taking
for granted.

One of those channels checks **APRS-IS** — "IS" stands for **Internet
Service** — a shared internet feed that most local APRS stations
(including yours) already relay their over-the-air traffic onto. It's
how a website like aprs.fi shows APRS activity from anywhere, and it's
run by volunteers as a public service to the whole ham community, not by
this project. Background on how it actually works is at **aprs2.net**,
if you want to go deeper. Checking APRS-IS means this channel can hear a
report even if your own Pi and radio are completely off — as long as
*some* nearby station relayed it. That's the real value here: you get a
second way to capture reports without buying or running any extra
hardware.

What to keep in mind: this only helps if some station near the
reporting operator is relaying to APRS-IS in the first place. In an
area with few such stations, a report might never reach APRS-IS at all
— which is exactly why your own hardware-tied channel (2.1) still
matters as a fallback, not a redundant extra step. Also worth knowing:
GitHub's own free scheduling isn't perfectly precise for very-frequent
jobs like this one — expect checks roughly every 15–60 minutes in
practice, not a metronome-exact 15.

**Why not just open the small computer directly to the internet?**[⁶]
It's technically possible to make a home computer reachable from the
internet directly, without an encrypting service like Tailscale, by adjusting some
router settings. Doing it that way means the whole open internet can attempt to reach your computer, not just the people you've actually invited — every additional exposure like that is a chance for something to go wrong that has nothing to do with
this project. A private networking service instead only allows in the
specific devices you've personally approved, over a secure, invitation-
only connection — the same "give it only the smallest access it needs"
idea from Part I, applied to your network instead of a password.
A free tier on github makes Internet security one less hassle to deal with.

---

# Part III (Making It Yours) picks up next — your category list, field
format, staleness timing, corroboration rules, and local reference
resources.*

---

# PART III — Making It Yours

Everything in this part is meant to be rebuilt, not copied. Nothing here
came from a rulebook — it came from one club, in one county, working out
what fit their own area. Yours will look different, and it should.
Nobody who wasn't there with you during your last storm knows your roads,
your shelters, or your radio traffic better than you and your own
operators do — so treat everything below as a worked example to learn
the *method* from, not a checklist to copy word for word.

---

## 3.1 Building Your Own Category List

**The method, not the answer:** start from the actual hazards your area
faces, not from someone else's list. Ask your own experienced operators
and local emergency contacts: *"What did people actually need to know
during our last real event?"*

**Worked example, to show the method in action:** a county well inland,
prone to wind damage and long power/water outages, might land on
categories like shelter, medical, road, water, food, fuel, power, cell
signal, ATM access, and a general health-and-welfare relay. A small town
right on the Gulf coast, though, is looking at a different mix of real
dangers — storm surge, evacuation routes, marina and boat-launch
conditions — so its list might swap some of those out entirely for
things like **evacuation route status**, **storm surge/levee
conditions**, or **marina/boat-launch status**. Neither list is more
"correct" than the other — each fits the place it was built for.

**Steps:**
1. Gather your own experienced operators and ask what mattered most last
   time, or what they worry about most next time.
2. Aim for somewhere around eight to twelve categories — enough to cover
   real needs, few enough that someone can remember them without looking
   them up.
3. For each category, pick a short 2–4 letter specifier code (e.g. a
   status of shelter capacity, or type of road hazard) — same idea as
   the worked example, just your own list.
4. Write your final list down somewhere every operator can easily find
   it — this becomes the actual reference card operators use in the
   field.

---

## 3.2 Your Field-Format Grammar

**What this is:** the short, consistent pattern a report gets typed
into, so it can be read by both a person and a computer without any
confusion.

**Steps:**
1. Pick your own short prefix, in place of something like `KCGR-`, that
   ties every report clearly to your project (e.g. your county's
   initials plus "RS" for "resource status," or similar).
2. Decide your field order — most systems put status first, then a
   short category-specific code, then a plain-text location, then a
   timestamp last. This order isn't sacred; what matters is picking one
   order and using it consistently, so operators develop a habit around
   it.
3. Keep the whole thing well under your actual length limit — and it's
   worth knowing there are genuinely two different numbers here,
   depending on which part of APRS you're using. A one-to-one APRS text
   message can hold around 60–70 characters. But the **object beacon**
   format this whole system is actually built around — the one that
   creates a labeled pin at a location — has a much tighter limit, often
   around **43 characters** for the descriptive part of the message.
   That's a real constraint, not a rounding error, and it's exactly why
   the field-format grammar needs to be short and abbreviated rather than
   free-flowing sentences. Check which limit actually applies to your own
   setup before finalizing your format. 🔧
4. Write a handful of realistic worked examples, using real local place
   names, and put them directly on whatever reference card or webpage
   operators will actually look at in the field. An abstract rule is
   much easier to follow once you've seen it filled in with a real,
   familiar example.

---

## 3.3 Setting Your Own Staleness Timing

**The method:** rather than picking numbers that sound reasonable, look
at how *your* area actually recovered from a real past event, and match
your timing to that.

**Steps:**
1. Group your categories into a few speed tiers — some things (cell
   service, road status) tend to change within a day; others (shelters)
   stay accurate for closer to a week; still others (water systems,
   power in hard-hit rural or low-lying areas) can take weeks.
2. For each tier, look for real historical recovery data from a past
   event in your own region if you can find it — a coastal town's power
   and water recovery curve after storm surge flooding looks very
   different from an inland county's after wind damage, so don't assume
   another area's numbers apply to yours.
3. Write down your chosen window for each tier, and *why* you picked it
   — future you, or your successor, will want to know the reasoning
   later, not just the number.
4. Treat these numbers as a first draft. Revisit them after your system
   gets used in a real event or a serious exercise — real experience
   beats an educated guess every time.

---

## 3.4 Corroboration Distance

**What this is:** how close together two reports need to be before the
system treats them as "the same real-world thing," rather than two
separate locations.

**Worth knowing first — how much precision a coordinate actually has.**
GPS coordinates are just numbers with decimal places, and it's easy to
assume more decimal places always means "more precise" without a sense
of what that actually means in real distance on the ground:

| Decimal places | Roughly this precise |
|---|---|
| 1 | ~11 km (about 7 miles) |
| 2 | ~1.1 km (about ⅔ mile) |
| 3 | ~110 meters (about a football field) |
| 4 | ~11 meters (about a car length) |
| 5 | ~1.1 meters |
| 6 | ~11 centimeters |

This matters directly for this section: if your data source only gives
you coordinates to 3 decimal places, setting your corroboration distance
tighter than about 110 meters doesn't actually gain you anything — you'd
be asking for more precision than your own data can really deliver.

**Steps:**
1. Start somewhere in the range of 50–150 meters as a first guess — this
   is roughly what similar crowd-reporting projects have landed on
   before, so it's a reasonable starting point, not a rule.
2. Think about your own area's geography — a dense small town might want
   a tighter number, so two nearby-but-different locations don't get
   collapsed into one pin by mistake; a spread-out rural area might
   reasonably want a looser one.
3. Adjust after real use, the same way as your staleness timing above —
   this is a dial to tune, not a one-time decision.

---

## 3.5 Your Vetting Policy

**What this is:** deciding who gets trusted automatically, and who needs
a second confirmation first.

**Steps:**
1. Decide, together with your local ARES/RACES leadership and EOC
   contact, which channels count as automatically trusted. A common,
   reasonable starting point: any licensed ham radio operator's report
   through your radio system is trusted automatically, on the reasoning
   that the license itself already verifies who they are (see Part I,
   note 5).
2. Decide which other channels — a public web form, a different radio
   service, unsolicited tips — need a second person to confirm before
   posting, rather than posting automatically.
3. Write this policy down somewhere public-facing (your own version of
   an operations FAQ page), so operators and the public both know how
   it works, rather than leaving it as an internal assumption.

---

## 3.6 Local Reference Resources

**What this is:** a short list of official, already-existing sources of
information — road conditions, power outages, shelters, and so on — that
your operators and the public can check alongside your own map. This
list is almost entirely local, and needs its own research for your area
— state DOT road-condition sites, your state's power-outage tracking
tools, your regional Red Cross or equivalent shelter listings, and any
local water utility or boil-water advisory pages all vary by state and
county. 🔧

Build this list once, check that every link still works before an actual
event, and revisit it occasionally — these resources tend to change more
than you'd expect.

---

# PART IV — Running It

Parts I through III got the system built and made it your own. This
part is different — it's less about code and configuration, more about
the people who actually run this when something's happening. Everything
below assumes Parts II and III are already done: your pipeline exists,
your categories are picked, your database and map are live.

---

## 4.1 Filing a KCGR Report

**Two channels reach the map automatically: APRS and Winlink.** Both
skip the database entirely — a correctly formatted report on either
channel appears on the public map with no one manually entering it.

**APRS.** Send a `KCGR-<CATEGORY>` object beacon with your status,
specifier, location, and timestamp packed into the comment field. The
full field grammar, category list, and status/specifier codes are
kept in one place — your Quick Start reference — rather than repeated
here, so operators always look in the same spot and it can't drift out
of sync with this manual.

**Winlink, with the form installed.** File the **KCGR Resource
Status** template (`winlink_forms/` in the repo) addressed to
`KCGR-OPS` — type the address yourself; the form's own "Send To"
field is a reminder only; it does not address the message. Up to 3
reports per message. See the README for install paths for Winlink
Express and Pat.

**Winlink, without the form.** Not every station will have the form
installed — someone relaying on your behalf from an unfamiliar client,
for instance. `winlink_forms/KCGR_NoForm_Winlink_Template.md` is a
plain-text, copy/paste version of the same message: address it the
same way, keep the section headers and field labels exactly as
written (that's the literal text the automated parser matches on),
and fill in the blanks after each colon.

**What happens if a field's wrong or missing — nothing is ever
silently lost:**
- A blank `Category` means that report block is treated as not filed
  and skipped — not an error, just as if it wasn't there.
- A `Category` that's filled in but not a recognized code still
  publishes — flagged for a human to clean up, never dropped.
- A missing or unrecognized `Status` auto-publishes as `UK -
  unknown` rather than being rejected.

Same design principle as the APRS side (Part III, 3.2): built for the
untrained sender, not just the trained one.

---

## 4.2 Training Operators

**Two roles, and why they're trained differently.**

Two distinct jobs sit inside "operating KCGR," even though the same
person sometimes does both:

- **Data-entry operators** — anyone entering a report by hand into your
  database, whether it arrived over a channel your automation doesn't
  cover (Facebook, Meshtastic, DMR, a phone call), or as a backup when
  the automated pipeline itself is down.
- **Validators** — whoever's reviewing what's already out there:
  checking incoming reports for anything that looks wrong, and watching
  for reports that should have made it onto the map but didn't.[¹]

**One rule every operator needs before their first shift:** report only
businesses, organizations, and charitable/public services — never a
private residence, regardless of category (full rationale in Part III).

**Steps:**
1. Walk every new operator through your field-format grammar and your
   own category list (Part III), using your own real worked examples —
   not the abstract rule alone.
2. Have data-entry trainees enter one real (test) report into the live
   database, start to finish, before an actual event.
3. Show validator trainees the **public map itself**, not just the
   database, and how to cross-check one against the other — the map is
   what the public sees, so that's what a validator should be judging.
4. Give every **data-entry operator** their own account on your
   database — not a shared login (Part I, note 6). Field operators
   reporting over APRS or Winlink never touch the database directly, so
   they don't need an account at all — only people doing manual entry
   or validation do.[⁵] 🔧
5. Add every new operator to your private network (Tailscale or
   equivalent) following your one-time device setup (see your Operator
   Manual) 🔧.
---

### GITHUB PERSONAL ACCESS TOKEN (P.A.T.) FOR THE ADMIN-PAGE REMOVAL PANEL

**Not to be confused with *Pat*, the separate Winlink client program
used elsewhere in this system — this is an unrelated credential issued
by GitHub itself, spelled out here in full every time to avoid the
mix-up.**

The admin page's report-removal tool depends on a GitHub Personal
Access Token (hereafter **P.A.T.**) that expires **8/14/2027**. If it
lapses, the toggle and status sections of the admin page keep working
normally — ***only the removal tool breaks***, and it fails with an
***authentication error*** rather than anything visible elsewhere on
the page.

If a removal attempt fails after this date, or if you're checking in
proactively around this date:
1. Generate a new fine-grained GitHub Personal Access Token at
   `github.com/settings/personal-access-tokens/new` — repository
   access: `kcgr-resource-feed` only; permissions: `Contents:
   Read-only`, `Actions: Read and write`.
2. Optionally validate it before trusting it: run `setup_pat.py` (in
   the repo root, from your own computer — not the Pi) to confirm the
   new token actually works against the repo and its workflows before
   it goes anywhere near `credentials.env`.
3. Update the `GITHUB_PAT` value in `~/.kcgr_secrets/credentials.env`
   on the Pi with the new P.A.T.
4. Restart the admin app.

Contact the Hub Operator if you're not sure how to do this. (See Part
VI for a fully click-by-click walkthrough of generating one of these
from scratch, written for someone who's never created a GitHub P.A.T.
before.)

---

## 4.3 Pre-Event Activation Checklist

**What "activation" means here.** Most of what you're activating
already runs on its own, all the time — your independently-scheduled
channels (an internet-based radio feed and Winlink/email, see 2.2)
don't wait for anyone to switch them on. What's still a technical step
is your hardware-tied fallback channel (the Pi's own local capture),
which stays off by default and someone has to deliberately turn on if
you want that extra layer running for this event.[²]

**Steps:**
1. If you want your hardware-tied fallback channel active for this
   event, turn it on (see your Quick Command Reference appendix) and
   confirm it shows as running. Your independently-scheduled channels
   need no action here — they're already checking on their own
   schedule.
2. Do one test entry directly in your database, and confirm the
   matching pin appears correctly on the public map before relying on
   it for real reports.
3. Notify your data-entry operators and validators that KCGR is active
   — this is the step that actually puts people watching, regardless of
   what any individual channel is doing.
4. If your EOC, CERT, or a net (Skywarn or otherwise) is activating
   around the same event, coordinate timing so KCGR can record live
   field reports as they come in — active and ready before other
   channels start generating them, not scrambling to catch up
   afterward 🔧.
5. Start a fresh paper handoff log for this activation (see Appendix E).
6. If your county EM office has agreed to help promote the map
   publicly, let them know it's live 🔧.

---

## 4.4 During-Event Operations & Monitoring

**Every operator confirms their own report reached the map — within one
hour, every channel, no exceptions.**[³]

**Watch for reports that never make it in.** Only your own automated
channels — your local radio capture, its independent internet-based
backup, and Winlink/email — get checked automatically. Anything relayed
over DMR, Meshtastic, Facebook, Skywarn, or any other channel depends
entirely on a person remembering to also put it in your database 
(getgrist in the case of the KCGR project). This
is a validator's main job during an active event — not just watching
what's already on the map, but watching for the gap.

**Handling a report that's clearly wrong.**[⁴]
1. Pull it using your removal tool.
2. Keep going — don't stop to fully investigate mid-event.
3. Note it (paper handoff log is fine) for a full review after the
   event.

**Shift changes.** Fill out the shift-end questions (Appendix E) before
you hand off, and hand the paper log to the next operator directly, not
left for them to find.

**If your own local internet goes down:** ask a station outside the
affected area to check the public map and relay status back to you over
voice or Winlink. The map itself doesn't depend on your local
connection — only your ability to check it does.

**Significant reports also go to your EOC directly**, using an ICS-213
General Message, per your relationship-building approach in Part I,
note 9 🔧.

---

## 4.5 Post-Event Wind-Down

**What wind-down means here.** Your independently-scheduled channels
don't need winding down at all — they keep running on their own
schedule whether or not anything's actively happening, same as before
the event. If you turned on your hardware-tied fallback channel for
this event (4.3, step 1), wind-down includes turning it back off.
Beyond that one optional step, wind-down is already mostly about people
and data, not infrastructure (see note 2).

**Steps:**
1. If you turned on your hardware-tied fallback channel for this event,
   turn it off once you're confident the event is truly over — not
   automatically, not on a timer (Part I, note 8: a person makes this
   call by hand). If you never turned it on, or don't use that channel
   at all, skip this step.
2. Fill out the post-event questions (Appendix E) while the event is
   still fresh — days later is fine, weeks later loses detail.
3. Clear out reports that are now confirmed resolved; leave anything
   uncertain marked unconfirmed rather than deleting it (Part I, note
   4).
4. Confirm your pipeline's automatic backup of the record store ran
   correctly before you consider the event fully closed.
5. If KCGR was formally activated alongside your EOC or CERT, let them
   know you're standing down too — don't let the relationship go quiet
   just because the event's over 🔧.
6. Fold anything worth remembering into your changelog / lessons-learned
   record (Part V) — especially anything that surprised you.
---

## Notes for Part IV

**[¹] Why data-entry and validation are trained separately.**
These are genuinely different skills, even when the same person ends up
doing both. Entering a report quickly and accurately is a narrow,
focused task. Validating is broad and comparative — noticing that
something's missing, stale, or doesn't match what the map shows. A
trainee taught only the first will enter reports well but may never
think to check whether *other* reports are missing. Teaching them separately, even briefly, makes sure both skills actually get developed.

[²] **Why activation is mostly just notifying people now**, with one
optional toggle left.**
Early on, "activation" meant turning the whole pipeline on — everything
lived on a single Pi at home, and there was no reason to poll for
reports around the clock if there was no active need. That's no longer
true for most of the system: your independently-scheduled channels
(2.2) already run continuously on infrastructure that isn't tied to
your home power or internet, so there's no real cost to leaving them
running all the time — anyone reporting in already "activates" that
part of the system just by sending a report, the same way a Skywarn
net-control operator activates a net simply by starting it, not by
requesting permission first.

What's left of the old toggle is scoped to a single, now-optional
fallback channel — your hardware-tied local capture, which still
defaults to off and still needs a deliberate switch, because it's the
one piece still tied to your own Pi being powered on and connected.
Update this note again if that channel is ever migrated off local
hardware too — at that point there'd be nothing left to switch, and
step 1 of both 4.3 and 4.5 would become unnecessary rather than just
optional.

**[³] Why every operator checks their own report, on every channel,
within an hour.**
No channel in this system gives you positive delivery confirmation.
There's no equivalent of an email bounce or a web request's success/
failure code — an APRS beacon can get stepped on by another station
transmitting at the same time; a Winlink message can fail mid-relay;
even inside the automated pipeline itself, pieces have been tested
individually and still failed silently together, with real reports
never reaching the map and no error anywhere to show it. So this isn't
a patch for any one channel's weakness — it's the one general safety
net that covers all of them equally, because none of them can be fully
trusted to fail loudly.

It's also genuinely efficient, not just redundant. A hub operator or
validator is doing broad, shallow monitoring — scanning everything at
once. A field operator checking their own one or two reports is doing
narrow, deep monitoring on exactly the item they have the most context
to judge — they know what they meant to send, and can catch a wrong
location or wrong code that a broad scan would miss entirely. One hour was chosen as tight enough to catch a dropped report while
the same operator is still on shift, before they move on and forget to
circle back.

**[⁴] Why "pull it, keep moving, review later" — and why the deeper
policy isn't written here.**
In an active emergency, something will go wrong — that's part of what
running the hub means. The system's existing design already trusts a
person to make imperfect, in-the-moment calls rather than waiting for
certainty (staleness timing, corroboration, vetting all work this way).
A clearly wrong report gets the same treatment: act now, review later.
What this section deliberately does *not* do is define a formal policy
for handling false or malicious reports — that question involves
judgment calls (intent, accountability, follow-up with the reporting
operator) that belong with a broader committee, not a unilateral answer
baked into a manual. Treat that policy as open until your club settles
it on purpose.

**[⁵] Why database accounts are scoped to roles, not everyone.**
As of 8/2026, Grist's free tier caps a team at three members; Grist has
announced this rising to ten by the end of August 2026, but that's
still a real ceiling, not unlimited seats. Handing every trained
operator a login — including field operators who only ever report over
APRS or Winlink and never open the database at all — would burn through
those seats fast for no operational reason. Scoping accounts to the
people who actually need direct access (data-entry operators,
validators) keeps you within the free tier longer, and is really just
Part I's smallest-necessary-access principle applied to seat count
instead of permission level. If your roster ever outgrows even the
higher seat cap, that's a real decision point for the club: pay for
additional seats, or move to self-hosting (already confirmed technically
workable — no hard cap there — though not obviously worth the added
maintenance burden unless the free tier truly stops fitting) 🔧.

---

# PART V — Keeping It Alive

Parts I through IV got this system built, made it yours, and running.
This part is different again — it's about what happens *after* that:
what a successor needs to find without you standing there, what a real
failure actually looks like when you're staring at it, and a place to
put what you learn so the next person (possibly a future version of
you) doesn't have to relearn it the hard way.

---

## 5.1 Third-Party Permissions Log

**What this is:** a living table of every outside account this system
depends on — who owns it, who can get into it, and how much they can
do once they're in. Unlike most of this manual, this section is
deliberately **not** meant to be reusable across clubs by design — it's
your own operational reality, specific to your accounts, filled with
your own real answers, not a generic template.

**Why this matters:** the same "smallest necessary access" principle
from Part I, applied at the level of *who can see this table at all*.
A successor who inherits this project cold needs to know what accounts
exist and who to ask before they need to know it in an emergency — not
discover it by trial and error while something's actively broken.

**Steps:**
1. Keep one row per outside service this system touches — not per
   credential, per *service* — so a reviewer can see the whole
   footprint at a glance.
2. Review this table on a fixed cadence (quarterly is reasonable), not
   only when something breaks. A credential that's still valid but
   nobody remembers exists is exactly as risky as one that's expired.
3. Update the "Last reviewed" column every time you touch a row — even
   if nothing changed. An untouched date tells you as much as a wrong
   one.

**Real, filled example** (this project's own accounts, as of the last
edit to this table — replace with your own):

| Service | Account owner | Who has access | Access level | Last reviewed |
|---|---|---|---|---|
| GitHub (`kcgr-resource-feed` repo) | Club GitHub org account, not a personal login | Hub Operator + each stand-in, via individual collaborator invites (see 5.2) | Repo write | 🔧 |
| GitHub Personal Access Token (P.A.T.)[²] | Stored in `~/.kcgr_secrets/credentials.env` on the Pi | Whoever can reach the Pi's admin app or its credentials file | `Contents: Read-only`, `Actions: Read and write`, scoped to `kcgr-resource-feed` only — **expires 8/14/2027** | 🔧 |
| Admin app (`kcgr-admin.service`) | `KCGR_ADMIN_PASSWORD`, one shared password | Anyone with the password and Tailscale access | Pipeline toggle + `/records` removal panel | 🔧 |
| Grist | Club shared email | Team members added directly in Grist | Per-seat, capped by the current plan tier — check before adding a new operator | 🔧 |
| uMap | Club shared email | Whoever needs to edit map layers or styling | Edit access is rare — most operators only ever need view | 🔧 |
| Tailscale | `kc4rc.fd@gmail.com`, not a personal account | Every device that's joined the tailnet | Personal plan — 6 users, unlimited devices per user | 🔧 |
| Gmail (`kc4rc.fd@gmail.com`) | Club shared account | Hub Operator, primary; forwarding rules also route copies elsewhere | 2FA via authenticator app + a scoped App Password ("KCGR Automation") powering the Winlink poller; 10 backup codes stored on paper and in a password manager | 🔧 |

---

## 5.2 Access Control & Succession

**What this is:** how a new stand-in Hub Operator actually gets set up
— and the reasoning behind why access works the way it does, so a
future maintainer doesn't "simplify" it back into something
this project already deliberately moved away from.

**The decided policy:**
- Each stand-in Hub Operator gets their **own individual GitHub
  account**, granted repo write access directly — never a shared
  account, never a shared login.
- Each account enrolls its **own independent TOTP 2FA** (an
  authenticator app or a hardware key) — deliberately **not**
  SMS-based, and **not** one shared TOTP secret handed to multiple
  people.
- This reuses the access boundary the project already trusts — GitHub
  repo write permission — instead of building a second, separate
  authentication system just for this project.

**Steps, for onboarding a new stand-in operator:**
1. Have them create their own free GitHub account, if they don't
   already have one.
2. Have them enroll independent TOTP 2FA on that account before you
   send an invite — an authenticator app or hardware key, not SMS.
3. Send a collaborator invite from the `kcgr-resource-feed` repo
   directly to their account.
4. Once accepted, confirm they can actually reach the admin app over
   Tailscale (see 2.4) — GitHub access and admin-app access are two
   separate things, and a new operator needs both.
5. Log the new row in the permissions table (5.1) the same day —
   waiting "until things settle down" is exactly how a table like this
   goes stale.

**Still open, not yet decided:**
- A friendlier setup path for the `GITHUB_PAT` itself, for a future
  Hub Operator who's never created one before. Three options have been
  discussed — a proper GitHub App install/authorize flow, a setup
  script that still uses a PAT but automates writing it to
  `credentials.env`, or simply documenting the current manual process
  well as a real worksheet. None of these is blocking today's use of
  the removal panel; this is a real decision the club hasn't made yet,
  not an oversight.
- A second director's phone number as a backup 2-Step Verification
  method on the shared Gmail account, in case the primary
  authenticator device is unavailable.
- Who actively checks the shared Gmail inbox, and how often — a
  decision the club needs to make on purpose, not default into.

**Out of scope for this section:** someone outside your own area
adapting this system for their own county or region should **fork**
the repository rather than receive collaborator access to this one —
that's a separate guide, not yet written, and belongs on its own
rather than folded into succession planning for *this* project's own
operators.

---

## 5.3 Troubleshooting & Recovery

**What this is:** not a list of every bug this project has ever hit —
those live in the changelog (5.4) — but the *patterns* behind them,
generalized so you recognize the shape of a new problem even if the
specific cause is different. Every pattern below was learned from a
real failure, not anticipated in the abstract.[¹]

| If you're seeing... | It's likely because... | Check this first |
|---|---|---|
| The public map isn't updating, even though a channel's own data file looks correct | The publishing step's own trigger file may be silently broken — a single malformed line can disable **every** way that step can run, not just the one you happen to be testing | Open that workflow's own run history directly and read what it actually says, rather than assuming a `push` not firing means only that trigger is affected |
| A scheduled channel just stops producing anything, with no visible error | A file may have been silently overwritten with the wrong content — easy to do by accident when uploading several similar files back-to-back | Open an actual recent run's log, not just its pass/fail status — a wrong-content crash and a real success can look identical from a run *list* alone |
| A run's log looks unusually repetitive, and you're not sure if that's normal | Output may be getting buffered and never reaching the log at all, especially in a non-interactive scheduled environment | Force unbuffered output before trusting a quiet log as meaningful, not just when something's already suspected wrong |
| A category, status, or lookup value isn't matching even though it looks right in the log | A fixed-width or padded data format may be leaving invisible extra whitespace in the value | Read the actual stored value directly (not a formatted log line) — trailing whitespace is often invisible in normal output |
| Something you fixed still seems broken, or you're not sure if it's really fixed | A description of a change (a commit message, a checkmark, a "done" note) isn't the same thing as confirming the change | Re-verify against real evidence — the actual file content, the actual log line, the actual live page — every time, not just once |

**General recovery steps, once you've identified what's actually
wrong:**
1. Fix the root cause, not just the visible symptom — a silently
   broken trigger file and the data it should have published are two
   separate things that both need checking.
2. Verify the fix with real evidence at every step it touches, not
   just the last one.
3. Log it in the changelog (5.4) before moving on — even a fix that
   feels obvious in the moment is easy to forget the reasoning behind
   later.

---

## 5.4 Append-Only Changelog

**What this is, and how it's different from the rest of this
manual.** Every other part of this document describes your system as
it currently is — when something changes, you update the relevant
section in place. This section is the opposite on purpose: entries get
**added**, never rewritten or deleted, even after the thing they
describe gets fixed or replaced. A troubleshooting guide tells you what
to do; this tells you what actually happened, in order, so a pattern
across multiple incidents is visible later even if no single entry
looks alarming on its own.

**Steps:**
1. Add a dated entry whenever something breaks, gets fixed, or
   surprises you — while it's fresh, not from memory weeks later.
2. Write what actually happened and how it was actually confirmed, not
   just what you assume caused it.
3. Never edit or delete a past entry, even if it turns out to be
   wrong or incomplete — add a new, dated entry correcting it instead.
   The record of *being* wrong for a while is itself useful information
   for a future reader.

**Seed entries** (real, to show the format — keep adding below these,
don't replace them):

- **[date]** — A single mis-indented line in a workflow's own trigger
  configuration silently disabled every way that workflow could run —
  push, chained trigger, and manual click alike — for several hours,
  with no error visible anywhere an operator would naturally look.
  Fixed by re-indenting; confirmed via a real end-to-end test
  afterward, not just a clean-looking file.
- **[date]** — A poller script was found holding a different, unrelated
  script's content after a multi-file upload session — every scheduled
  run crashed instantly for hours before this was caught. Restored
  from a known-good backup; confirmed with a real successful run
  afterward.
- **[date]** — A wire format's fixed-width padding survived unstripped
  into a lookup key, silently misclassifying several categories as
  "unknown" with no error anywhere. Caught only by reading the raw
  stored value directly. Fixed by explicitly stripping the value
  before using it as a key.

---

## Notes for Part V

**[¹] **Why this section teaches patterns** instead of listing every past
bug.** A list of exactly what broke before is useful once, for
recognizing the *same* problem again — but it doesn't help with the
next, different problem. The changelog (5.4) is where the specific
history lives; this section exists to make that history transferable,
so a future maintainer facing a new symptom still recognizes
the shape of it from a pattern they've seen described here.

**[²] Why this is always spelled out as "P.A.T." with periods.** This
system also uses a completely unrelated program called *Pat* for
Winlink. "PAT" as a bare acronym and "Pat" as a program name look
identical on the page — spelling it out as "GitHub Personal Access
Token" on first use in any section, and using the punctuated "P.A.T."
as shorthand after that, is a small, deliberate habit meant to keep the
two from ever getting confused by a reader skimming quickly.

---

# PART VI — Adapting This System For Your Own Area

Everything built in Parts I–V belongs to one club, in one county. This
part is for someone else entirely — a different county, a regional ARES
group, or a statewide effort — who wants their own, fully independent
version of this system: their own repository, their own database, their
own map, sharing none of the original project's actual data or
accounts.

**This part is deliberately hypothetical in one specific way.** The
naming examples used throughout — swapping `KCGR-` for something like
`MGS-` (a regional Midlands group) or `SCGR-` (a statewide effort) — are
illustrative possibilities, not an announced plan. They exist here in
the hope that more of the state gets involved, not as a commitment any
group has made. Treat them as a worked example to learn the method
from, exactly the same way Part III treats its own category-list
example.

---

## 6.1 Why Fork, Not Ask for Access

**The short version:** you're building your own separate copy of this
system, not borrowing a seat in someone else's. On GitHub, that's called
**forking** — it makes you a complete, independent copy of the code,
under your own account, that you can change freely without touching the
original project at all.

This matters for two real reasons:
- **Your data stays yours.** A fork never shares reports, credentials,
  or map data with the original project — it's a separate system from
  the moment it's created.
- **Nothing you do can break the original.** You're free to rename
  things, experiment, and make mistakes in your own copy without any
  risk to the project you copied it from.

**The original project's own documentation already anticipated this.**
Its format was built around a deliberate three-step "prefix ladder,"
designed in from the start rather than added later:

| Prefix | Covers | Length |
|---|---|---|
| `KCGR-` | Kershaw County | 5 characters |
| `MGS-` | Midlands (regional) | 4 characters |
| `SCGR-` | South Carolina (statewide) | 5 characters |

**Why the lengths matter, not just the names.** Every character inside
an APRS object beacon's comment field is scarce — the whole format was
built around a hard 43-character limit. `MGS-` is one character
*shorter* than `KCGR-`, which actually gains you one character of room
elsewhere in the message. `SCGR-` is the same length as `KCGR-`, so a
statewide adoption ports over with no restructuring needed at all.

**The prefix is deliberately the *only* thing meant to change at a
larger scale.** Per the original project's own documentation: field
order and specifier codes are load-bearing — they're what keeps the
format self-describing and readable under stress, without a lookup
table. If your own group ever proposes changes beyond a renamed prefix,
the original author's stated guidance is to shorten or replace the
prefix further before touching field order or eliminating codes, not
the other way around.

**Worth knowing, in the original author's own words:** this format was
"developed June 2026 by AA4TE, Camden SC, EM94, KC4RC / Kershaw County
ARES... not a final standard — for review by Kershaw County ARES EC,
Midlands Section 3, and SC ARES." In other words: exactly as hypothetical
as it sounds when you first hear about it. Forking today doesn't require
waiting on any of that review to happen — a single county adopting this
independently, with its own prefix, is a complete and valid use of
everything in this part, with or without a larger regional or state
effort ever materializing.
---

## 6.2 Before You Start: What You'll Need

- [ ] Your own group's shared email address (not anyone's personal
      email — see the reasoning in Part I, note 7, which applies here
      just as much as it did to the original project)
- [ ] Someone comfortable clicking through unfamiliar websites and
      following instructions closely — you do **not** need a
      programmer for anything in this part
- [ ] Your own small always-on computer (Part II, 2.1) — this is not
      shared with the original project either
- [ ] About an hour of uninterrupted time for the account-creation
      steps below — they go faster if you're not stopping and starting

---

## 6.3 Creating Your Own Copy of the Code (Forking on GitHub)

**Step-by-step, starting from nothing:**

1. Go to **github.com** in your web browser.
2. If you don't already have a GitHub account:
   - Click **Sign up** (top right corner).
   - Enter your group's shared email address, choose a password, and
     choose a username — pick something that identifies your group
     clearly (e.g. `mgs-groundreport`), since this becomes part of your
     project's public web address.
   - Follow GitHub's verification steps (usually a code sent to your
     email).
3. Once logged in, go to the original project's repository page: 🔧
	**https://github.com/taco40sauce/kcgr-resource-feed**

*(fill in the real address — ask whoever shared this manual with
   you if you don't have it)*
4. Near the top right of that page, click the **Fork** button.
5. On the screen that appears:
   - **Owner**: leave this as your own account/organization.
   - **Repository name**: replace `kcgr-resource-feed` with your own —
     e.g. `mgs-resource-feed` or `scgr-resource-feed`.
   - Leave "Copy the main branch only" checked (the default).
6. Click **Create fork**.

**You now have your own, completely independent copy of the code**,
at your own web address (`github.com/[your-username]/[your-repo-name]`).
Nothing you do to it from here affects the original project at all.

---

## 6.4 Choosing and Renaming Your Own Prefix

**What this is:** every category, file, and workflow in the original
project uses the prefix `KCGR-` (short for the original project's own
name). Your copy needs its own prefix, consistently applied everywhere
— the same exact-spelling principle from Part II, note [4], applies
here at a larger scale: a computer treats `KCGR-` and `MGS-` as
completely unrelated text, so every occurrence needs to be found and
changed, not just the obvious ones.

**Before you rename anything**, do the character math for your own
prefix** (see 6.1) — a shorter prefix than `KCGR-` gains you room in
the 43-character field; a same-length prefix (like `SCGR-`) needs no
adjustment; a longer prefix costs you room elsewhere and may force
trimming your location or comment fields shorter than the original
project's own examples.

**Steps:**
1. Pick your own short prefix (Part III, 3.2, step 1 covers how) —
   for this walkthrough, we'll use `MGS-` as the worked example.
2. In your forked repository's page on GitHub, click the **magnifying
   glass search icon** near the top of the page (or press `/` on your
   keyboard while viewing the repo).
3. Type `KCGR-` and press Enter. This searches every file in your
   repository for that exact text.
4. GitHub shows you a list of every file containing a match. Click
   into each one, one at a time.
5. Inside a file, click the **pencil (edit) icon** near the top right
   of the file view.
6. Use your browser's own find function (`Ctrl+F` on Windows/Linux,
   `Cmd+F` on Mac) to jump to each occurrence of `KCGR-` inside that
   file, and manually type your own prefix in its place.
7. Once you've replaced every occurrence in that file, scroll down and
   click **Commit changes** (a short description like "Rename prefix
   to MGS-" is fine).
8. Repeat steps 4–7 for every file in the search results from step 3.
9. **Re-run the search from step 2 and 3 again after finishing** — a
   fresh search for `KCGR-` should now return zero results across your
   whole repository. If it doesn't, you've missed one — go fix it
   before moving on.

**Places this prefix shows up that are easy to miss:** workflow *names*
(not just file names) inside `.github/workflows/` files, category names
inside any parser code, and any text on your web pages (`kcgr-start.html`
and `kcgr-ops.html` equivalents) — not just the technical files. Treat
the search in step 9 as your real check, not a mental list of "the
obvious spots."

---

## 6.5 Setting Up Your Own Database (Grist)

**Step-by-step:**

1. Go to **getgrist.com** in your web browser.
2. Click **Sign up** (top right).
3. Enter your group's shared email address and create a password.
   Follow the verification steps.
4. Once logged in, you'll land on your **team site** home page. Click
   **Create empty document** (or **+ New**, then **Document**,
   depending on the current Grist interface).
5. Give the document a name matching your own project — e.g.
   `MGS-ResourceStatus`.
6. Grist opens a blank document with one empty table. Rename it by
   clicking the table's current name (usually "Table1") at the top and
   typing your own name — e.g. `Reports`.
7. Build your columns to match your own field format (Part III, 3.2).
   For each column, click the **+** at the far right of the column
   headers to add a new one, then click the column's **dropdown arrow**
   → **Column Options** to set its type:

   | Column | Type to choose | Notes |
   |---|---|---|
   | `ObjectName` | Choice List (dropdown) | Fill in your own category list from Part III, 3.1 |
   | `Status` | Choice List (dropdown) | Your own status codes |
   | `Specifier` | Choice List (dropdown) | Your own specifier codes |
   | `Location` | Text | Free text |
   | `Notes` | Text | Free text |
   | `ReportedBy` | Text | Free text — agency names and callsigns both fit here |
   | `DateTime` | Date/Time | Set your own display format |
   | `Latitude` | Numeric | Plain decimal degrees |
   | `Longitude` | Numeric | Plain decimal degrees |
   | `Verified` | Toggle (checkbox) | Internal team reference only |
   | `ReportCount` | Numeric | Internal corroboration bookkeeping only |

8. To fill in a **Choice List's** actual options (e.g. your category
   list), click the column header dropdown → **Column Options** →
   find the **Choices** field → type each option on its own line,
   matching your Part III category list exactly, including your own
   prefix.
9. To share access with your own team: click **Share** (top right),
   enter each teammate's email, and choose their role — most
   data-entry operators only need **Editor**, not **Owner**.

---

## 6.6 Setting Up Your Own Public Map (uMap)

**Step-by-step:**

1. Go to **umap.openstreetmap.fr** in your web browser.
2. Click **Log in** (top right). If you don't already have an
   OpenStreetMap account, click the option to create one — it's free
   and separate from Grist/GitHub.
3. Once logged in, click **+ Create a map**.
4. Give your map a title matching your own project.
5. Use the map's pan/zoom controls to center the default view on your
   own coverage area, then click the **wrench/settings icon** →
   **Save current view as default**.
6. Add your layers — click the **layers icon** on the left side, then
   **+ Add a layer**:
   - One layer reading from your own automated pipeline's published
     file — point it at your own fork's raw GeoJSON address, e.g.
     `raw.githubusercontent.com/[your-username]/[your-repo-name]/main/[your-geojson-filename]`
   - One layer reading from your own Grist table, following Grist's
     own current instructions for sharing a table as a live data
     source (this changes from time to time on Grist's side — check
     their current documentation for the exact steps 🔧).
7. For each layer, set styling rules matching your own category and
   status list — click a layer → **Edit properties** → set colors and
   icons per value. **Match spelling exactly** between this map, your
   Grist columns, and your codebase's category list (Part II, note
   [4] — the same invisible-mismatch trap applies here, just in a new
   system).
8. Click **Save** (top left), then find your map's public sharing link
   under the **Share** option to give to your own operators and the
   public.

---

## 6.7 Setting Up Your Own Private Network (Tailscale)

Follow Part II, 2.4, exactly as written — this step doesn't change at
all between the original project and your own fork. Create your own
account under your own group's shared email; don't reuse or request
access to the original project's tailnet.

---

## 6.8 Generating Your Own GitHub Personal Access Token (P.A.T.)

**Not to be confused with *Pat*, the separate Winlink client program —
this is an unrelated credential issued by GitHub itself.**

**Step-by-step:**

1. Log into your own GitHub account (the one from 6.3).
2. Click your **profile picture** (top right corner) → **Settings**.
3. Scroll to the very bottom of the left sidebar and click
   **Developer settings**.
4. Click **Personal access tokens** → **Fine-grained tokens**.
5. Click **Generate new token**.
6. Under **Token name**, give it a name that identifies what it's for
   — e.g. `MGS Removal Panel Token`.
7. Under **Expiration**, choose a duration — one year is a reasonable
   default. Whatever you pick, **put a calendar reminder a few weeks
   before that date now**, while you're already here — this token
   will eventually need to be regenerated, and there's currently no
   easier path than doing this manually.[¹]
8. Under **Repository access**, choose **Only select repositories**,
   then pick your own forked repository from the list.
9. Under **Permissions**, tap **Add permissions**. Check the boxes for
   **Actions** and **Contents**. Once you do, a third item —
   **Metadata (Required)** — "Search repositories, list collaborators,
   and access repository metadata" — may appear automatically in the
   Repositories box. Metadata's access level is greyed out and can't be
   changed; leave it alone.
   - Find **Actions** in the list and change its dropdown from the
     default **Access: Read-only** to **Access: Read and write**.
   - Find **Contents** in the list — its dropdown is active and could
     be changed, but leave it at the default **Read-only** (may also
     display as simply **Read**) — don't change this one, even though
     you can.
   - Leave every other permission at its default (**No access**).
10. A confirmation popup titled **"New personal access token"** will
    ask "Are you sure?" — write down or screenshot the token's name,
    the date, and the three settings shown (Actions: Read and write,
    Contents: Read-only, Metadata: Read-only or just Read) before continuing. This
    becomes your own record if anything needs troubleshooting later —
    the token itself is only ever shown once, but this confirmation
    screen is a second, useful place to capture the same details.
11. Scroll down and click **Generate token**.
12. **Copy the token immediately** — GitHub shows it to you exactly
    once. Paste it into your own credentials file (Part II, step 3)
    as `GITHUB_PAT=` followed by the token, with no spaces around the
    `=`. Never paste this token anywhere inside your actual repository
    files — it belongs only in the separate, private credentials file.

**Optional but recommended — validate it before trusting it:** run
`setup_pat.py` (in the repo root) from your own computer, not the Pi.
It's a standalone, stdlib-only script — no install step, nothing to
set up — that checks your new token against the real repo and the
three workflows the removal panel depends on
(`aprsis-removal.yml`, `winlink-removal.yml`, `merge-and-publish.yml`)
before you paste it anywhere. It does not write to your credentials
file itself; it prints the `GITHUB_PAT=` line for you to paste by
hand, same as step 12 above, just with the token already confirmed
working.
---

## Notes for Part VI

**[¹] Why this manual still says "regenerate it manually," rather than
something friendlier.** A friendlier setup path for this token was an
open question for a while — options considered were a proper GitHub
App install flow, a script that automates writing it to your
credentials file, or just documenting the manual process well.
**Decided:** a validation script (`setup_pat.py`, referenced in step 12
above) — not a GitHub App, and not documentation-only. It confirms a
newly generated token actually works against your repo and workflows
before you trust it, but deliberately doesn't write to your
credentials file for you; you still paste that line by hand.
Generating and *rotating* the token itself is still a manual process —
this script only removes the guesswork of whether a freshly generated
token is actually valid.

**[²] On the naming examples used throughout this part.** `MGS-` and
`SCGR-` are used here purely as worked examples, the same way Part III
uses an inland-county and a Gulf-coast-town example side by side to
teach a method, not to prescribe an answer. Nothing about adopting this
system requires coordinating with any other group's naming — a single
county forking this on its own, with its own prefix, is a complete and
valid use of everything in this part.




# APPENDIX A — Quick Command Reference (Start to Finish)

This appendix assumes your Raspberry Pi, radio, and Graywolf software are
already set up and running — see your separate station guide for the
actual hardware startup/shutdown/recovery steps. This appendix covers
just the KCGR automation piece: turning it on, checking it, removing a
bad report, and turning it off.

**A typical session starts like this:**

> Everything's set up — the pipeline is installed on the Raspberry Pi,
> and the public pages are live on our website. I've turned the Pi on,
> and Graywolf is up and running. Now I want to turn the automated
> reporting on, check that it's working, maybe remove a bad report, and
> turn it off again when I'm done.

Here's every command you'd need for that, in order.

---

### 1. Connect to the Pi

```
ssh dave@graywolf
```
🔧 *(replace `dave` and `graywolf` with your own username and hostname —
or use your Tailscale address instead if connecting remotely, e.g.
`ssh dave@100.68.180.65`)*

---

### 2. Turn the automated pipeline ON

**From the terminal:**
```
sudo systemctl start kcgr-pipeline
```

**Or from a web browser** (any device on your Tailscale network):
```
http://100.68.180.65:5050
```
Log in with the admin password, click **Turn ON**. 🔧

### 2  Alternative Turn the automated pipeline ON

**From the terminal:**

```
sudo systemctl start kcgr-pipeline
```


**Or from a web browser** (any device on your Tailscale network):
http://100.68.180.65:5050


**If the page doesn't load:** the admin panel itself
(`kcgr-admin.service`) is a separate service from the pipeline this
page controls, and may not be running. Check and start it from the
Pi's terminal:
---

### 3. Check whether it's actually running

```
sudo systemctl status kcgr-pipeline
```
Look for `Active: active (running)` in green.
```
sudo systemctl status kcgr-admin.service
sudo systemctl start kcgr-admin.service
```
Then reload the page. Once it loads, log in with the admin password
(from your credentials file — see Part I, note [⁶]) and click
**Turn ON**.
---

### 4. Watch it live (see reports come in as they happen)

```
journalctl -u kcgr-pipeline -f
```
Press `Ctrl+C` to stop watching — this does **not** turn the pipeline
off, it just closes the log view.

---

### 5. Run a single manual cycle (for testing, without waiting)

```
cd ~/kcgr-pipeline
python3 run_cycle.py
```
Useful right after sending a test report, so you don't have to wait for
the next automatic cycle.

---

### 6. Remove a report that shouldn't be on the map

**For reports on your two automated channels currently in active use
(APRS-IS and Winlink), use the browser-based removal panel instead of
the terminal:**

1. From any device on your Tailscale network, log into the admin page:
   ```
   http://100.68.180.65:5050
   ```
   🔧 *(use your own Tailscale address)*
2. Click **View/remove active records**, or go directly to:
   ```
   http://100.68.180.65:5050/records
   ```
3. Find the report in the list — labeled by source, category, status,
   location, and callsign — click **Remove**, then confirm on the next
   screen.

This updates the underlying data and republishes the public map
automatically — no need to touch uMap's own delete tools at all, since
deleting there doesn't actually stick.

**For a report that came in through this Pi's own local pipeline**
(the `data/records.json` channel — not your primary intake path, and
not yet covered by the browser panel above), use the terminal instead:

**First, find its exact identity:**
```
cat ~/kcgr-pipeline/data/records.json
```
Look for the entry you want gone — it's labeled something like
`"AA4TE-10:KCGR-FUEL"`.

**Then remove it, using that exact identity:**
```
cd ~/kcgr-pipeline
python3 remove_record.py "AA4TE-10:KCGR-FUEL"
```
🔧 *(use the real identity string from the file above — copy it exactly,
including the colon)*

This also updates the public map automatically — same underlying
principle as the panel above, just a different tool for a different
data source.

---

### 7. Turn the automated pipeline OFF

**From the terminal:**
```
sudo systemctl stop kcgr-pipeline
```

**Or from the web browser**, same page as step 2 — click **Turn OFF**.

---

### 8. Properly shut down the Pi itself (only if you're powering it off
entirely — not needed just to stop the pipeline)

```
sudo shutdown -h now
```
Wait 30–60 seconds after your SSH session disconnects before unplugging
power. See your station guide's Section 1 for the full explanation of
why this matters.

---

*End of Appendix A.*

---

# APPENDIX B — Opening Your Web-Based Tools

Appendix A covers the automated pipeline, which mostly lives in a
terminal. This appendix is for the tools most operators will actually
spend their time in — entering a report by hand, or checking the public
map itself. No terminal needed for anything below.

---

### Entering a report by hand (your database)

1. Go to your database site (this system uses **Grist**): 🔧
   ```
   https://getgrist.com
   ```
2. Log in with your account.
3. Open your team site, then your resource-status document (e.g.
   `KCGR-ResourceStatus`). 🔧
4. Click into the table, and add a new row — one row per report, filling
   in status, category, location, and so on, matching your own field
   format from Part III.
5. If you're marking something as officially checked/confirmed, use the
   `Verified` column (a simple checkbox) — this is for your team's own
   reference and does not change how it looks on the public map.

---

### Checking or editing the public map

1. Go to your map site (this system uses **uMap**): 🔧
   ```
   https://umap.openstreetmap.fr
   ```
   (or your own map's direct public link, if you have it bookmarked)
2. To just **view** the public map, no login is needed — anyone can see
   it, the same as any visitor would.
3. To **edit** the map itself (layers, style rules, settings) — not
   something most operators will need day to day — log in and open the
   map in edit mode.
4. **Important reminder:** don't use uMap's own delete/trash tool to
   remove a report from the automated feed layer — it doesn't actually
   stick (see Appendix A, Step 6, for the real way to remove a report).
   Deleting a hand-entered report from the manual-entry layer, though,
   should be done by deleting the actual row in your database instead,
   for the same reason — the map is just a display of data that lives
   somewhere else.

---

### County / partner agency spreadsheet (in progress)

🔧 *This section is being written as this integration is actually built —
placeholder for now.* Once a county or partner agency's spreadsheet is
connected as its own feed (see the note on this in Part I, section on
building an EOC relationship), this section will cover:
- Where to find their spreadsheet
- Who has permission to view or edit it
- How its data appears on the public map (as its own clearly-labeled
  layer, separate from ham radio reports and manual entries)

---
# APPENDIX C — Winlink Tactical Address Format Reference

This appendix covers the actual formatting rules for a Winlink tactical
address — the kind of address `KCGR-OPS` already is. It's built
entirely from Winlink's own official documentation (`winlink.org`),
not a third-party summary.

---

### What a tactical address actually is

**Not a callsign, and not treated as one.** A tactical address is a
functional email account inside the Winlink system — tied to a role or
project rather than a specific person — that's always associated with
one or more real amateur callsigns for sending and receiving.

---

### Format rules

- **Length:** 3 to 24 total characters, before `@winlink.org`.
- **Before any hyphen:** letters only, and at least 3 of them.
- **After a hyphen:** letters, numbers, or additional hyphens, in any
  combination.

| Example | Valid? | Why |
|---|---|---|
| `KCGR-OPS` | Yes | 4 letters before the hyphen, 3 alphanumeric after |
| `EOC` | Yes | 3 letters, no hyphen needed |
| `MGS-1` | Yes | 3 letters before the hyphen, a number after |
| `AB` | No | Fewer than 3 letters before any hyphen |
| `1CGR-OPS` | No | Starts with a number, not a letter |

**This project's own tactical address, `KCGR-OPS`, is fully compliant**
— worth confirming explicitly here rather than assuming, since nothing
about the format rules was checked against the real standard until now.
If you're building a renamed version for your own area (Part VI), the
same rule applies to whatever prefix you choose: `MGS-OPS` and
`SCGR-OPS` are both valid under this same rule, since both prefixes are
3+ letters.

---

### Password — not required, but worth setting

A tactical address doesn't require a password to receive mail. Without
one, though, it isn't secure, and nobody can log into the account on
Winlink's own website to manage its settings. Set a password for any
tactical address meant to last beyond a single short-term event.

---

### Filtering incoming internet mail (ACCEPTLIST)

Each tactical address has its own accept/reject list for internet
email reaching it — managed either on the account's own page at
`winlink.org` after logging in, or by sending a specially-formatted
message to the system itself from the tactical address. Full detail
isn't reproduced here; see the source link below if you need to
configure this.

---

### Which Winlink clients actually support this

**Supported:** Winlink Express (the preferred client) and Paclink.
**Not supported:** Airmail, or any other third-party client — a
tactical address won't work if your operators are using one of those.

---

### How long a tactical address stays active

Per Winlink's own FAQ documentation, a tactical address's registration
lapses after **6 months without use** — worth knowing if this project's
own `KCGR-OPS` address, or any address a forking group sets up under
Part VI, ever goes silent for an extended stretch between activations.

---

### Notes for Appendix C

**On the character-count discrepancy.** Winlink's dedicated "Tactical
Addresses" page (last updated April 2023) states the current limit as
3–24 characters. A separate Winlink FAQ document states a 12-character
limit. Since the dedicated page is the more specific, more recently
updated source, this appendix treats 3–24 as current. Either number is
irrelevant for `KCGR-OPS` itself, which fits comfortably under both —
but worth knowing this exists in case you cross-reference Winlink's own
FAQ directly and see a different number.

**Source:** Winlink Global Radio Email, "Tactical Addresses,"
`winlink.org/content/tactical_addresses` (updated April 27, 2023).
---

---

# APPENDIX D — Related Companion Documents

This manual doesn't stand alone — a few companion documents live
alongside it, each built for a different moment or a different reader.
None of them are part of this manual itself, and none of their content
is duplicated here — this appendix exists so you know they exist. All
three live in this repo's `companion-docs/` folder:
https://github.com/taco40sauce/kcgr-resource-feed/tree/main/companion-docs

**Global Variables Worksheet**
(`companion-docs/Resource-Status_Global_Variables_Worksheet.pdf`)
A one-page, fill-in-once worksheet for a new adopting club. Walks
through every value you'll substitute for KCGR's own throughout Parts
III and VI (your prefix, coverage area, account names, category lists,
and so on) — fill it out once before you start building, so you're
copying from one page instead of hunting through several sections
mid-build. See Part VI for where these values actually get used.

**Quick Start**
(`companion-docs/quick_start.pdf`)
A one-page, crisis-speed reference for field operators and validators —
sending a report, status codes, object types and specifiers, worked
examples. Built to be printed and kept on hand, not read start to
finish. See Part IV, 4.1 for the full report-filing walkthrough this
reference summarizes.

**Quick Start — Large Print**
(`companion-docs/quick_start_large_print.pdf`)
Same content as the Quick Start reference above, reformatted as a
two-page, double-sided document with larger fonts for anyone who finds
the standard edition difficult to read.

---







# [County/Town] Emergency Ground-Report Pipeline — Full Setup & Operations Manual

**Adapted from the KCGR (Kershaw County Ground Report) system, built by
the Kershaw County Amateur Radio Club (KC4RC), South Carolina.** Every 🔧
marks something specific to Kershaw County that you'll want to think
through for your own area, not just copy as-is. A one-page worksheet for
recording your own answers will be added once the rest of this manual is
in place.

**Please read this whole manual once, calmly, before you ever need it.**
Everything here is written so you *can* look something up mid-emergency —
but you'll move faster and with more confidence if the ideas are already
familiar before that day comes. A short Quick Start guide will sit at the
very front of the finished manual for exactly the moment when you don't
have time to read anything else — this fuller version is what backs it up.

*Each section below has two parts: short instructions you can act on
right away, and numbered notes at the end explaining the "why" behind
them. You don't need the notes to get moving. They're there for whenever
you have a quiet moment, or want to understand something well enough to
change it for your own town.*

---

# PART I — Before You Start

### A Word for the Skeptics in the Room

If you're reading this because your club already takes emergency
preparedness seriously, feel free to skip ahead to Section 1.1 — this
short passage isn't really for you. It's for the club member, spouse, or
town official looking over your shoulder right now, thinking "we've
never needed anything like this before."

Here's something worth passing along honestly: most clubs that take
preparedness seriously didn't start out that way. Often, it took getting
caught off guard once, and deciding out loud that they never wanted that
feeling again. One of our own members happened, purely by coincidence
while on vacation, to sit in on another town's ham radio club meeting.
What they noticed was a whole club, fully engaged in planning, drills,
and supplies — a real, visible change from what that same club used to
be. When asked why, the answer was simple: they'd been caught unprepared
once, and had decided never to let that happen again.

You don't have to wait for your own hard lesson to take this seriously.
That's really the quiet purpose of this whole manual — letting you
borrow someone else's hard-earned experience, instead of needing to earn
your own the same way.

---

## 1.1 The Thinking Behind This System

A handful of ideas shaped every decision in this system. Read through
these once before building anything — they'll save you from running into
the same problems we already worked through.

- **Build this for someone who's never been trained, not just for
  yourself.**[¹]
- **Expect to change things later — that's not a failure, that's the plan.**[²]
- **When two people report the same thing, that's a good sign, not a
  duplicate to clean up.**[³]
- **An old report doesn't get deleted. It just gets labeled as
  unconfirmed.**[⁴]
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

**People & authority**This is the KCGR project (Kershaw County Ground Report — ham radio emergency resource map). Read KCGR_CORE.md in full before doing anything else — it's the single current reference, replaces all prior versions, and is fully up to date as of tonight (8/13/2026 into 8/14). Repo: github.com/taco40sauce/kcgr-resource-feed.

Two things worth knowing before you start:

    §8 is the prioritized open-items list — start there for what's next. Items 1–3 (verifying the new APRS-IS-to-map cutover fires with zero manual intervention, proving reception via a genuinely independent iGate, and letting the poller run unattended for a while) are the live thread from tonight and can't be forced — they depend on real traffic and time passing, not more building.
    §7 has a process lesson you should actually follow, not just read: I don't have standing authorization to edit or build anything without an explicit go-ahead. A question like "Can I...?" or "Shall we...?" is not that — even when it sounds like agreement. When in doubt, give the diagnosis or the plan (and the exact old/new lines for anything small enough to self-serve) and wait to be told to proceed.

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
- [ ] A Tailscale (or equivalent mesh VPN) account under the
      organizational email, for remote operator access

**Decisions to make before building (don't skip — see Part III for how)**
- [ ] Your category list — what hazards actually matter in your area 🔧
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
but not exact?" The answer should never be "it gets thrown away silently."

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
skeleton first, get it running, and expect the details (categories,
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
labeled honestly as "unconfirmed" or "unclear," rather than thrown away.
A grey, imperfect pin on a map still tells someone "something's happening
here" — which is more than they had before, and doesn't waste the effort
someone put into sending it.

**[³] Two matching reports are worth more than one.**
Picture this: two different operators, who don't know each other, both
report the same bridge as washed out. Is that a duplicate to clean up, or
is it actually the most reassuring thing that could happen — real
confirmation from two independent sources? We treat it as the second one.
Every report still gets saved on its own, under the name of the person who
sent it — nothing gets merged or overwritten — but the map shows a count,
like "confirmed by 3 operators," so anyone looking at it can judge for
themselves how solid a report is, rather than the system quietly deciding
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
pretending it's still fresh, the map simply marks it "unconfirmed" after
a certain amount of time. The original information stays visible the
whole time — it's just honestly labeled as older. How long that takes
before something gets marked unconfirmed is different for every type of
report, and should be based on how fast things actually tend to change in
your area (see Part III for how to work that out for yourself).

**[⁵] Why a license alone is enough to trust a report.**
Any licensed ham radio operator's report gets posted automatically,
without needing a second person to confirm it first — and that's a
deliberate choice, not something we skipped by accident. A ham radio
license means the government has already verified who that person really
is and that they can be held accountable for what they transmit — the
same reason the U.S. Geological Survey trusts ordinary citizens' "I felt
an earthquake" reports without needing anyone to double-check them first.
A callsign works the same way here: it's already a form of ID.

This doesn't extend automatically to *every* possible source of
information, though, and that's worth being clear about, since it could
mean two different things:

- If a report comes in through a completely different system — say, a
  future version of this pipeline that also accepts reports over a
  citizens-band mesh network, or a web form open to the general public —
  that source doesn't carry the same built-in ID-checking a ham license
  does. That doesn't mean it gets held back and hidden, though — same as
  everywhere else in this system, it still goes on the map right away,
  just honestly labeled "unconfirmed," until either a second, independent
  report backs it up, or a licensed operator is able to check it out and
  vouch for it personally.
- On the other hand, if a *licensed ham* hears something secondhand —
  from a scanner, a neighbor, social media — and chooses to relay it as
  their own report, that's still coming in through the ham radio system,
  under their own callsign, and their license still vouches for them
  personally. It's on that operator to only relay what they're confident
  enough to put their own callsign behind — same as any other report they
  send.

In short: it's the *path the report came in on* that determines the
trust level, not the *original source* of what an operator personally
chose to pass along.

**[⁶] Only ever give a password or a key the smallest job it needs.**
Think of it like giving out house keys: you wouldn't hand someone a
master key just so they can water your plants — you'd give them a key
that only opens the side door. This system follows that same idea
everywhere. A login used to update the public map is only ever allowed to
update that one thing, not access everything else in the account it lives
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
and the shared file storage — so a future person can be handed the keys
cleanly, without needing your personal accounts at all. Write things down
assuming the person reading them later might be far less technical than
you are right now, not as technical as you'll be after building all of
this yourself.

One real wrinkle worth flagging honestly, not glossing over: a shared
club account is great for succession, but it does raise a practical
question once Winlink becomes part of this system — someone still has to
actually log in and check that shared account regularly, the same way you
might check your own personal one out of habit. That's not automatic just
because it's a shared account. Checking a Winlink account usually means
connecting to it directly (for example, over telnet), not glancing at a
regular inbox — so this needs its own clear answer: who checks it, and
how often, especially during an actual event. We don't have a clean
answer to that yet ourselves — it's flagged here on purpose as something
to work out together with your team when you get to that part of the
system, not something already solved.

**[⁸] A person clears old reports by hand — the system doesn't guess.**
There's no fully reliable way for the system to know on its own when a
situation is truly over — a shelter closing, a road reopening — versus
just quiet for a while. Rather than let a computer guess wrong and remove
a report that's still true, a real person checks and clears things out
after an event has settled down. Getting this wrong in the safer
direction (a report stays visible a little longer than it needs to) is
far better than getting it wrong in the other direction (a still-true
report disappears on its own). The corroboration count mentioned earlier
is a helpful clue for *where* to look when doing this cleanup — a report
that many people confirmed, but that's gone quiet for a while, is worth a
second look — but a person always makes the actual call.

**[⁹] Build a real relationship with your local EOC — not just a feed
going out.**
It's worth thinking about your local Emergency Operations Center as a
partner, not just an audience for your public map. One concrete way to do
this: encourage your operators to also send significant reports directly
to your local (or state) emergency management using the standard format
they already use for this — called an **ICS-213 General Message form**.
It's a simple, widely-recognized way of relaying a message during an
emergency, already familiar to most EOC and ARES/RACES people, so using
it (rather than a made-up format of your own) tends to be taken
seriously right away.

Doing this well can create a genuine two-way street: official
information the EOC has — that never would have come from a ham
operator on the ground — can end up getting added to your public map by
your Hub Operator, filling in gaps your own reports alone couldn't cover.

There's a real trade-off worth naming plainly, though: asking every
field operator to fill out a second, more formal message on top of their
quick radio report adds real effort, right when they're busiest. Two
reasonable ways to handle this, and it's worth picking one on purpose
rather than leaving it vague:
- Ask operators to send both, for reports they judge important enough —
  simple but adds workload to the person out in the field.
- Have your Hub Operator (or someone else in that role) periodically
  gather up the notable reports already coming in and relay *those* to
  the EOC as ICS-213 messages — keeps the field side simple and fast, at
  the cost of a little delay and one more task for whoever runs the hub.

Either can work. What matters most is deciding this on purpose, together
with your team, rather than leaving it to chance — see Part IV, section
4.3, for how this plays out during an actual activation.

**[¹⁰] Does your radio already have a sound card built in? Start there.**
The single most useful question to answer first is: **does your radio
already have its own built-in sound card?** Some newer radios (including
the one this system was originally built around) do — which means audio
and radio control both travel over one plain USB cable straight from the
radio to your computer, with nothing extra to buy or wire up.

Older or simpler radios usually don't have that built in, and need a
small separate box in between the radio and the computer to handle audio
and switch the radio to transmit — a "Signalink" is a well-known example
of this kind of box. It does the same job, just with an extra piece of
hardware and a bit more cabling.

Neither setup is better than the other for this system — you're not
missing out either way. You just need to know which one you have, since
the setup steps in Part II differ slightly depending on the answer. If
you're not sure, check your radio's manual for the words "USB audio" or
"built-in sound card" — that'll tell you which category you're in.

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
- [ ] A small always-on computer (a Raspberry Pi is what this system was
      built around — a credit-card-sized computer that sips very little
      power and is inexpensive)
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

**What "the pipeline" actually is, in plain terms:** a small set of
programs that work together to notice a new report coming in over the
radio, read what it says, save it, and automatically put it on your
public map — without anyone needing to do that by hand.

There are five small pieces, each with one simple job:

| Piece | Its one job |
|---|---|
| The **fetcher** | Logs into your APRS software and asks, "any new messages?" |
| The **reader** | Takes one message and figures out what it actually says |
| The **filing cabinet** | Saves each report so nothing gets lost |
| The **publisher** | Takes everything currently saved and updates the public map |
| The **conductor** | Runs the first four, in the right order, every time |

**Steps:**
1. Get the code onto your small computer. This system's code is kept on
   **GitHub** — a free website for storing and sharing code, a bit like
   a shared drive, except it also keeps a full history of every change
   ever made to it, which is genuinely useful when something needs to be
   undone or double-checked later. Create a free account there under
   your **club's shared email**, not a personal one (see Part I, note 7).
2. Install Python (the programming language all of this is written in)
   if it isn't already on your small computer.
3. Set up a **separate file just for your passwords and logins** — kept
   completely apart from the actual program files. This matters: it
   means your real password never accidentally ends up somewhere public,
   like the shared code repository.
4. **Test each piece by itself before connecting them.** Run the fetcher
   alone first, and confirm it can actually log in and pull messages.
   Then test the conductor, which runs everything together. Don't skip
   this — testing one piece at a time is exactly how a real, hard-to-spot
   problem[¹] got caught and fixed in the system this was built from.
5. Once the conductor runs cleanly by hand, set it up to run
   automatically and repeatedly, on its own, without you needing to sit
   there and type anything.[²] How often it checks is worth thinking
   about deliberately rather than just picking a number — see Note 2 🔧
6. Add a simple on/off switch, reachable from a web browser with a
   password, so you (or another trained operator) can turn the automatic
   checking on before an event and off afterward, from anywhere — not
   just from the small computer itself.[³]

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
   a pin will quietly show up unstyled, with no error or warning
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
weren't — nothing was actually calling them in sequence, so real reports
went out over the radio and simply never made it to the map, without any
error showing up anywhere. Testing one piece at a time, and then testing
the whole chain together deliberately, catches exactly this kind of gap.

**[²] Why "runs automatically" needs an on/off switch, not just "always
on."**
It might seem simpler to have this checking for new messages constantly,
all the time, forever. In practice, there's rarely a need for that
outside of an actual emergency — and having an explicit on/off switch
means it's only using your radio and internet connection when there's a
real reason to. This system defaults to **off**, and someone turns it on
deliberately when it's actually needed, then off again afterward.

Worth thinking about your checking interval the same deliberate way. It's
tempting to assume "more often is always better," but that's not
necessarily true — if your local APRS frequency tends to get busy or
crowded during a real event, reports may only be getting through the
shared airwaves occasionally in the first place, no matter how often your
system checks for them. Checking faster than real reports can actually
arrive doesn't gain you anything, and just uses more of your radio and
internet resources for no benefit. A good interval is one that matches
how busy your own local frequency realistically gets — worth a
conversation with other local operators who know that frequency well,
rather than guessing.

**[³] Why the on/off switch is a separate thing from the automatic
checking itself.**
These are set up as two independent pieces on purpose: the switch itself
should always be reachable, even when the automatic checking is turned
off — otherwise you'd have no way to turn it back on remotely. Keeping
them separate means one can be "always available" while the other is
"only running when needed."

**[⁴] Why exact spelling matters so much here.**
Computers don't understand meaning the way people do — they check
whether two pieces of text match *exactly*, character for character. To
a person, "Food-open" and "Food-Open" obviously mean the same thing. To
the map's styling rules, they're two completely different, unrelated
values — and a mismatch doesn't cause an error message, it just quietly
leaves that one pin unstyled, gray or invisible, with nothing telling you
why. This exact problem happened during real testing of this system, and
took real effort to track down precisely because nothing "broke" in an
obvious way. Worth double- and triple-checking every value matches
exactly, rather than assuming close-enough is good enough.

**[⁵] Why not just open the small computer directly to the internet
instead?**
It's technically possible to make a home computer reachable from the
internet directly, without a service like Tailscale, by adjusting some
router settings. This system deliberately avoids that. Doing it that way
means the whole open internet can attempt to reach your computer, not
just the people you've actually invited — every additional exposure like
that is a chance for something to go wrong that has nothing to do with
this project. A private networking service instead only allows in the
specific devices you've personally approved, over a secure, invitation-
only connection — the same "give it only the smallest access it needs"
idea from Part I, applied to your network instead of a password.

---

*Part III (Making It Yours) picks up next — your category list, field
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
   power in hard-hit rural or low-lying areas) can genuinely take weeks.
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

## 4.1 Training Operators

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
### REMOVAL-PANAL ACCESS TOKEN ON GITHUB for admin page report  
  Removal-panel access token — expires 8/14/2027. The admin page's 
report-removal tool depends on a GitHub access token that expires on this date. 
If it lapses, the toggle and status sections of this page keep 
working normally — *** only the removal tool breaks *** , and it fails with an 
*** authentication error *** rather than anything visible elsewhere on the page. 
If a removal attempt fails after this date, or if you're checking in proactively 
around this date: generate a new fine-grained token at 
github.com/settings/personal-access-tokens/new (repository access: kcgr-resource-feed only; 
permissions: Contents read-only, Actions read/write), 
then update GITHUB_PAT in ~/.kcgr_secrets/credentials.env on the Pi and r
estart the admin app. Contact the Hub Operator if you're not sure how to do this.

---

## 4.2 Pre-Event Activation Checklist

**What "activation" means here.** Right now, activation is a technical
step — turning your automated pipeline on. That's expected to change as
more of this system moves off local hardware.[²]

**Steps:**
1. Turn the automated pipeline on (see your Quick Command Reference
   appendix) and confirm it shows as running.
2. Do one test entry directly in your database, and confirm the
   matching pin appears correctly on the public map before relying on
   it for real reports.
3. Notify your data-entry operators and validators that KCGR is active
   — this is the step that actually puts people watching, regardless of
   what the pipeline itself is doing.
4. If your EOC, CERT, or a net (Skywarn or otherwise) is activating
   around the same event, coordinate timing so KCGR can record live
   field reports as they come in — active and ready before other
   channels start generating them, not scrambling to catch up
   afterward 🔧.
5. Start a fresh paper handoff log for this activation (see Appendix D).
6. If your county EM office has agreed to help promote the map
   publicly, let them know it's live 🔧.

---

## 4.3 During-Event Operations & Monitoring

**Every operator confirms their own report reached the map — within one
hour, every channel, no exceptions.**[³]

**Watch for reports that never make it in.** Only your own automated
channels (APRS, and Winlink once built) get checked by the pipeline
itself. Anything relayed over DMR, Meshtastic, Facebook, Skywarn, or any
other channel depends entirely on a person remembering to also put it in
your database. This is a validator's main job during an active
event — not just watching what's already on the map, but watching for
the gap.

**Handling a report that's clearly wrong.**[⁴]
1. Pull it using your removal tool.
2. Keep going — don't stop to fully investigate mid-event.
3. Note it (paper handoff log is fine) for a full review after the
   event.

**Shift changes.** Fill out the shift-end questions (Appendix D) before
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

## 4.4 Post-Event Wind-Down

**What wind-down means here.** Today, wind-down includes turning the
pipeline off — the same Pi-hosted toggle covered in note 2. The plan is
for that step to disappear entirely once the pipeline moves off the Pi
onto always-on infrastructure; at that point there's nothing to switch
off, and wind-down becomes purely about people and data, not
infrastructure. Update step 1 below once that migration is real.

**Steps:**
1. If your pipeline is still Pi-hosted with an on/off toggle, turn it
   off once you're confident the event is truly over — not
   automatically, not on a timer (Part I, note 8: a person makes this
   call by hand). Once it's running on always-on infrastructure
   instead, skip this step — there's nothing to turn off.
2. Fill out the post-event questions (Appendix D) while the event is
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
think to check whether *other* reports are missing. Teaching them
separately, even briefly, makes sure both muscles actually get built.

**[²] Why activation is currently a toggle, but described as changing.**
Today, your automated pipeline defaults to off (Part II, note 2) and
someone has to deliberately turn it on. That was a deliberate choice
when everything ran on a single Pi at home — no reason to poll for
reports around the clock if there's no active need. Once more of this
system moves to always-available infrastructure (not tied to your home
power or internet), that reasoning goes away: there's no real cost to
leaving it running continuously, and doing so means anyone reporting in
already "activates" the system just by sending a report — the same way
a Skywarn net-control operator activates a net simply by starting it,
not by requesting permission first. When that shift happens, this
checklist's step 1 becomes unnecessary, and "activation" becomes purely
about notifying people, not touching any switch. Update this section
when that migration is complete — don't leave stale toggle instructions
here once they no longer apply.

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
location or wrong code that a broad scan would miss entirely. One hour
was chosen as tight enough to catch a genuinely dropped report
same-shift, before an operator moves on and forgets to circle back.

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

*Part V (Keeping It Alive) picks up next — troubleshooting/recovery,
succession planning, third-party permissions log, and an append-only
changelog of lessons learned.*

---

# APPENDIX A — Quick Command Reference (Start to Finish)

*(Note: this will move to the very end of the manual once Part V is
written. It's placed here for now so it isn't lost in the meantime.)*

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

---

### 3. Check whether it's actually running

```
sudo systemctl status kcgr-pipeline
```
Look for `Active: active (running)` in green.

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

*End of Appendix B.*

---
name: charter
description: Interview the project owner to fill in the authority tiers — what is settled, what is arguable, and what the project's rock-solid concepts are. Run once at the start of a project, before writing code.
---

# Charter the project

Fill `docs/tiers.md` by **interview**. Do not draft a tier list and present it as finished:
a list the owner did not build is a list the owner has not agreed to, and it will quietly
become a way to overrule them later.

Run this once, early, before there is code to be attached to.

## How to run it

**Interview, in rounds.** Ask a few questions, write down the answers, come back with what
the answers imply. Two or three short rounds beat one long questionnaire, because the
second round is where the interesting corrections happen.

**Ask about consequences, not categories.** "Is the schema Tier 1?" is unanswerable by
someone who does not implement. "If a future version had to change the database layout to
make search fast, and no user could tell the difference, is that my call or yours?" is
answerable by anyone.

**Write the answers in the owner's own words.** Quote them in the registry's notes. A
quoted sentence settles an argument two months from now; a paraphrase reopens it.

## What to establish

**1 · The rock-solid concepts.** Three to six things the project would not be itself
without. Ask directly: *what could I not change, no matter how much easier it made the
code?* Push for few — if the list runs past six it has stopped being a list of promises.

**2 · The registry rows.** For each area of the system, what is the **promise** (the
owner's) and what is the **means** (the assistant's). Work through: the core guarantees;
data formats and on-disk representation; identity and versioning; storage and schema;
error recovery; configuration and vocabulary; the interface; engineering practice;
dependencies. Adapt the list to the project — an area with nothing at stake needs no row.

**3 · The direction of pushback.** Ask where the owner *wants* to be argued with, and say
plainly that the tiers will be read as an instruction to argue there and not elsewhere.
Most owners are strongest on the architecture and weakest on implementation detail; the
registry should point the argument at the second.

**4 · The reverse direction.** Ask whether they want the high-level concepts pressed on
for practicality — will this be too slow, will it survive contact with the real system —
and on what terms. If yes, agree explicitly that such a review **surfaces findings with
evidence and changes nothing**. Good designs are not to be altered by a review that was
only meant to test them.

**5 · The absolutes.** Ask how strongly to read "must" and "never" in what they have
already written, and agree that these get audited early rather than encoded silently. See
`.claude/skills/audit-absolutes`.

## The rules this interview establishes

Write these into `docs/tiers.md` unchanged — they are what makes the rest safe:

- Unassigned defaults to Tier 1.
- The assistant may only ever **propose** a tier, never assign one.
- A mechanism that turns out to have a **visible consequence** becomes the owner's again.
- The lower level serves the higher level; where they conflict, the lower-level rule
  yields.
- A tier that moved without a row changing did not move.

## Afterwards

Date the registry and say who set it. Re-run the interview when the project reaches a
stage the original answers did not anticipate — a first interface, a first release — and
add rows rather than rewriting history. Note what moved and why.

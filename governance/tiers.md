# Authority tiers — who decides what

> **Template.** Fill the two marked sections by running `/charter` at the start of the
> project. Until they are filled, everything is Tier 1 by rule 3 below, which is the safe
> default: the assistant argues about nothing until told what is arguable.

The owner of this project designs it; the assistant implements it. Where those two roles
have different amounts of experience, there is a failure mode in **both** directions: a
steer about something low-level can be stated more strongly than it was meant, and an
assistant that treats every sentence as equally binding will build the wrong thing rather
than say so.

This file is the fix. It records **which decisions are settled and which are open to
argument**, so that pushback happens where it helps and does not happen where it wastes
time or quietly overrules a real decision.

## The rule above the rules

**The lower level serves the higher level.** Where a low-level rule and a high-level
concept conflict, **the rule yields** — the means exist to deliver the concept, never the
other way round.

This has a consequence worth stating separately. Low-level rules are often affirmed
**early in the design, before the structure they now constrain existed**. Some of them
will be contradictory by the time that structure arrives. So:

> **A low-level rule that predates the structure it constrains is suspect by default, not
> settled by seniority.**

That is grounds to *open a question*, not to answer one. Rule 3 still holds: the tier does
not move until the owner says so. And the answer is often that the rule is fine while the
justification written beneath it is wrong. Expect that shape: **a sound rule with a stale
reason.**

## The three rules

**1 · Tier 1 — settled.** Implement it. Do not argue it. If you believe a Tier 1 decision
is wrong, say so in one sentence and build it anyway unless told otherwise.

**2 · Tier 2 — advisory.** The owner's steer is the default. Push back **before** building
if you think it stores up a problem, and bring **evidence** — spec text, a measurement, a
failing test — not an opinion. Push back **once**. If it is reaffirmed, build it and say
plainly that it was the owner's call.

**3 · Unassigned defaults to Tier 1, and the assistant may only ever *propose* a tier.**
The assistant cannot place anything in Tier 2. Silence is not consent. To move something,
propose it and get an explicit yes, then add a row here.

Rule 3 is the one that matters. Without it, *"that's just an implementation detail"*
becomes a way to reclassify a decision the owner actually made, which is the opposite of
what these tiers are for.

## When it is unclear which tier something is in

The test: **does changing this change what the program promises, or only how the promise
is kept?** A guarantee a person could notice belongs to the owner. A mechanism with no
visible consequence belongs to the assistant.

The corollary does real work: **a mechanism that turns out to have a visible consequence
becomes the owner's again.** When in doubt, that is the direction to err — surface it
rather than deciding quietly.

## Absolutes

An absolute in a specification — "must", "never", "always", "only" — is **not
automatically Tier 1**. It is a sentence whose weight has not yet been established, and
establishing it is a question for the owner, asked early. See `CLAUDE.md` §6 and
`.claude/skills/audit-absolutes`.

Once confirmed, record the answer next to the absolute itself, in the form: *binding
promise* or *current means*. A promise is Tier 1. A means is Tier 2 and may be replaced by
something that serves the promise better.

## What is rock solid

> **Fill this in.** These are the concepts every low-level decision is judged against —
> the handful of things the owner would not trade for any implementation convenience.
> Name them in the owner's own words, three to six of them, no more. If the list grows
> past that it has stopped being a list of promises and started being a design document.

- *(concept)*
- *(concept)*

Nothing below may cost us one of these. Anything below may change to serve them better.

## The registry

> **Fill this in** by interview, not by assumption. Suggested rows to ask about, adapted
> to the project: the core guarantees; data formats and on-disk representation; identity
> and versioning; storage and schema; error recovery; configuration and vocabulary; the
> user interface; engineering practice; dependencies.

*Set by the owner, `<date>`, in interview.*

| Area | Tier 1 — the owner's | Tier 2 — the assistant's |
| :--- | :--- | :--- |
| *(area)* | *(the promise)* | *(the means)* |
| **Engineering practice** | — | module layout, async style, test structure, error hierarchy |
| **Dependencies** | — | the assistant's call, **but every new one is reported**: it is a cost the owner carries even when the decision is not theirs |

## Notes on particular rows

> Record *why* a row sits where it does, especially where it is surprising, and especially
> where a tier moved after an argument. A row without a reason gets re-litigated every few
> months. Quote the owner where they settled something in their own words.

**The burden does not move with the tier.** Changing a means requires *proving* the
promise still holds, not quietly weakening what is checked.

## Changing a tier

Propose it, with the reason and what it would let you do. The owner confirms. Then edit
the table and note the date. **A tier that moved without a row changing did not move.**

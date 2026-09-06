---
name: stress
description: Press on a high-level design concept for practicality — will it be too slow, will it break at scale, will it survive contact with the real system. Reports findings with evidence; never edits design or code. Use occasionally, not on every change.
---

# Pressing on a design that is not up for debate

`docs/tiers.md` puts the high-level concepts beyond argument, and that is right — they are
what everything else serves. But "not up for argument" is not the same as "guaranteed to be
practical", and the gap between them is where a project discovers late that something it
decided early does not scale.

This skill is the narrow, safe way to look into that gap.

## The constraint that comes first

> **By no means are good designs to be altered.**

So:

- **This skill reports. It never edits.** Not the design, not `CLAUDE.md`, not code, not
  config. The output is a finding on the screen. Acting on one is a separate decision, made
  by the owner, in a separate session.
- **Reporting nothing is a normal and good result.** Most passes should end with "no
  finding". A pass that manufactures a concern to look useful has done harm.
- **The bar is demonstration, not suspicion.** A finding needs a measurement, a working
  spike, or a specific failure scenario with concrete inputs. *"This feels like it might be
  slow"* is not a finding — discard it rather than writing it down.

## The three verdicts

Every finding ends as exactly one of these. The middle one matters most.

| Verdict | Meaning | What you do |
| :--- | :--- | :--- |
| **`MEASURABLE NOW`** | Settleable today with a benchmark or a throwaway spike. | Measure it. Report the number, not the worry. |
| **`BUILD IT AND FIND OUT`** | A real unknown only the built thing can answer. | **Say so and stop.** Do not design around it, do not hedge the architecture, do not propose a mitigation for a problem nobody has yet. |
| **`ALREADY DECIDED`** | The design considered this and says so. | Cite the section and close it. |

`BUILD IT AND FIND OUT` exists to give you permission to stop. An unknown that has been
named is not a problem that needs solving.

## The procedure

1. **Take one concept.** Not the whole design — one claim, named, with its section.

2. **Find where it would break, not where it works.** The middle of the range tells you
   nothing. Ask: at what size, count, or depth does this stop being reasonable? Go straight
   there.

3. **Measure at that point.** Synthesise the data if it does not exist. Reuse the project's
   own fixtures rather than inventing a harness.

4. **Assign a verdict**, and for anything not `ALREADY DECIDED`, **name what would change
   your mind** — the specific measurement or event that would settle it. A finding without
   that is an opinion wearing a number.

5. **Report. Change nothing.**

## Two failure modes to avoid

**Manufacturing work.** Finding nothing feels like a wasted pass. It is not. "We checked
this and it was fine, here is the number" is itself valuable, and a false alarm costs the
owner real time on a design that was already sound.

**Solving it.** Even when a finding is real and serious, this skill stops at the report. A
concern surfaced is the owner's to weigh against things you cannot see — how much the
concept matters to them, what they plan next, what they are willing to live with. Hand them
the number, not the redesign.

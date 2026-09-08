---
name: focus
description: Distil the large design documents into a one-screen "what to do next" note and a decisions queue ordered by when each call is forced. Run when re-orienting, or after the plan has moved.
---

# A short read that says what to do next

A project accumulates a big architecture document and a big plan. Both are right to be
big. Neither answers the question you actually have on a Monday morning: *what do I work on
now, and what is stopping me.* This skill produces and maintains two small artifacts that
do, derived from the large ones and never replacing them.

## The two artifacts

**`NEXT.md` at the repo root — the worktop note.** One screen. Three parts:

1. **Where the build is** — three or four bullets, current state only.
2. **The next moves, in order** — the next handful of concrete steps, smallest first.
   If this list does not fit on the screen it is too long, and that means you are not
   focusing yet — cut it to what genuinely comes next.
3. **Blocking decisions right now** — the two to five open questions actually in the way
   of the next moves, each one line, pointing at the queue for detail.

It opens by saying what it is: a worktop note, **not a source of truth**, derived from the
plan and the design doc, to be checked against them. Without that line it becomes a fourth
document that quietly goes stale and then misleads.

**`notes/decisions-queue.md` — the decision backlog.** Every open question from the design
document and the plan, filtered to *what the next few milestones actually force*, and
**grouped by when the build needs the answer** — decide now / decide during the next
milestone / decide for the one after / can wait. Not grouped by importance. That ordering
is the entire point: the big documents already rank things by how much they matter, and
that is exactly the ranking that does not tell you what to settle this week.

For each item: the question, the options in a clause or two, and the leading answer where
the documents already lean one way.

## How

1. Find the two inputs: the architecture / source-of-truth document, and the plan /
   roadmap. Read the plan's sequencing section and the design doc's open-questions section
   in full; skim the rest.
2. Work out the next three-to-five concrete moves from the plan's own order — not what is
   most interesting, what is next.
3. Pull every open question from both documents. Drop the ones that do not touch the next
   few milestones. Sort the rest by the milestone that forces them.
4. Write `notes/decisions-queue.md`, then write `NEXT.md` as the short view over it.
5. Add a pointer from `CLAUDE.md` so the next session finds them.

## Keeping them honest

- **A settled decision lands in the real document first**, then gets struck from the
  queue. The queue is never where a decision is recorded — only where it waits.
- **Refresh when the plan moves.** A milestone completed, a decision made, a step
  resequenced: update both artifacts in the same change, the way `drift` expects a doc
  change to ripple.
- If `NEXT.md` and the plan disagree, the plan wins and `NEXT.md` is stale — fix it, do
  not reason from it.

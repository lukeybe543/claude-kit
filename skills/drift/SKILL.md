---
name: drift
description: Find claims in the project's documents that the code, or a recent design change, has quietly made false. Reports; does not edit unless asked.
---

# Finding what the docs still claim and the project no longer does

This is not a proofreading pass. Look for claims that were **true when written** and were
quietly invalidated — the failure mode where a section is rewritten around a new idea while
other sections go on arguing from the old one.

## How

1. `git diff HEAD~5..HEAD --stat`, or the range the user names — what actually changed.
2. For each changed area, ask what the documents *assert* about it, and check the assertion
   rather than the wording. **Grep for the vocabulary of the old idea, not the new one.**
3. Check the direction that gets missed: a **doc-only** change can invalidate another
   **doc**. Renaming a concept in one section does not update another section's use of it.

## Where drift concentrates

- **Cross-references** — a section number meant one thing before renumbering and another
  after.
- **Counts** — "five core sections", "four test layers", "complete but for…".
- **Superseded framings** — the commonest and the most expensive.
- **Status claims** — build checklists, "what exists now" sections, `DRAFT` markers.
- **Fossils** — a surviving half-sentence whose subject was deleted. Grep the glossary for
  terms the body no longer explains.

## Report

Each finding as `file:line` — the claim, what made it false, and the smallest correct
replacement. Rank by how load-bearing the claim is: a wrong invariant outranks a stale
count.

Say "no drift found" plainly if that is the answer. Do not manufacture findings, and do not
edit anything unless asked.

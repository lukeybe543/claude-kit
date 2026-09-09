---
name: flags
description: Process the inline review marks the owner left in a document — WRONG / VAGUE / STALE / REORG — acting on each, removing the mark, and reporting mark by mark. The owner marks; this skill resolves.
---

# Resolving the owner's review marks

The owner reviews a large document by prepending a **tag word** to a block that
is not right, rather than pasting the block into chat. This skill is the other
half: it walks the marks, acts on each, and clears them.

The division of labour matters. The owner decides *what* is wrong and how
severely; this skill decides *how* to fix it, within the limits each mark sets.
It is not a proofreading pass — untouched text stays untouched.

## The marks

A mark sits on its own line, directly above the block it applies to. Above a
heading it flags the whole section; above a paragraph, just that block. Any text
after the mark is a note from the owner. Marks stack (`WRONG: REORG:`).

| Mark | Means | What to do |
| --- | --- | --- |
| `WRONG:` | Contradicts reality, the code, or another part of the document. | Correct it. If the correction is itself a decision the owner has not made, re-flag with a note and stop — do not decide it. |
| `VAGUE:` | Not wrong, but imprecise, ambiguous or under-specified. | Tighten the wording so it can only be read one way. Ask only if the intent is genuinely unrecoverable. |
| `STALE:` | Was true when written, now outdated, could mislead. | Reconcile against `plan.md`, the code, `docs/decisions.md`, or a later decision. State what changed. |
| `REORG:` | The content may be fine, but it is the wrong shape, in the wrong place, or at the wrong granularity. | Propose a reorganisation and wait for the owner. Do not restructure unilaterally — `REORG` is a discussion, not an instruction. |

## How to run it

1. `grep -n` the file for the four tokens. Read each marked block *and* enough
   around it to understand what the block is doing.
2. Work the marks in document order. For each:
   - Make the change the mark licenses, and no more. A `VAGUE:` mark is not
     permission to rewrite the paragraph — only to make it precise.
   - If acting on the mark would touch a `firm` decision in `docs/decisions.md`,
     stop and surface it rather than editing around it.
   - Remove the mark line once its issue is resolved.
   - A mark you cannot resolve without a decision stays, with a one-line note
     appended saying what is needed.
3. Report mark by mark: the location, what the mark said, what you did or why
   you could not. Rank nothing — the owner set the severity.

## Afterwards

- If a resolved mark changed a claim other sections rely on, say so — the same
  ripple `drift` looks for.
- If a `STALE:` mark turned out to reflect a real decision that was never
  recorded, add it to `docs/decisions.md` rather than only fixing the sentence.
- Leave the file with no marks except the ones you explicitly handed back.

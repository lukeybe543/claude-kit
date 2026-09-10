---
name: bands
description: Build a published review page for the flagged and un-Banded rows of docs/decisions.md, let the owner work through it, then apply the result — flag concerns captured, rows reworded, Bands set — back to the register. For the Band re-approval the charter's Band lifecycle calls for.
---

# The Band re-approval workbench

`docs/decisions.md` accumulates two kinds of unfinished row:

- **Flagged** — the owner put a `Flagged:` reason on it. Per the charter it is
  raised on sight, and a substantive change clears its Band to `unset`.
- **Un-Banded** — no owner-set Band, only a Claude-proposed one (or none). Also
  `unset`: not binding, blocks the coding gate.

Working through these in the `docs/decisions.md` table itself is miserable —
a wide markdown table in a preview pane. This skill puts them on a published
Artifact page instead: one card per row, the owner fills a box per row, the
page saves as they go, and this skill reads it back and applies it.

**The rule that shapes it:** a `Flagged:` reason usually means *"I need to think
about this"*, not *"tidy the wording"*. So the page shows the flag verbatim and
asks for the concern behind it — **it proposes no rewording**. The fix is drafted
only in phase 2, once the real concern is in hand.

## Phase 1 — build and publish the workbench

1. **Parse `docs/decisions.md`.** For every row, read `ID`, `Decision`, `Alt`,
   `Band`, `Flag`, `Domain`, `Status`. Sort into three lists:
   - `flagged` — `Flag` holds an **open** `Flagged:` (ignore ones marked
     `Resolved`/`Withdrawn`). Fields: `id`, `statement` (the `Decision` text),
     `flag` (the reason, with the `Flagged:` prefix stripped),
     `meta` (`"<alt> · <domain>"`).
   - `toBand` — `Band` is empty or `unset` **and** no open flag. Fields: `id`,
     `statement`, `meta`, and an optional one-line `note` where the row also
     needs a small wording fix (a renamed term, a superseded reference).
   - `done` — optional; rows resolved earlier in this same review, shown for
     reference. `id`, `statement` (a short summary of what was settled).
2. **Fill the template.** Copy `workbench.template.html` (next to this file) and
   replace three markers:
   - `__TITLE__` — `"<Project> Decision Bands"` or similar (2–4 words).
   - `__HEADLINE__` — a plain sentence, e.g. `"Working through the flagged decisions"`.
   - the `{"flagged":[],"toBand":[],"done":[]}` literal on the `__INJECT_DECISIONS__`
     line — the real JSON. Keep the exact shape; escape strings properly.
   Change nothing else in the template.
3. **Publish** with the `Artifact` tool: `capabilities: {"db": {}}`, a `favicon`,
   a one-line `description`. Give the owner the URL and a one-paragraph how-it-works
   (fill the concern box, pick a disposition, set Bands below; notes save
   automatically; tell Claude when done). Say nothing about a deadline — the owner
   works through it at their own pace, across sessions if needed.

If the owner later says the page shows "not saving", the `db` capability did not
connect: check `Artifact action:"read_db" db_op:"list" collection:"review"`
resolves, and republish if the capability was dropped.

## Phase 2 — read it back and apply

Triggered when the owner says they are done (or "apply the bands review").

1. **Read the input:** `Artifact action:"read_db" db_op:"list" collection:"review"`.
   Each doc id is a decision id; body is `{concern, disposition, band}`.
2. **Act per disposition**, one row at a time, in `docs/decisions.md`:
   - `resolve` — now draft the reworded `Decision` cell, using the **captured
     concern** as the brief. Show the owner old → new; on their yes, apply it.
     Per the charter's Band lifecycle the reword **clears the Band to `unset`
     and archives the `Flag`** (replace the `Flagged:` text with a dated
     `Resolved:` note, or blank it and log it in `NEXT.md`).
   - `topic` — leave the row flagged. Append to the `Flag`: which design topic
     it belongs to. Add that topic to `NEXT.md` / the decisions queue.
   - `withdraw` — the owner decided the flag was a non-issue. Remove the
     `Flagged:` text; the row still needs a Band (next step).
   - `unsure` / empty — leave the row untouched; it stays open. Report it.
3. **Set Bands.** Apply each `toBand` row's Band from the page. For rows
   reworded or flag-withdrawn in step 2, propose a Band each (guided by `Alt`,
   `Prov`, `Era` — see the charter) as a single table, and get the owner's
   confirmation as **one batch**, the way the Band lifecycle prescribes.
4. **Reconcile.** Run `drift` (or its checks) so every reworded row still
   agrees with its source section in the design docs. Update `NEXT.md` and any
   review tracker. State which milestones the coding gate now clears.
5. Leave `docs/decisions.md` with open flags only on rows the owner sent to a
   design topic or left `unsure`.

## Notes

- The workbench is a review aid, not a source of truth — `docs/decisions.md` is.
  Never treat a `review` doc as the decision; it is the owner's note about it.
- One workbench per review. Re-running phase 1 republishes to the same URL and
  keeps the saved notes (same `review` collection). Publishing from a different
  conversation needs the `url` passed, or it forks a new artifact.
- The `review` collection is scratch. Once phase 2 is applied and committed, the
  page can be left as a record or the docs deleted with `db_op:"delete"`.

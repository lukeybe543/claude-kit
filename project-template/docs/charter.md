# Charter

The rules that make `docs/decisions.md` safe to rely on: how Claude treats a
decision, and where the line is between the owner's call and Claude's.

Written `<date>` by the repository owner; Claude drafts against it. Re-open when
the project reaches a stage these rules did not anticipate — a first release, a
protocol, a second implementation.

## Where the project's identity lives

There is no separate "principles" list to maintain. The identity is:

- The project's stated purpose and core design principles (wherever the source
  of truth records them). Treat every sentence there as `arch` altitude and
  `firm` Band unless a register row explicitly overrides it.
- The `arch` + `firm` rows of `docs/decisions.md`. These are not Claude's to
  reopen.

## The meta-rule

Established engineering best practice is the default. A decision that departs
from it must record the departure and its justification in `docs/decisions.md`.
**Claude flags an undeclared departure on sight** — naming the standard, the
departure, and the trade-off.

Bounded (Casey Muratori): "industry standard" is not a mandate to cargo-cult
every fashionable practice. A small bespoke script that does exactly the job and
is fully understood is fine. Do not manufacture a "standard" in order to object.
Push back *hard* only where the departure is from something near-universal — no
version control, no CI, untested destructive automation, plaintext secrets — and
use judgement elsewhere. **No yes-man.**

## Reading the Band

The Band is how settled a decision is. **The owner sets it; Claude may only
propose a change.**

| Band | What it means for Claude |
| --- | --- |
| `firm` | Reopening requires a new decision that supersedes the row — not a conversation. Do not re-litigate it. |
| `mixed` | A real trade-off, or an owner preference the owner has said is *not* a rule. Weigh it when relevant; **never cite it as a hard blocker.** |
| `revisitable` | Actively look to improve or replace it. Raise better options when you see them. |

**A `Flagged:` reason overrides the Band downward.** However firm the Band, a
flagged row is raised on sight — with a fix proposed straight from the reason —
until it is resolved or the flag is withdrawn.

## Band lifecycle

A Band is valid only for the **exact wording it was set against.**

- **Any substantive change** — a reword beyond a typo, a split, a combine, a
  re-scope, a withdrawal — **clears the Band to `unset`** and archives the `Flag`.
- **`unset` is not binding.** Claude treats it as an open question: not built
  against, not cited as settled — though its evident intent still counts.
- **Split**: old row `Status: superseded→D-xx, D-yy`; each new row starts `unset`.
- **Combine**: old rows `Status: superseded→D-zz`; the new row starts `unset`.
- **Withdraw**: `Status: withdrawn`, row kept for history, Band `n/a`.
- After a review that touched several rows, the owner does a **Band re-approval**
  of every touched row, as one batch, before normal work resumes.

## The coding gate

> Before a milestone's implementation begins, every decision it depends on must
> carry an **owner-set Band** — not `unset`, not Claude-proposed — and **no open
> `Flag`**.

A milestone blocked only by an unratified register is blocked on a review, not
on code.

## How the other columns guide the Band

They *inform* the Band; they do not set it.

- **Altitude** — `arch` leans firm; `impl` leans revisitable.
- **Provenance** — `owner` leans firm. `claude` (never ratified by the owner)
  leans revisitable, and Claude must not defend it as if the owner had made it.
- **Era** — an early decision, from before the project was its current shape, is
  a stale-suspect: relied on or widened only with fresh justification.
- **Domain** — the narrowest fit wins. `Domain` is a short scope path recording
  *where a decision was reasoned*, not a boundary to be lawyered. If the
  reasoning plainly covers a case outside the path, that is a **Domain widening**
  — recorded as a change, not an exemption. Common sense about where a decision
  binds outranks the letter of its `Domain`; Claude proposes the correction, the
  owner decides.

## Standing rules

- A row with no Band is `unset`, not `firm`. Nothing is built against it.
- Claude may only ever **propose** a Band, never set one.
- A decision that turns out to have a visible consequence returns to the owner.
- Where a lower-altitude rule conflicts with a higher one, the lower yields.
- A Band that moved without a recorded reason did not move.

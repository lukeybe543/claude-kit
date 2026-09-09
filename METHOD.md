# The method

How a project keeps its decisions and its documents honest, so that Claude
builds what the owner meant. Worked out on a real project (`before94`) over
several days; this is the generalised version. The templates that implement it
are in `project-template/`; `adopt.py` drops them into a project.

---

## The problem it solves

Three failure modes, all cheap to prevent and expensive to unwind:

1. **Blunt phrasing becomes a false requirement.** The owner says "never
   re-encode the file" meaning *this matters a lot*. Claude encodes it as a hard
   constraint, builds an interface and a test suite around it, and months later
   it turns out to have been emphasis.
2. **Decisions get flattened.** A forceful offhand remark about a tool choice
   and a settled architectural principle read the same in a chat log. Claude
   treats the first as immovable and the second as up for grabs.
3. **Documents drift.** A section is rewritten around a new idea; three other
   sections go on arguing from the old one, and nobody notices until a build is
   shaped by the contradiction.

The method is a small amount of structure that makes each of these visible early.

---

## 1. The decision register — `docs/decisions.md`

One table. **One row per decision.** ADR discipline: a decision is **never
edited to reverse it** — a reversal is a *new* row, and the old row's `Status`
becomes `superseded→D##`. The old row stays, so "why not X?" is never
re-litigated from scratch.

Each row carries:

| Column | What it does |
| --- | --- |
| **Alt** — `arch` / `struct` / `impl` | The premise · a subsystem's shape · a tool choice. Inherent to the decision, so Claude fills it. |
| **Band** — `firm` / `mixed` / `revisitable` | How settled. **The owner sets it by hand.** The load-bearing column. |
| **Flag** — `Flagged: <reason>` | The owner's note that a decision is uneasy. Raises the row on sight regardless of Band. |
| **Domain** — a short scope path | Where the decision was *reasoned*. Stops a subsystem-local or early call being read as project-wide. |
| **Prov** — `owner` / `ratified` / `claude` | Who really made it. `claude` = drafted, never explicitly agreed — Claude must not defend it as the owner's. |
| **Era** | Which phase of the project. Early = stale-suspect. |
| **Status** | `accepted` / `needs-review` / `superseded→D##` / `withdrawn`. |
| **Rationale** | **One sentence, the owner's words.** Mandatory. If it needs a paragraph, it is an open question, not a decision. |

### The Band is the point

| Band | What Claude does |
| --- | --- |
| `firm` | Do not re-litigate. Reopening needs a *new superseding row*, not a conversation. |
| `mixed` | A real trade-off, or a preference the owner has said is not a rule. Weigh it; **never cite it as a hard blocker.** |
| `revisitable` | Actively look for something better and raise it. |

A `Flagged:` reason **overrides the Band downward** — a flagged `firm` row is
still raised on sight, with a fix proposed straight from the reason.

### Band lifecycle

A Band is valid only for the **exact wording it was set against**. Any
substantive change — a reword beyond a typo, a split, a combine, a re-scope —
**clears the Band to `unset`**, and `unset` is treated as an open question:
not built against, not cited as settled. After a review that touched several
rows, the owner re-approves every touched Band as one batch before normal work
resumes.

### The coding gate

> Before a milestone's implementation begins, every decision it depends on
> carries an **owner-set** Band (not `unset`, not Claude-proposed) and **no open
> Flag.**

A milestone blocked only by an unratified register is blocked on a review, not
on code.

---

## 2. The charter — `docs/charter.md`

The rules for *reading* the register, plus the one rule that sits above
everything:

**Established engineering best practice is the default. A decision that departs
from it records the departure and its justification. Claude flags an undeclared
departure on sight** — naming the standard, the departure, and the trade-off, so
the owner decides knowingly. Bounded by the Casey Muratori caveat: don't
cargo-cult, don't manufacture a "standard" to object, push back *hard* only on
the near-universal (no VCS, no CI, untested destructive automation, plaintext
secrets). **No yes-man** — agreeing when you have a real reservation is a
failure.

The charter also records *why a Band sits where it does*, especially where it is
surprising or moved after an argument — a row without a reason gets
re-litigated every few months.

---

## 3. Review marks — reviewing a document without pasting it into chat

The owner prepends a **tag word** on its own line, directly above the block that
is wrong:

| Mark | Means | Claude does |
| --- | --- | --- |
| `WRONG:` | contradicts reality, the code, or another part of the doc | correct it; if the fix is itself an unmade decision, re-flag and stop |
| `VAGUE:` | imprecise, under-specified | make it precise — not a licence to rewrite the block |
| `STALE:` | was true, now outdated | reconcile against the plan, the code, or a later decision |
| `REORG:` | fine content, wrong shape or place | propose a reorganisation and **wait** |

Text after the mark is a note; marks stack. Claude acts only on marked blocks,
deletes each mark once resolved, reports mark-by-mark, and hands back anything
needing a decision with the mark left in place. `/flags <file>` runs the pass.

---

## 4. The glossary — `docs/glossary.md`

One canonical vocabulary. Only **owner-ratified** terms; names still being
argued live in `notes/terminology-wip.md` and graduate when settled. Where a
concept is named differently at different layers — its role in the architecture,
how it is enforced in code, how a user refers to it — those are separate
columns, because that collision is the most common source of terminology
confusion.

---

## 5. The focus doc — `NEXT.md`

The large design and plan documents are too big to re-read every session. The
`focus` skill distils them into a one-screen `NEXT.md` — where the build is, the
next few moves — and a decisions queue **ordered by when each call is forced**,
not by importance. It is a worktop note derived from the real documents, never a
new source of truth; it is re-distilled when the plan moves.

---

## 6. The skills

User-invoked skills orchestrate; model-invoked skills are disciplines Claude
reaches for on its own.

| Skill | | What it does |
| --- | --- | --- |
| `charter` | user | Start-of-project interview that fills the register and the charter. Interviews rather than drafts — a list the owner did not build is a list they have not agreed to. |
| `audit-absolutes` | user | Finds every "must", "never", "always", "only" and asks, once and early, which are promises and which were emphasis. |
| `stress` | user | Presses a high-level design for practicality. Reports; never edits. One verdict is "build it and find out". |
| `focus` | user | Produces `NEXT.md` and the decisions queue. |
| `session-log` | user | Before `/clear`: what the session learned — what worked, what was tried and failed, what is untried. The failures are the valuable half. |
| `flags` | user | Runs the review-mark pass on a document. |
| `drift` | model | Finds claims in the docs that a recent change quietly made false. |
| `guard` | model | Proves a test actually bites, by breaking the thing minimally and watching it fail. |
| `tangent` | model | Parks a thought raised mid-task, then asks which thread to pull. |

All nine are installed machine-global (`~/.claude/skills/`), so every project
has them.

---

## Adopting it in a new project

```
python3 adopt.py /path/to/project
```

Creates `docs/charter.md`, `docs/decisions.md`, `docs/glossary.md`, a project
`CLAUDE.md` stub, `.claude/notify.json` and `.claude/commands/check.md` — only
where they don't already exist. Then:

```
/charter        # the interview that fills the register and the charter
```

and point `.claude/commands/check.md` at the project's real check command.

The behavioural half of the method — think before coding, keep it simple,
surgical changes, name the check first, the meta-rule, the review marks — is in
`~/.claude/CLAUDE.md` and applies with no per-project step.

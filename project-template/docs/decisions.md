# Decisions

The canonical record of decisions already made. `docs/charter.md` is how to read
it.

**Discipline (ADR):** one row per decision. A decision is never edited to reverse
it — a reversal is a **new** row, and the old row's `Status` becomes
`superseded→D##`. The `Rationale` is mandatory and is the point of the row: one
sentence, in the owner's words. If it needs a paragraph, it is an open question,
not a settled decision.

## The columns

| Column | Values | Meaning |
| --- | --- | --- |
| **ID** | `D-01`, `D-02`, … | Stable. Never reused. |
| **Alt** (altitude) | `arch` · `struct` · `impl` | The premise · a subsystem's shape · a tool choice. Inherent to the decision. |
| **Band** | `firm` · `mixed` · `revisitable` · *(blank = `unset`)* | How settled — **the owner sets this by hand.** See `docs/charter.md`. |
| **Flag** | blank · `Flagged: <reason>` | The owner writes *why* a decision is uneasy; Claude proposes a fix from the reason. A `Flagged:` reason lowers the bar whatever the Band says. |
| **Domain** | a short scope path | What the decision governs. Stops a subsystem-local or early decision being read as project-wide. |
| **Prov** (provenance) | `owner` · `ratified` · `claude` | Who made the call. `ratified` = Claude raised or drafted it, the owner agreed. `claude` = Claude wrote it, never explicitly ratified. |
| **Era** | *(project-defined)* | Which phase of the project. An early era is a stale-suspect. |
| **Status** | `accepted` · `needs-review` · `superseded→D##` · `withdrawn` | — |
| **Rationale** | one sentence, the owner's words | — |

`Alt`, `Domain`, `Prov` and `Era` are Claude-populated and the owner's to
correct; `Band`, `Flag` and the final `Rationale` wording are the owner's.

## The register

<!-- Populate by running /charter, or by hand. Example row: -->

| ID | Decision | Alt | Band | Flag | Domain | Prov | Era | Status | Rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D-01 | *(the decision, in a few words)* | arch | | | *(scope)* | owner | | accepted | *(one sentence, the owner's words)* |

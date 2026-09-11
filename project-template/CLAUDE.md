# CLAUDE.md — <project>

The shared method and behavioural rules live in `~/.claude/CLAUDE.md` (installed
by claude-kit). This file holds **only what is specific to this project** — if
a rule would make sense on any project, it belongs in the global file, not
here.

## What this is, and where it stands

<!-- A compressed pointer, not a copy: what the project does; that design.md
     is the architecture and the source of truth; that plan.md sequences it;
     that README.md is the outside summary derived from design.md and must
     not accumulate architecture of its own; roughly where the build stands. -->

## The workflow / how to verify

<!-- How a change is made and checked here. Name the check command — see
     .claude/commands/check.md. -->

## Environment gotchas

<!-- Things that cost real debugging time. Delete the heading if none yet. -->

## Decisions already made

The register is `docs/decisions.md`; `docs/charter.md` is how to read it. Check
both before proposing anything. The handful most likely to be re-suggested, all
`firm`:

<!-- List the 3–5 firm decisions worth stating up front, or run /charter. -->

## Vocabulary

`docs/glossary.md` is canonical — use its terms.

<!-- Add sections beyond these as the project actually needs them — e.g.
     "Operating constraints for the agent" for unusual safety requirements,
     "Naming" for terminology still in flux, "Scope boundary" for a hard
     edge worth restating close to the code. Don't add a section pre-
     emptively; add it when the need becomes real. -->

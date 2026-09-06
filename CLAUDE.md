# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What this project is

**claude-kit** is a toolkit that gets installed into other projects to provide:

1. **Audible feedback** — `notify.py` implements Claude Code hooks that ring when Claude needs attention, ding at turn boundaries, speak verification results, and catch errors before commits.
2. **Governance framework** — `governance/CLAUDE.md` and `governance/tiers.md` help projects distinguish settled decisions from advisory ones, and `governance/permissions.json` establishes safe permission defaults.
3. **Skills** — user-invoked (`charter`, `audit-absolutes`, `stress`, `session-log`) and model-invoked (`guard`, `drift`, `tangent`) discipline the conversation without requiring constant invocation.
4. **Agents** — narrow agents (`scout` for searching, `reviewer` for independent review) delegate to cheaper models to keep context lean.

The toolkit is installed via `python install.py /path/to/target-project`. Nothing in the target project is overwritten except `notify.py` (versioned code); everything meant to be edited locally (`CLAUDE.md`, `tiers.md`, skills, config) is written once and left alone.

## Architecture and structure

```
agents/          Two narrow agents that delegate to cheap models
  scout.md       Read-only search agent (Haiku)
  reviewer.md    Independent review agent (Sonnet)

commands/        Templates for projects to customize
  check.md       Verification command template

governance/      Behavioral rules and decision registry
  CLAUDE.md      12-point behavioral guidelines for how to work
  tiers.md       Registry: which decisions are settled, advisory, or arguable
  permissions.json   Baseline permissions: what runs without a prompt

hooks/           Audible notifications and verification
  notify.py      Main hook script (copies into all projects unchanged)
  notify.json.example   Configuration template (copied once per project)
  settings-hooks.json   Claude Code settings for hook registration
  README.md       Hook system documentation

skills/          User and model-invoked disciplines
  charter/       Interview to fill the tier registry
  audit-absolutes/   Find and confirm "must", "never", "always" statements
  stress/        Press a design for practical concerns
  guard/         Verify tests bite by breaking the code
  drift/         Find docs contradicted by recent changes
  tangent/       Park thoughts raised mid-task
  session-log/   Record what a session learned

install.py       Script that copies everything into a target project
README.md        User-facing documentation
.gitattributes   Line ending rules: shell scripts must stay LF
```

## Key design principles

**One-way copies:** `install.py` copies files to the target project. Fixes to `notify.py` and core files here ship to all projects via re-running the install; projects' own `CLAUDE.md`, `tiers.md`, and skills are never overwritten.

**Immutable except notify.py:** Most files are meant to be read and understood by the installed project, not modified. Only `notify.py` is versioned and re-copied, allowing bug fixes and improvements to propagate. This is explicit in `install.py`.

**Platform portability in notify.py:** The script detects `sys.platform` at runtime and chooses platform-specific backends for sounds (winsound on Windows, freedesktop theme on Linux) and speech (spd-say/espeak on Linux only; Windows PowerShell constraints block SAPI). See `RING_REPEATS`, `NOTIFY_ROUNDS`, `ROUND_GAP_SECONDS` at the top of the script for tuning constants.

**Line ending discipline:** `.gitattributes` enforces LF on shell scripts because CRLF breaks bash under some builds (commit 069719d).

**Narrow agents, cheap models:** Both agents delegate to cheaper models (`scout` → Haiku, `reviewer` → Sonnet) because they perform specific, scoped tasks where input is large and output is small. The savings are worth the round-trip.

## Working on this project

### Understanding a change

When a change touches `notify.py`, it ships to all installed projects on re-run, so test it carefully: verify that hooks still register, that sounds play on the target platform, and that verification doesn't break on edge cases. Look at `.gitattributes` and recent commits (especially 069719d, 236e425, a77b646) for gotchas.

When a change touches governance files (`CLAUDE.md`, `tiers.md`), it clarifies policy but does not override projects' own copies. New rules should surface tradeoffs explicitly (see §9 in `governance/CLAUDE.md` on model selection).

When a change touches a skill, the skill is meant to be read and understood by the person who runs it, not to be opaque. Skill definitions live in `SKILL.md` files; read the referenced skill docs to understand what it does.

When a change touches agents, recall that they start cold with no session context (except `scout` if forked with subagent_type: `fork`). Keep instructions self-contained.

### Install script behavior

`install.py` is the only distribution mechanism. It:
- Copies files from this repo into a target project under `.claude/`
- Merges permission rules rather than overwriting them (so re-running is safe)
- Reports what it wrote and what it kept (to show non-destructive updates)
- Accepts `--hooks`, `--governance` flags to install only a subset

Changes to `install.py` should preserve this non-destructive behavior.

### Testing changes

There is no automated test suite. Verify changes manually:
1. Make a change to the code (e.g., to `notify.py` or a skill)
2. Run `python install.py /tmp/test-project --hooks` (or `--governance`, or neither)
3. Check that the target project's `.claude/` was updated correctly
4. If the change touches hooks, start a Claude Code session in that project and verify the hooks work (sounds play, verification runs)
5. If the change touches governance or skills, read through to check for clarity and consistency with the rest of the kit

Commit 069719d added a self-test to `notify.py` (the `if __name__ == "__main__"` block) to catch line-ending issues; running `python hooks/notify.py` as a self-test is recommended for hook changes.

### Release considerations

- Keep `notify.py` portable: no platform-specific imports outside the backend section
- Test on Linux (freedesktop sounds, speech) before merging
- Line endings matter: use the `.gitattributes` rule
- Backward compatibility: `notify.json` schemas evolve carefully; an old project with old notify.py should still work when re-run with new install.py
- Agents should state their assumptions explicitly (what they assume about the project, what tools they need)

## Scope and non-goals

**In scope:**
- Improvements to notification and verification (`notify.py`)
- Refinements to the behavioral guidelines (`CLAUDE.md`)
- New skills to help with common decisions
- Fixes to installation or agent definitions

**Out of scope:**
- Adding tests where manual verification suffices (this is a small kit that ships rarely)
- Autoating the installation process (it is intentionally simple and auditable)
- Building a full IDE integration (the kit works through Claude Code's hook system)

---

## References

- `README.md` — user-facing introduction
- `governance/CLAUDE.md` — the 12-point behavioral framework that forms the project's philosophy
- `governance/tiers.md` — the decision registry structure
- `hooks/README.md` — technical details of the hook system

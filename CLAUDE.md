# CLAUDE.md — working on claude-kit

## What this is

A machine-global toolkit for Claude Code, installed into `~/.claude` by
`install.py`:

- **Notifications** — `hooks/notify.py` + `hooks/sounds/` + `hooks/desk-listener/`.
  Wired into `~/.claude/settings.json`, acts on the project in
  `$CLAUDE_PROJECT_DIR`. Push channels (`local` / `ntfy` / `pushover`) carry the
  alert to a workstation or phone when the box running the hook is headless.
- **The docs method** — `skills/` (nine, installed to `~/.claude/skills/`),
  `global/CLAUDE.md` (→ `~/.claude/CLAUDE.md`), and `project-template/` +
  `adopt.py` for the per-project half. Written up in `METHOD.md`.
- **`global/settings-hooks.json`** is the 10 hook entries (`__NOTIFY__`
  placeholder) that `install.py` merges into `~/.claude/settings.json`. It
  touches nothing else in that file — permissions are a per-project concern
  (`project-template/.claude/settings.json`, placed by `adopt.py`).

## Two install paths, do not confuse them

- **`install.py`** — machine-global. Copies `hooks/`, `skills/`, `agents/` into
  `~/.claude/`, merges settings. Idempotent; re-run to update. Never overwrites
  `~/.claude/CLAUDE.md` or `~/.claude/hooks/notify.json`.
- **`adopt.py <project>`** — one project. Creates the docs templates and a
  `CLAUDE.md` stub **only where they are absent**; prints a diff and stops
  otherwise. Never touches hooks or skills.

An existing project or machine `CLAUDE.md` is the owner's — it is never rewritten
unattended.

## Working here

- No automated test suite. After a change: `python3 hooks/notify.py selftest`;
  `HOME=$(mktemp -d) python3 install.py` twice and check idempotency;
  `python3 adopt.py $(mktemp -d)` twice.
- `notify.py` must stay portable: platform-specific code only in the marked
  backend section. The ring tuning constants (`RING_REPEATS`, `NOTIFY_ROUNDS`,
  `ROUND_GAP_SECONDS`) are at the top of the file.
- Sounds are regenerated with `hooks/sounds/generate.py` (deterministic — a
  regenerated WAV is byte-identical).
- `.gitattributes` keeps shell scripts LF.
- Every `notify.py` entry point returns 0 on anything unexpected — a broken hook
  must never take a session down.

## Downstream

`before94` is the project this was extracted from and still carries an in-repo
`.claude/` copy of an earlier version; migrating it to the global model is a
pending, deliberate task. `eyeprompt` uses the global install.

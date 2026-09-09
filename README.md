# claude-kit

Two things worth having on every project, set up **once per machine** so every
project and every Claude Code session gets them with no per-project step:

- **A session you can hear** — hooks that ring when Claude needs you, ding when a
  long turn ends, and (when you work over SSH on a headless box) push the sound
  to the machine you are actually sitting at.
- **A way of deciding who decides** — a decision register, a charter, review
  marks and a set of skills that keep a project's documents and decisions
  honest. The whole method is written up in [`METHOD.md`](METHOD.md).

## Install

```
git clone https://github.com/lukeybe543/claude-kit ~/.claude/claude-kit
python3 ~/.claude/claude-kit/install.py            # headless / server
python3 ~/.claude/claude-kit/install.py --desktop  # a workstation with speakers
```

This copies the notification hooks, the skills and the agents into `~/.claude/`,
wires the hooks into `~/.claude/settings.json` (keeping whatever is already
there — permissions and everything else are left alone), and — with `--desktop`
— sets up the desk-listener service. It is idempotent; **update by re-running
it**:

```
git -C ~/.claude/claude-kit pull && python3 ~/.claude/claude-kit/install.py
```

`~/.claude/CLAUDE.md` and `~/.claude/hooks/notify.json` are yours to edit —
install.py writes them once and then leaves them alone, and if a
`~/.claude/CLAUDE.md` already exists it is never overwritten (you get a diff to
merge).

## Adopt the docs method in a project

```
python3 ~/.claude/claude-kit/adopt.py /path/to/project
```

Scaffolds `docs/{charter,decisions,glossary}.md`, a project `CLAUDE.md` stub and
`.claude/notify.json` — **only where they don't already exist**. Then run
`/charter` before writing code. See [`METHOD.md`](METHOD.md).

## Notifications

| When | What happens |
| :--- | :--- |
| Claude needs permission or an answer | Rings; **stops the moment you act**. Unanswered, it comes back a minute later, three rounds, then gives up. |
| A turn ends after 45s+ of work | A soft ding — short turns stay silent on purpose. |
| A file is written, in a project with a `lint` command | Lints just that file; a violation goes straight back to Claude. |
| Code changed this turn, in a project with a `verify` command | Runs it in the background, then chimes or errors. |
| A commit is about to be made | Runs `verify` first, refuses the commit if it is red. |
| An edit touches a `guarded_path` | Becomes a permission prompt instead of just happening. |
| The session is about to compact | A distinct sound. |

The sounds are bundled WAVs (`hooks/sounds/`, synthesised by `generate.py`) —
no system sound theme, so nothing goes missing and there is no jarring stock
ring. Project-specific behaviour (`lint`, `verify`, `guarded_paths`) is opt-in
via a project `.claude/notify.json`, merged over the global defaults; a project
with none just gets the sounds.

### Hearing it from a headless dev box

Working over SSH (Zed / VS Code → a droplet), the hooks run on the droplet,
which has no audio. Point them at the machine you sit at: run
`install.py --desktop` there, and in the dev box's
`~/.claude/hooks/notify.local.json` set

```json
{ "local": "http://<workstation-tailnet-ip>:19191" }
```

so the needs-you / turn-end events play on your speakers over the tailnet.
`pushover` and `ntfy` keys in the same file add a phone as a fallback. See
[`hooks/desk-listener/README.md`](hooks/desk-listener/README.md).

## Layout

```
install.py            machine setup + update (idempotent)
adopt.py              per-project docs scaffold (creates files only)
METHOD.md             the docs method, written up
global/               what install.py puts in ~/.claude
  CLAUDE.md            -> ~/.claude/CLAUDE.md  (behavioural rules, review marks, meta-rule)
  settings-hooks.json  the 10 notify hook entries, merged into ~/.claude/settings.json
hooks/                notify.py, the bundled sounds, the desk-listener
skills/  agents/       -> ~/.claude/skills/*, ~/.claude/agents/*
commands/check.md     a /check template for a project
project-template/     what adopt.py scaffolds into a project
  .claude/settings.json   a safe per-project permission baseline
```

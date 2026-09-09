# notify.py — hooks for a session you can hear

Claude Code's own notifications are easy to miss, so this turns the moments that
matter into sounds, and uses the same wiring to lint and verify as work happens.

| When | What happens |
| :--- | :--- |
| Claude needs permission or an answer | Rings; **stops the moment you act**. Unanswered, it comes back a minute later, up to three rounds, then gives up |
| A turn ends after 45s+ of work | A soft ding |
| A source file is written | Lints just that file; a violation goes straight back to Claude |
| Code changed this turn | Runs the verification command in the background, then chimes or errors |
| A commit is about to be made | Runs verification first, and refuses the commit if it is red |
| An edit touches reserved text | Turns into a permission prompt instead of just happening |
| The session is about to compact | A distinct sound — the session has grown expensive |
| A session starts | Says so if the last verification run left the tree red |
| Any of the above, with a push channel configured | Also sends a one-line push (needs-you / turn-end / commit-blocked / compacting) — the channel that reaches you when the sound cannot |

## How it is installed

`notify.py` lives at `~/.claude/hooks/notify.py` and is wired into
`~/.claude/settings.json` by the top-level `install.py`, so every project gets
it. It finds the project a hook is acting on from `$CLAUDE_PROJECT_DIR`.

Config is merged, later winning: `~/.claude/hooks/notify.json` (global
defaults) → `<project>/.claude/notify.json` (that project's `lint` / `verify` /
`guarded_paths`) → `*.local.json` beside each (the push URLs and tokens,
gitignored). A project with no `notify.json` just gets the sounds and pushes.

```json
{
  "lint": ["{python}", "-m", "ruff", "check", "{file}"],
  "lint_suffixes": [".py"],
  "verify": ["bash", "run_tests.sh"],
  "guarded_paths": ["design.md"]
}
```

`{python}` becomes the interpreter running the hook, and `{file}` the file just
written. For a TypeScript project, `["npx", "eslint", "{file}"]` with
`[".ts", ".tsx"]` and `["npm", "test"]` is the same shape.

## Sound

The five sounds ship as WAVs in `sounds/`, the same on every platform —
`sounds/generate.py` synthesises them from sine tones and can retune them. A
system sound theme is not used: it is absent on a headless box, and where it
exists the stock "incoming call" is the sound this replaced. WAV specifically,
because `winsound` (Windows) and `aplay` both play only WAV.

**Windows** plays them with `winsound`. Speech is unavailable there: PowerShell
runs in ConstrainedLanguage mode and Windows Script Host is blocked by group
policy, so `System.Speech`, the `SAPI.SpVoice` COM object and `cscript` all
fail.

**Linux** plays them through the first of `paplay`, `pw-play`, `afplay` or
`aplay` it finds, falling back to `canberra-gtk-play`. It also *speaks*
verification results through `spd-say` (speech-dispatcher) or `espeak-ng` where
either is installed. Nothing is configured per machine; the backend is chosen
from `sys.platform` at runtime.

## Reaching you on a headless box

Run Claude Code over SSH to a server (a droplet reached from Zed or VS Code) and
the hook runs *there* — no sound card, no player, silence. The terminal bell is
no help either: Zed drops OSC 9, and its bell-notification does not fire for
remote terminals.

The way through is `_notify_push`, which fans the needs-you / turn-end /
commit-blocked / compacting events out to whatever is set in `notify.local.json`
(gitignored — the URLs and tokens never land in git). Each send is independent
and a failed or slow one is swallowed after 5 s.

```json
{
  "local": "http://127.0.0.1:19191",
  "ntfy": "https://ntfy.sh/your-unguessable-topic",
  "pushover": { "token": "…", "user": "…" }
}
```

- **`local`** — the desk-listener on the machine you actually sit at, reached
  over a tailnet (fires whenever that machine is up) or a reverse SSH forward
  (fires while you are connected). It plays the sound and pops a desktop
  notification. See [`desk-listener/`](desk-listener/README.md). This is the one
  to use for a fixed workstation.
- **`ntfy`** — an [ntfy](https://ntfy.sh) topic; subscribe in the app and pick
  the sound there. For a phone. (Android per-channel sound settings can be
  fiddly — check the *Max priority* channel.)
- **`pushover`** — [Pushover](https://pushover.net): make an account, register
  an application for the API token, and take your user key from the dashboard.
  For a phone, when ntfy's sound won't cooperate.

## Housekeeping

State lives in `~/.claude/hooks/state/`: the ring token, the turn clock, and
`last-verify.log` (the full output of the last verification run — shared across
the machine's sessions, so acting in any session silences a ring). Per-machine
push config is `~/.claude/hooks/notify.local.json`, gitignored. `/hooks` lists
everything live; disable any of it by deleting its entry from
`~/.claude/settings.json`.

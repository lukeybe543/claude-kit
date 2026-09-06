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

## Installing it in another project

```
python .claude/hooks/notify.py install /path/to/other/project
```

That copies the script and this README, writes a blank `notify.json`, and merges
the hook entries into the target's `.claude/settings.json`, leaving anything
already there alone. It deliberately copies only the hooks that *are* this
script — project-specific rules written directly into `settings.json`, like the
blocked-path rule below, stay behind.

Then point `notify.json` at the new project's commands. Every key is optional;
an empty or missing one turns that behaviour off, so a project with no test
suite simply gets the sounds.

```json
{
  "lint": ["{python}", "-m", "ruff", "check", "{file}"],
  "lint_suffixes": [".py"],
  "verify": ["bash", "run_tests.sh"],
  "guarded_text": ["RULE_VERSION"]
}
```

`{python}` becomes the interpreter running the hook, and `{file}` the file just
written. For a TypeScript project, `["npx", "eslint", "{file}"]` with
`[".ts", ".tsx"]` and `["npm", "test"]` is the same shape.

## Platforms

The script picks its backend from `sys.platform` at runtime — nothing needs to
be configured per machine, and the same file works on both. VS Code is not
involved: the hook is a plain process, so Python's own view of the OS is what
decides.

**Windows** uses `winsound` with the stock sounds in `%SystemRoot%\Media`.
Speech is unavailable on this machine: PowerShell runs in ConstrainedLanguage
mode and Windows Script Host is blocked by group policy, so `System.Speech` and
the `SAPI.SpVoice` COM object both fail, as does `cscript`. Distinct sounds
stand in for words.

**Linux** plays the freedesktop sound theme through the first of `paplay`,
`pw-play`, `afplay` or `aplay` it finds, falling back to `canberra-gtk-play`.
It also *speaks* verification results through `spd-say` (speech-dispatcher) or
`espeak-ng` where either is installed — so on Fedora the spoken notification
that Windows cannot give you is available. On a Fedora workstation both the
sound theme and speech-dispatcher are usually present already; if not:

```
sudo dnf install sound-theme-freedesktop pipewire-utils speech-dispatcher
```

To add another platform, extend the `SOUNDS` table and `_player()`.

## The project-specific rule this project also uses

`.claude/settings.json` blocks reads of `docs/archive/**` with a static
`PreToolUse` rule — no Python involved. It is a project rule rather than part of
this script, so `install` does not carry it to other projects. The pattern is
worth copying by hand where a directory must never be read as spec:

```json
"PreToolUse": [
  {
    "matcher": "Read",
    "hooks": [
      {
        "type": "command",
        "if": "Read(docs/archive/**)",
        "command": "echo '{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"...\"}}'"
      }
    ]
  }
]
```

## Housekeeping

State lives in `.claude/state/` (gitignored): the ring token, the turn clock,
and `last-verify.log`, which holds the full output of the last verification run.
Nothing else is written. `/hooks` lists everything that is live, and disabling
any of it is a matter of deleting its entry from `.claude/settings.json`.

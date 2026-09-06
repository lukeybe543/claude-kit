# Prompt: rebuild this notification system on Linux

Paste everything below the line into a fresh Claude Code session on the Fedora
machine. It is self-contained — it does not need this repository, only the
description. If you can copy files instead, do that: `python
.claude/hooks/notify.py install /path/to/project` already works on Linux, and
this prompt exists for the case where you are starting clean.

---

Build me a set of Claude Code hooks that make a session audible. I have ADHD and
the built-in notifications are too easy to miss, so the point is that the
moments which need me actually reach me. Put the script at
`.claude/hooks/notify.py`, its configuration at `.claude/hooks/notify.json`, and
wire the hooks into `.claude/settings.json`. Write scratch state to
`.claude/state/` and add that directory to `.gitignore`.

**Behaviour, event by event.**

- `Notification` — Claude needs permission or an answer. Ring: play the sound
  twice. If I have not acted, wait 60 seconds and ring again, for three rounds
  in total, then give up and stay quiet. Every new notification starts a fresh
  ringer, so giving up is never permanent.
- `UserPromptSubmit` — I acted. Stop any ringing, record the turn's start time,
  and clear the "code changed" flag.
- `PostToolUse`, all tools — I acted (approving a permission prompt is what
  makes a tool run, and there is no "permission answered" event to listen for).
  Stop any ringing.
- `PermissionDenied` — I acted. Stop any ringing.
- `PostToolUse` on `Edit|Write` — lint just the file that was written, using the
  command from the config. If it fails, print the output on stderr and **exit 2**,
  which hands the error back to Claude as a blocking error. Also mark that code
  changed this turn.
- `Stop` — if code changed this turn, run the project's verification command in
  the background, save its output to `.claude/state/last-verify.log`, play a
  pass or fail sound, speak the result, and print a `systemMessage` saying which.
  If no code changed but the turn ran 45 seconds or longer, play a soft "done"
  sound. Say nothing at all for a short turn: an alert after every three-second
  reply stops being a signal within a day.
- `PreToolUse` on `Edit|Write` — if the edit's payload contains any string listed
  in the config's `guarded_text`, return a `permissionDecision` of `"ask"` with a
  reason, so a reserved change becomes a prompt instead of just happening.
- `PreCompact` — play a distinct sound and print a `systemMessage`: the session
  has grown long and starting the next task with `/clear` is cheaper.
- `SessionStart` — if `last-verify.log` records a failure, report which parts
  failed, both as a `systemMessage` and as `additionalContext`. Stay silent when
  the last run was green.

**The ring has to be cancellable, and that constrains the design.** A second
process cannot reliably stop the first one's audio, so the ringer must stay
alive and watch for a stop signal itself. Use a flag file holding the ringer's
PID as a token: the "I acted" hooks delete it, and a newer ringer overwrites it
so the older one stands down. Poll every 0.1 seconds — during the sound *and*
during the 60-second gaps — so acting mid-gap stops the cycle too. On Linux,
play through a subprocess and `terminate()` it to cut the sound off.

**Sound and speech on Fedora.** Play the freedesktop theme from
`/usr/share/sounds/freedesktop/stereo/` using the first of `paplay`, `pw-play`,
`aplay` found on PATH, falling back to `canberra-gtk-play -f`. Use
`phone-incoming-call.oga` for "needs you", `complete.oga` for pass,
`dialog-error.oga` for fail, `message.oga` for a finished turn, and
`dialog-warning.oga` for compaction. For speech use `spd-say -w`, falling back
to `espeak-ng`. If the installs are missing:
`sudo dnf install sound-theme-freedesktop pipewire-utils speech-dispatcher`.

Pick the backend from `sys.platform` at runtime rather than configuring it, and
keep the platform-specific parts in one clearly marked section so another OS can
be added there. (On Windows the same script uses `winsound` and cannot speak,
because PowerShell runs in ConstrainedLanguage mode and Windows Script Host is
blocked by policy — worth knowing if this ever has to run on both.)

**Keep the project-specific parts out of the code.** `notify.json` holds them,
and any empty or missing key simply turns that behaviour off:

```json
{
  "lint": ["{python}", "-m", "ruff", "check", "{file}"],
  "lint_suffixes": [".py"],
  "verify": ["bash", "run_tests.sh"],
  "guarded_text": []
}
```

`{python}` means the interpreter running the hook and `{file}` the file just
written. Work out the right values for this project rather than assuming these.

**Two things that will silently break it if you miss them.** Hooks default to a
60-second timeout, which would kill the ringer partway through its first gap, so
give the `Notification` hook `"timeout": 300` and `"async": true`. And every
entry point must exit 0 on anything unexpected — a hook that raises can take the
session down — so wrap the dispatch in a broad `except` with a comment saying
why.

**Prove it works before telling me it does.** Show me: the ring stopping within
a fraction of a second of a simulated action; an uninterrupted cycle giving up
after three rounds and cleaning up its flag file; an action landing inside a gap
stopping the cycle; the lint hook exiting 2 on a file with a deliberate error;
and the guarded-text check firing on a match and staying silent otherwise. Then
confirm the settings file is valid JSON and that the hooks are actually live.

Finally, add a `python notify.py install <project>` command that copies the
script and config into another project and merges its hook entries into that
project's `.claude/settings.json` without disturbing what is already there.

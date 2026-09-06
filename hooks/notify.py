"""Audible alerts, lint-on-edit and post-turn verification, as Claude Code hooks.

Portable by design. Everything platform-specific lives in the backend section
below, and everything project-specific lives in `notify.json` beside this file,
so the script itself copies into any project unchanged -- `python notify.py
install <project>` does exactly that. See README.md.

Speech: on Linux this speaks results through `spd-say` where it is present. On
Windows it cannot -- PowerShell runs in ConstrainedLanguage mode and Windows
Script Host is blocked by group policy, so both SAPI routes are shut -- and
distinct stock sounds stand in for words.

Every entry point returns 0 on anything unexpected: a broken hook must never be
able to stop a session.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATE = HERE.parent / "state"
QUIET = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}

# One round of "needs-you" is this many plays of the sound.
RING_REPEATS = 2

# Silence is not an answer, so a round that goes unanswered is repeated after a
# gap -- but only this many times. Past that the ringing would be nagging an
# empty chair, so it gives up and waits; acting resets the whole cycle, because
# the next thing that needs an answer starts a fresh ringer.
NOTIFY_ROUNDS = 3
ROUND_GAP_SECONDS = 60

# A turn shorter than this was never long enough to lose someone's attention;
# alerting on it would only train the ear to ignore the sound.
QUIET_TURN_SECONDS = 45


# ---------------------------------------------------------------------------
# Platform backends
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    import winsound

    _MEDIA = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Media"
    SOUNDS = {
        "needs-you": _MEDIA / "Ring01.wav",
        "pass": _MEDIA / "chimes.wav",
        "fail": _MEDIA / "chord.wav",
        "done": _MEDIA / "ding.wav",
        "compacting": _MEDIA / "ringout.wav",
    }
else:
    winsound = None
    _MEDIA = Path("/usr/share/sounds/freedesktop/stereo")
    SOUNDS = {
        "needs-you": _MEDIA / "phone-incoming-call.oga",
        "pass": _MEDIA / "complete.oga",
        "fail": _MEDIA / "dialog-error.oga",
        "done": _MEDIA / "message.oga",
        "compacting": _MEDIA / "dialog-warning.oga",
    }


def _player():
    """The command that plays one sound file and exits, or None if there is none."""
    for name in ("paplay", "pw-play", "afplay", "aplay"):
        found = shutil.which(name)
        if found:
            return [found]
    canberra = shutil.which("canberra-gtk-play")
    return [canberra, "-f"] if canberra else None


def _speak(text):
    """Say `text` aloud where the platform allows it; stay silent where it does not."""
    for name, args in (("spd-say", ["-w"]), ("espeak-ng", []), ("say", [])):
        found = shutil.which(name)
        if found:
            subprocess.run([found, *args, text], check=False, **QUIET)
            return


def _sound_seconds(path):
    try:
        with wave.open(str(path)) as handle:
            return handle.getnframes() / handle.getframerate()
    except Exception:  # noqa: BLE001 -- any unreadable file just gets the default
        return 3.0


def _play_once(event):
    """Play a sound and wait for it to finish."""
    path = SOUNDS[event]
    if winsound:
        winsound.PlaySound(str(path), winsound.SND_FILENAME)
        return
    player = _player()
    if player:
        subprocess.run([*player, str(path)], check=False, **QUIET)


def _play_interruptibly(event, token):
    """Play a sound once; return True if the user acted before it finished."""
    path = SOUNDS[event]
    if winsound:
        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        deadline = time.time() + _sound_seconds(path)
        while time.time() < deadline:
            time.sleep(0.1)
            if _superseded(token):
                winsound.PlaySound(None, winsound.SND_PURGE)
                return True
        return False

    player = _player()
    if not player:
        return True
    playing = subprocess.Popen([*player, str(path)], **QUIET)
    while playing.poll() is None:
        time.sleep(0.1)
        if _superseded(token):
            playing.terminate()
            return True
    return False


# ---------------------------------------------------------------------------
# State and configuration
# ---------------------------------------------------------------------------

def _flag(name):
    return STATE / name


def _config():
    try:
        return json.loads((HERE / "notify.json").read_text())
    except (OSError, ValueError):
        return {}


def _superseded(token):
    try:
        return _flag("ringing").read_text() != token
    except OSError:
        return True


# ---------------------------------------------------------------------------
# Hook entry points
# ---------------------------------------------------------------------------

def _wait(seconds, token):
    """Sleep, returning True as soon as the user acts."""
    deadline = time.time() + seconds
    while time.time() < deadline:
        time.sleep(0.1)
        if _superseded(token):
            return True
    return False


def _stand_down(token):
    """Give up the ring, unless a newer ringer has already taken it over."""
    try:
        if _flag("ringing").read_text() == token:
            _flag("ringing").unlink()
    except OSError:
        pass
    return 0


def ring():
    """Ring, and keep coming back, until the user acts or the rounds run out."""
    STATE.mkdir(parents=True, exist_ok=True)
    token = str(os.getpid())
    _flag("ringing").write_text(token)
    for round_number in range(NOTIFY_ROUNDS):
        if round_number and _wait(ROUND_GAP_SECONDS, token):
            return 0
        for _ in range(RING_REPEATS):
            if _play_interruptibly("needs-you", token):
                return 0
    return _stand_down(token)


def silence():
    """The user acted; stop any ringing."""
    _flag("ringing").unlink(missing_ok=True)
    return 0


def turn_start():
    STATE.mkdir(parents=True, exist_ok=True)
    silence()
    _flag("turn-start").write_text(str(time.time()))
    _flag("code-edited").unlink(missing_ok=True)
    return 0


def guard_edit():
    """Hold an edit that touches something the project has reserved for its owner."""
    config = _config()
    guarded_text = config.get("guarded_text") or []
    guarded_paths = config.get("guarded_paths") or []
    if not guarded_text and not guarded_paths:
        return 0

    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    path = (tool_input.get("file_path") or "").replace("\\", "/")

    reason = None
    folder = next((p for p in guarded_paths if p in path), None)
    if folder:
        reason = ("This edits " + folder + ", which the project treats as a document to be "
                  "changed deliberately. Say what the change is and why before making it -- "
                  "and if the wording carries a requirement, clarify it first.")
    else:
        word = next((w for w in guarded_text if w in json.dumps(tool_input)), None)
        if word:
            reason = ("This edit touches " + word + ", which docs/tiers.md places in "
                      "Tier 1 -- settled, and the owner's call rather than Claude's.")
    if not reason:
        return 0

    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": reason,
    }}))
    return 0


def after_edit():
    """Lint the file that was just written; hand any error straight back."""
    config = _config()
    command = config.get("lint")
    if not command:
        return 0
    payload = json.load(sys.stdin)
    path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not any(path.endswith(s) for s in config.get("lint_suffixes") or []):
        return 0

    STATE.mkdir(parents=True, exist_ok=True)
    _flag("code-edited").touch()

    filled = [sys.executable if a == "{python}" else a.replace("{file}", path)
              for a in command]
    lint = subprocess.run(filled, cwd=ROOT, capture_output=True, text=True, check=False)
    if lint.returncode:
        print(lint.stdout or lint.stderr, file=sys.stderr)
        return 2  # exit 2 feeds stderr back to Claude as a blocking error
    return 0


def _bash():
    """The bash that can actually run this project's scripts.

    On Windows, PATH may resolve `bash` to the WSL launcher in System32, which
    cannot run a script saved with Windows line endings, nor a Windows path.
    Git for Windows' bash can, so prefer it and refuse the WSL one.
    """
    if sys.platform == "win32":
        for variable in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)"):
            candidate = Path(os.environ.get(variable, "")) / "Git" / "bin" / "bash.exe"
            if candidate.is_file():
                return str(candidate)
    found = shutil.which("bash")
    return None if found and "System32" in found else found


def _run_verify():
    """Run the project's verification command; return (passed, output), or None."""
    command = _config().get("verify")
    if not command:
        return None
    filled = []
    for argument in command:
        if argument == "{python}":
            filled.append(sys.executable)
        elif argument == "bash":
            resolved = _bash()
            if not resolved:
                return None
            filled.append(resolved)
        else:
            filled.append(argument)
    if not (Path(filled[0]).is_file() or shutil.which(filled[0])):
        return None

    run = subprocess.run(filled, cwd=ROOT, capture_output=True, text=True, check=False)
    output = run.stdout + run.stderr
    STATE.mkdir(parents=True, exist_ok=True)
    _flag("last-verify.log").write_text(output)
    return run.returncode == 0, output


def turn_end():
    """Run the verification loop if code changed; otherwise mark a long turn ending."""
    silence()
    result = _run_verify() if _flag("code-edited").exists() else None
    if result is None:
        try:
            started = float(_flag("turn-start").read_text())
        except (OSError, ValueError):
            return 0
        if time.time() - started >= QUIET_TURN_SECONDS:
            _play_once("done")
        return 0

    _flag("code-edited").unlink()
    passed, _ = result
    _play_once("pass" if passed else "fail")
    _speak("Verification passed" if passed else "Verification failed")
    print(json.dumps({"systemMessage": (
        "Verification: ALL LAYERS PASS" if passed else
        "Verification: SOME LAYERS FAILED -- see .claude/state/last-verify.log"
    )}))
    return 0


_COMMIT = re.compile(r"\bgit\b.*\bcommit\b")
_SEGMENTS = re.compile(r"&&|\|\||;|\|")


def _is_commit(command):
    """True when the command really runs `git commit`, however it is dressed up.

    Looking for the literal "git commit" misses `git -c user.name=... commit`,
    which is how a commit is usually made from a script; looking for both words
    anywhere matches `echo commit && git log`. Split on shell separators and
    require both words, in that order, inside a single segment.
    """
    return any(_COMMIT.search(part) for part in _SEGMENTS.split(command))


def commit_gate():
    """Refuse a commit while verification is red."""
    payload = json.load(sys.stdin)
    # A settings-level filter cannot see through `cd x && git -c ... commit`, so the
    # check is made here, on the real command, where it cannot be lost.
    if not _is_commit((payload.get("tool_input") or {}).get("command") or ""):
        return 0

    result = _run_verify()
    if result is None:
        print(json.dumps({"systemMessage":
                          "Commit gate skipped: verification could not be run."}))
        return 0
    passed, output = result
    if passed:
        return 0

    _play_once("fail")
    failed = [line.strip() for line in output.splitlines() if ": FAIL" in line]
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Verification is red, so nothing was committed: "
            + "; ".join(failed or ["see .claude/state/last-verify.log"])
            + ". Fix it first, or commit by hand if this is deliberate."
        ),
    }}))
    return 0


def compacting():
    """Compaction means the session has grown expensive; say so out loud."""
    _play_once("compacting")
    print(json.dumps({"systemMessage": (
        "Compacting -- this session has grown long. Finishing the current task and "
        "starting the next with /clear is cheaper than carrying it forward."
    )}))
    return 0


def session_start():
    """Open a session knowing whether the tree was left red."""
    try:
        log = _flag("last-verify.log").read_text()
    except OSError:
        return 0
    if "SOME LAYERS FAILED" not in log:
        return 0
    failed = [line for line in log.splitlines() if ": FAIL" in line]
    note = ("The last verification run left the tree red: "
            + "; ".join(failed or ["see .claude/state/last-verify.log"]))
    print(json.dumps({
        "systemMessage": note,
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": note},
    }))
    return 0


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def selftest():
    """Check the parts that have no other way of telling you they are broken."""
    commits = ["git commit -m x", "cd /tmp && git commit -m x",
               "git -c user.name=a -c user.email=b commit -q -F -",
               "git add -A && git -c user.name=a commit -m x"]
    not_commits = ["git log --oneline", "echo commit && git log", "ls -la",
                   "python notify.py commit-gate"]
    for command in commits:
        assert _is_commit(command), "should gate: " + command
    for command in not_commits:
        assert not _is_commit(command), "should not gate: " + command
    missing = [name for name, path in SOUNDS.items() if not Path(path).is_file()]
    print("commit detection: " + str(len(commits) + len(not_commits)) + " cases pass")
    print("sounds missing: " + (", ".join(missing) if missing else "none"))
    print("bash for verification: " + str(_bash()))
    return 0


def install():
    """Copy these hooks into another project, settings and all."""
    target = Path(sys.argv[2]).expanduser().resolve()
    hooks = target / ".claude" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / "notify.py", hooks / "notify.py")
    shutil.copy2(HERE / "README.md", hooks / "README.md")
    if not (hooks / "notify.json").exists():
        (hooks / "notify.json").write_text(json.dumps(
            {"lint": [], "lint_suffixes": [], "verify": [], "guarded_text": []},
            indent=2) + "\n")

    settings_path = target / ".claude" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text())
    except (OSError, ValueError):
        settings = {}

    # Take the hook groups that are this script, so project-specific rules -- a
    # blocked path, say -- are never carried across with it.
    mine = json.loads((HERE.parent / "settings.json").read_text()).get("hooks")
    if not mine:
        print("No hooks to export: " + str(HERE.parent / "settings.json")
              + " has none. Install from a project where these hooks are already wired.")
        return 1
    existing = settings.setdefault("hooks", {})
    added = 0
    for event, groups in mine.items():
        portable = [group for group in groups
                    if all("notify.py" in h.get("command", "") for h in group["hooks"])]
        for group in portable:
            if group not in existing.setdefault(event, []):
                existing[event].append(group)
                added += 1

    settings_path.write_text(json.dumps(settings, indent=2) + "\n")
    print("Installed into " + str(target) + ": " + str(added) + " hook group(s). "
          "Edit " + str(hooks / "notify.json") + " to point lint and verify at "
          "this project's own commands.")
    return 0


COMMANDS = {
    "ring": ring,
    "silence": silence,
    "turn-start": turn_start,
    "guard-edit": guard_edit,
    "after-edit": after_edit,
    "turn-end": turn_end,
    "commit-gate": commit_gate,
    "selftest": selftest,
    "compacting": compacting,
    "session-start": session_start,
    "install": install,
}


def main():
    return COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 -- a hook must never take the session down with it
        sys.exit(0)

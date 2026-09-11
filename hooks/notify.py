"""Audible alerts, lint-on-edit and post-turn verification, as Claude Code hooks.

Installed once per machine at `~/.claude/hooks/notify.py` and wired into
`~/.claude/settings.json`, so every project and every session gets it with no
per-project setup. Project-specific behaviour (guarded paths, a lint command, a
verify command) is opt-in: drop a `.claude/notify.json` in the project and it is
merged over the global defaults. The project a hook is acting on comes from
`$CLAUDE_PROJECT_DIR`.

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
import shlex
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "state"
QUIET = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}


def _project_dir():
    """The project the current hook is acting on."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())


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

# Ceilings on the project's own lint/verify commands, kept under the matching
# hook's settings.json timeout (60s / 300s) so a stuck command ends in a clean
# timeout message instead of Claude Code hard-killing the hook -- and, for
# commit-gate, ends in a bounded delay on every commit rather than an
# unbounded one on a project whose verify command hangs.
LINT_TIMEOUT_SECONDS = 45
VERIFY_TIMEOUT_SECONDS = 240


# ---------------------------------------------------------------------------
# Platform backends
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    import winsound
else:
    winsound = None

# One bundled WAV per event, identical on every platform. A system sound theme
# is no good here: it is absent on a headless box, and where it exists the
# stock "incoming call" is the sound this replaced. See sounds/generate.py.
SOUNDS = {event: HERE / "sounds" / (event + ".wav")
          for event in ("needs-you", "pass", "fail", "done", "compacting")}


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
    if not path.is_file():
        return
    if winsound:
        winsound.PlaySound(str(path), winsound.SND_FILENAME)
        return
    player = _player()
    if player:
        subprocess.run([*player, str(path)], check=False, **QUIET)


def _play_interruptibly(event, token):
    """Play a sound once; return True if the user acted before it finished."""
    path = SOUNDS[event]
    if not path.is_file():
        return True
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


def _guarded_marker(session_id):
    slug = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)[:120]
    return STATE / ("guarded-seen-" + slug)


def _guarded_already_flagged(session_id, path):
    """A guarded document under active revision is announced once per session,
    not on every edit. True once an edit to `path` has gone through this session."""
    if not session_id:
        return False
    try:
        return path in _guarded_marker(session_id).read_text().splitlines()
    except OSError:
        return False


def _remember_guarded(session_id, path):
    if not session_id:
        return
    STATE.mkdir(parents=True, exist_ok=True)
    marker = _guarded_marker(session_id)
    try:
        seen = set(marker.read_text().splitlines())
    except OSError:
        seen = set()
    if path not in seen:
        marker.write_text("\n".join(sorted(seen | {path})) + "\n")
    cutoff = time.time() - 7 * 86400
    for stale in STATE.glob("guarded-seen-*"):
        try:
            if stale.stat().st_mtime < cutoff:
                stale.unlink()
        except OSError:
            pass


def _config():
    """The merged config, in increasing precedence:

      1. ~/.claude/hooks/notify.json          -- global defaults (usually empty)
      2. <project>/.claude/notify.json         -- this project's lint/verify/guards
      3. ~/.claude/hooks/notify.local.json     -- this machine's push URLs/tokens
      4. <project>/.claude/notify.local.json   -- rare per-project machine override

    *.local.json holds URLs and tokens and is gitignored; the rest is committed.
    """
    project = _project_dir() / ".claude"
    sources = (HERE / "notify.json", project / "notify.json",
               HERE / "notify.local.json", project / "notify.local.json")
    config = {}
    for source in sources:
        try:
            config.update(json.loads(source.read_text()))
        except (OSError, ValueError):
            pass
    return config


def _superseded(token):
    try:
        return _flag("ringing").read_text() != token
    except OSError:
        return True


def _stdin_payload():
    """The hook's JSON payload from stdin, or {} when there is nothing to read."""
    try:
        return json.load(sys.stdin)
    except (OSError, ValueError):
        return {}


def _post(url, data, headers):
    """POST and forget. Any failure -- DNS, timeout, refused, bad URL -- is fine:
    a missed notification must never be able to hold up or break a hook."""
    try:
        urllib.request.urlopen(
            urllib.request.Request(url, data=data, headers=headers, method="POST"),
            timeout=5).close()
    except Exception:  # noqa: BLE001
        pass


def _notify_push(title, body, event="needs-you", priority="default", tags=""):
    """Fan the alert out to every notifier in the merged config's *.local.json.

    `local` is the desk-listener on the machine you sit at, reached over a
    tailnet or a reverse SSH forward (see desk-listener/); `ntfy` and `pushover`
    reach a phone. Configure any combination; an unset one is simply skipped.
    """
    config = _config()

    ntfy = config.get("ntfy")
    if ntfy:
        headers = {"Title": title, "Priority": priority}
        if tags:
            headers["Tags"] = tags
        _post(ntfy, body.encode("utf-8"), headers)

    pushover = config.get("pushover") or {}
    if pushover.get("token") and pushover.get("user"):
        _post("https://api.pushover.net/1/messages.json", urllib.parse.urlencode({
            "token": pushover["token"], "user": pushover["user"],
            "title": title, "message": body or title,
            "priority": {"min": -2, "low": -1, "default": 0,
                         "high": 1, "max": 1}.get(priority, 0),
        }).encode("utf-8"), {"Content-Type": "application/x-www-form-urlencoded"})

    local = config.get("local")
    if local:
        _post(local,
              json.dumps({"event": event, "title": title, "body": body}).encode("utf-8"),
              {"Content-Type": "application/json"})


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
    message = (_stdin_payload().get("message") or "").strip()
    _notify_push(_project_dir().name + " needs you",
                 message or "Claude is waiting for a permission or an answer",
                 event="needs-you", priority="max", tags="bell")
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
        if _guarded_already_flagged(payload.get("session_id") or "", path):
            return 0  # announced once this session; do not nag on every edit
        reason = ("This edits " + folder + ", which the project treats as a document to be "
                  "changed deliberately. Say what the change is and why before making it -- "
                  "and if the wording carries a requirement, clarify it first. "
                  "You will not be asked again for this file this session.")
    else:
        word = next((w for w in guarded_text if w in json.dumps(tool_input)), None)
        if word:
            reason = ("This edit touches " + word + ", which the project's decision "
                      "register reserves for the owner rather than Claude.")
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
    payload = json.load(sys.stdin)
    path = (payload.get("tool_input") or {}).get("file_path") or ""

    # A guarded document, once edited with the owner's ok, is not re-flagged for
    # the rest of the session -- guard_edit reads this back.
    norm = path.replace("\\", "/")
    if any(p in norm for p in config.get("guarded_paths") or []):
        _remember_guarded(payload.get("session_id") or "", norm)

    command = config.get("lint")
    if not command:
        return 0
    if not any(path.endswith(s) for s in config.get("lint_suffixes") or []):
        return 0

    STATE.mkdir(parents=True, exist_ok=True)
    _flag("code-edited").touch()

    filled = [sys.executable if a == "{python}" else a.replace("{file}", path)
              for a in command]
    try:
        lint = subprocess.run(filled, cwd=_project_dir(), capture_output=True, text=True,
                               check=False, timeout=LINT_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        print("lint timed out after " + str(LINT_TIMEOUT_SECONDS) + "s: " + " ".join(filled),
              file=sys.stderr)
        return 2
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

    try:
        run = subprocess.run(filled, cwd=_project_dir(), capture_output=True, text=True,
                              check=False, timeout=VERIFY_TIMEOUT_SECONDS)
        output = run.stdout + run.stderr
        passed = run.returncode == 0
    except subprocess.TimeoutExpired as timeout:
        output = ((timeout.stdout or "") + (timeout.stderr or "")
                  + "\n[verify timed out after " + str(VERIFY_TIMEOUT_SECONDS) + "s]")
        passed = False
    STATE.mkdir(parents=True, exist_ok=True)
    _flag("last-verify.log").write_text(output)
    return passed, output


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
            _notify_push(_project_dir().name, "Turn finished", event="done",
                         tags="white_check_mark")
        return 0

    _flag("code-edited").unlink()
    passed, _ = result
    _play_once("pass" if passed else "fail")
    _speak("Verification passed" if passed else "Verification failed")
    _notify_push(_project_dir().name,
                 "Verification passed" if passed else "Verification FAILED",
                 event="pass" if passed else "fail",
                 priority="default" if passed else "high")
    print(json.dumps({"systemMessage": (
        "Verification: ALL LAYERS PASS" if passed else
        "Verification: SOME LAYERS FAILED -- see ~/.claude/hooks/state/last-verify.log"
    )}))
    return 0


_SEGMENTS = re.compile(r"&&|\|\||;|\|")

# git global flags that take their value as a separate following token (as
# opposed to `--git-dir=x`, which is self-contained) -- these have to be
# walked past, not mistaken for the subcommand.
_GIT_VALUE_FLAGS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def _is_commit(command):
    """True when the command really runs `git commit`, however it is dressed up.

    Looking for the literal "git commit" misses `git -c user.name=... commit`,
    which is how a commit is usually made from a script; looking for both words
    anywhere in a segment matches `git log --grep=commit` or `git diff --
    commit.py`, which run verification (and can hang on it) despite never
    committing anything. Split on shell separators, tokenize each segment, and
    walk past git's global flags to check whether the actual subcommand is
    "commit".
    """
    for part in _SEGMENTS.split(command):
        try:
            tokens = shlex.split(part)
        except ValueError:
            continue  # unbalanced quoting (e.g. a message split across a separator)
        for i, token in enumerate(tokens):
            if token != "git" and not token.endswith("/git"):
                continue
            rest = tokens[i + 1:]
            j = 0
            while j < len(rest) and rest[j].startswith("-"):
                if rest[j] in _GIT_VALUE_FLAGS and "=" not in rest[j]:
                    j += 1  # skip this flag's separate value too
                j += 1
            if j < len(rest) and rest[j] == "commit":
                return True
    return False


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
    _notify_push(_project_dir().name + " commit blocked",
                 "Verification is red; nothing was committed",
                 event="fail", priority="high")
    failed = [line.strip() for line in output.splitlines() if ": FAIL" in line]
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Verification is red, so nothing was committed: "
            + "; ".join(failed or ["see ~/.claude/hooks/state/last-verify.log"])
            + ". Fix it first, or commit by hand if this is deliberate."
        ),
    }}))
    return 0


def compacting():
    """Compaction means the session has grown expensive; say so out loud."""
    _play_once("compacting")
    _notify_push(_project_dir().name, "Session compacting -- it has grown long",
                 event="compacting", priority="low")
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
            + "; ".join(failed or ["see ~/.claude/hooks/state/last-verify.log"]))
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
                   "python notify.py commit-gate", "git log --grep=commit",
                   "git diff -- commit.py", "git branch commit-fix"]
    for command in commits:
        assert _is_commit(command), "should gate: " + command
    for command in not_commits:
        assert not _is_commit(command), "should not gate: " + command
    missing = [name for name, path in SOUNDS.items() if not path.is_file()]
    durations = ", ".join(f"{name} {_sound_seconds(path):.2f}s"
                          for name, path in SOUNDS.items() if path.is_file())
    print("commit detection: " + str(len(commits) + len(not_commits)) + " cases pass")
    print("sounds missing: " + (", ".join(missing) if missing else "none"))
    print("sound durations: " + (durations or "none"))
    print("player: " + str(_player()))
    config = _config()
    channels = [name for name in ("local", "ntfy", "pushover")
                if config.get(name) and (name != "pushover"
                                         or config["pushover"].get("token"))]
    print("push channels: " + (", ".join(channels) if channels else "none"))
    print("bash for verification: " + str(_bash()))
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
}


def main():
    return COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 -- a hook must never take the session down with it
        sys.exit(0)

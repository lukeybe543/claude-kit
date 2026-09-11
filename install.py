"""Install (or update) claude-kit into this machine's ~/.claude.

    python3 install.py              # install / update from this checkout (copies)
    python3 install.py --link       # symlink instead of copy -- see below
    python3 install.py --pull       # git pull this checkout first, then install
    python3 install.py --desktop    # also set up the desk-listener systemd service

Everything is machine-global: the notification hooks, the skills and the agents
land in ~/.claude and apply to every project and every session. Re-run any time
to pick up changes — it is idempotent and never overwrites a file you are meant
to edit (~/.claude/CLAUDE.md, ~/.claude/hooks/notify.json). Per-project
scaffolding is a separate script, adopt.py.

--link makes ~/.claude/hooks, ~/.claude/skills and ~/.claude/agents symlinks
into this checkout instead of copies of it. A copy install means an edit made
against the live ~/.claude files and an edit made in this checkout are two
different files that only agree right after the next install run -- --link
makes them the same file, so a hook edited in any session is live everywhere
immediately, and shipping it is just `git commit && git push` from here. Any
machine-specific file a prior copy-install left behind (notify.json,
notify.local.json, hooks/state/) is folded into the checkout, gitignored
there, before the symlink replaces the copy.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAUDE = Path.home() / ".claude"
NOTIFY = CLAUDE / "hooks" / "notify.py"


def _copy_tree(src, dst, report, overwrite=True):
    dst.mkdir(parents=True, exist_ok=True)
    for item in sorted(src.iterdir()):
        if item.name == "__pycache__":
            continue
        target = dst / item.name
        if item.is_dir():
            _copy_tree(item, target, report, overwrite)
        elif overwrite or not target.exists():
            shutil.copy2(item, target)
            report.append("wrote   " + str(target.relative_to(Path.home())))
        else:
            report.append("kept    " + str(target.relative_to(Path.home())))


def _link_tree(src, dst, report):
    """Symlink dst -> src, folding in any machine-specific file a prior
    copy-install left in dst that src does not already have."""
    if dst.is_symlink():
        if dst.resolve() == src.resolve():
            report.append("kept    " + str(dst.relative_to(Path.home())) + " (already linked)")
            return
        dst.unlink()
    elif dst.exists():
        for item in dst.rglob("*"):
            if item.is_dir() or item.name == "__pycache__":
                continue
            target = src / item.relative_to(dst)
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item), str(target))
                report.append("kept    " + str(target.relative_to(Path.home()))
                              + " (moved from the copy-install)")
        shutil.rmtree(dst)
    dst.symlink_to(src, target_is_directory=True)
    report.append("linked  " + str(dst.relative_to(Path.home())) + " -> " + str(src))


def _install_files(report, link=False):
    tree = _link_tree if link else _copy_tree
    tree(HERE / "hooks", CLAUDE / "hooks", report)
    for group in ("skills", "agents"):
        tree(HERE / group, CLAUDE / group, report)
    example = CLAUDE / "hooks" / "notify.json.example"
    default = CLAUDE / "hooks" / "notify.json"
    if example.exists() and not default.exists():
        shutil.copy2(example, default)
        report.append("wrote   " + str(default.relative_to(Path.home())))
    (CLAUDE / "hooks" / "state").mkdir(parents=True, exist_ok=True)


def _install_claude_md(report):
    src, dst = HERE / "global" / "CLAUDE.md", CLAUDE / "CLAUDE.md"
    if not dst.exists():
        shutil.copy2(src, dst)
        report.append("wrote   .claude/CLAUDE.md")
        return
    if dst.read_text() == src.read_text():
        report.append("kept    .claude/CLAUDE.md (already current)")
        return
    report.append("SKIPPED .claude/CLAUDE.md -- one already exists and differs.")
    report.append("        Review the diff and merge by hand:")
    report.append("          diff ~/.claude/CLAUDE.md " + str(src))


def _merge_settings(report):
    """Wire the notify hooks into ~/.claude/settings.json. Nothing else is
    touched -- permissions stay a per-project concern (see adopt.py)."""
    path = CLAUDE / "settings.json"
    try:
        settings = json.loads(path.read_text())
    except (OSError, ValueError):
        settings = {}

    hooks_template = (HERE / "global" / "settings-hooks.json").read_text()
    wanted = json.loads(hooks_template.replace("__NOTIFY__", str(NOTIFY)))["hooks"]
    existing = settings.setdefault("hooks", {})

    def _is_notify_group(group):
        hs = group.get("hooks") or []
        return bool(hs) and all("notify.py" in h.get("command", "") for h in hs)

    for event, groups in wanted.items():
        current = existing.setdefault(event, [])
        current[:] = [g for g in current if not _is_notify_group(g)] + list(groups)

    path.write_text(json.dumps(settings, indent=2) + "\n")
    report.append("merged  .claude/settings.json (10 notify hook groups re-wired)")


def _install_desktop(report):
    unit_src = CLAUDE / "hooks" / "desk-listener" / "desk-listener.service"
    unit_dst = Path.home() / ".config" / "systemd" / "user" / "desk-listener.service"
    unit_dst.parent.mkdir(parents=True, exist_ok=True)
    listener = CLAUDE / "hooks" / "desk-listener" / "listener.py"
    text = unit_src.read_text()
    # point ExecStart at the installed listener, whatever the template said
    lines = []
    for line in text.splitlines():
        if line.startswith("ExecStart="):
            line = "ExecStart=/usr/bin/python3 " + str(listener)
        lines.append(line)
    unit_dst.write_text("\n".join(lines) + "\n")
    report.append("wrote   " + str(unit_dst.relative_to(Path.home())))
    for cmd in (["systemctl", "--user", "daemon-reload"],
                ["systemctl", "--user", "enable", "--now", "desk-listener"]):
        subprocess.run(cmd, check=False)
    report.append("        systemctl --user enable --now desk-listener")
    report.append("        (firewall: allow tcp/19191 on the tailnet zone; "
                  "loginctl enable-linger to survive logout)")


def main():
    flags = set(sys.argv[1:])
    if "--pull" in flags:
        subprocess.run(["git", "-C", str(HERE), "pull", "--ff-only"], check=False)

    report = []
    _install_files(report, link="--link" in flags)
    _install_claude_md(report)
    _merge_settings(report)
    if "--desktop" in flags:
        _install_desktop(report)

    print("\n".join(report))
    if "--link" in flags:
        print("\nDone. Open /hooks in a running session once so Claude Code reloads "
              "settings.\n~/.claude/hooks, skills and agents are now this checkout -- "
              "edit here and every session sees it immediately.\nShip a change with: "
              "git -C " + str(HERE) + " commit && git -C " + str(HERE) + " push")
    else:
        print("\nDone. Open /hooks in a running session once so Claude Code reloads "
              "settings.\nUpdate later with:  git -C " + str(HERE)
              + " pull && python3 " + str(HERE / "install.py"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

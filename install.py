"""Set a project up with these hooks and this governance.

    python install.py /path/to/project
    python install.py /path/to/project --hooks        # sounds and checks only
    python install.py /path/to/project --governance   # docs, skills, commands, permissions

Nothing already in the project is overwritten except `notify.py` itself, which is code and
is versioned here. Anything you are meant to edit -- the config, CLAUDE.md, the tier
registry, the skills -- is written once and then left alone, so re-running this to pick up
a fix never costs you your own edits. Permission rules are merged, never removed.
"""

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_IGNORE = ".claude/state/"
LOCAL_IGNORE = ".claude/hooks/notify.local.json"


def _copy(source, destination, overwrite, report):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        report.append("kept    " + str(destination) + " (already there)")
        return
    shutil.copy2(source, destination)
    report.append("wrote   " + str(destination))


def _settings(target):
    path = target / ".claude" / "settings.json"
    try:
        return path, json.loads(path.read_text())
    except (OSError, ValueError):
        return path, {}


def _save(path, settings):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n")


def _install_hooks(target, report):
    hooks = target / ".claude" / "hooks"
    for name in ("notify.py", "README.md", "RECREATE-ON-LINUX.md"):
        _copy(HERE / "hooks" / name, hooks / name, True, report)
    _copy(HERE / "hooks" / "notify.json.example", hooks / "notify.json", False, report)
    _copy(HERE / "hooks" / "sounds" / "generate.py",
          hooks / "sounds" / "generate.py", True, report)
    for wav in sorted((HERE / "hooks" / "sounds").glob("*.wav")):
        _copy(wav, hooks / "sounds" / wav.name, True, report)
    for source in sorted((HERE / "hooks" / "desk-listener").iterdir()):
        _copy(source, hooks / "desk-listener" / source.name, True, report)

    path, settings = _settings(target)
    wanted = json.loads((HERE / "hooks" / "settings-hooks.json").read_text())["hooks"]
    existing = settings.setdefault("hooks", {})
    added = 0
    for event, groups in wanted.items():
        for group in groups:
            if group not in existing.setdefault(event, []):
                existing[event].append(group)
                added += 1
    _save(path, settings)
    report.append("merged  " + str(added) + " hook group(s) into " + str(path))

    ignore = target / ".gitignore"
    text = ignore.read_text() if ignore.exists() else ""
    missing = [line for line in (STATE_IGNORE, LOCAL_IGNORE) if line not in text]
    if missing:
        prefix = "" if text.endswith("\n") or not text else "\n"
        ignore.write_text(text + prefix + "\n# Claude hooks: scratch state and "
                          "per-machine config (the ntfy URL).\n" + "\n".join(missing)
                          + "\n")
        report.append("wrote   " + str(ignore) + " (ignoring " + ", ".join(missing) + ")")


def _install_permissions(target, report):
    """Add permission rules that are not already there. Never removes one."""
    baseline = json.loads((HERE / "governance" / "permissions.json").read_text())
    path, settings = _settings(target)
    permissions = settings.setdefault("permissions", {})
    added = 0
    for kind, rules in baseline["permissions"].items():
        if kind == "defaultMode":
            if "defaultMode" not in permissions:
                permissions["defaultMode"] = rules
                report.append("set     permissions.defaultMode = " + rules)
            continue
        current = permissions.setdefault(kind, [])
        for rule in rules:
            if rule not in current:
                current.append(rule)
                added += 1
    _save(path, settings)
    report.append("merged  " + str(added) + " permission rule(s) into " + str(path))


def _install_governance(target, report):
    _copy(HERE / "governance" / "CLAUDE.md", target / "CLAUDE.md", False, report)
    _copy(HERE / "governance" / "tiers.md", target / "docs" / "tiers.md", False, report)
    for skill in sorted((HERE / "skills").iterdir()):
        _copy(skill / "SKILL.md",
              target / ".claude" / "skills" / skill.name / "SKILL.md", False, report)
    for command in sorted((HERE / "commands").glob("*.md")):
        _copy(command, target / ".claude" / "commands" / command.name, False, report)
    for agent in sorted((HERE / "agents").glob("*.md")):
        _copy(agent, target / ".claude" / "agents" / agent.name, False, report)
    _install_permissions(target, report)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    target = Path(sys.argv[1]).expanduser().resolve()
    if not target.is_dir():
        print("Not a directory: " + str(target))
        return 1
    flags = set(sys.argv[2:])

    report = []
    if "--governance" not in flags:
        _install_hooks(target, report)
    if "--hooks" not in flags:
        _install_governance(target, report)

    print("\n".join(report))
    print("\nNext:")
    print("  1. Point .claude/hooks/notify.json at this project's lint and test commands,")
    print("     and list the document folders to guard in guarded_paths.")
    print("  2. Run /charter to fill in docs/tiers.md by interview, before writing code.")
    print("  3. Fill in .claude/commands/check.md with this project's own check commands.")
    print("  4. Open /hooks once so Claude Code picks up the new settings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

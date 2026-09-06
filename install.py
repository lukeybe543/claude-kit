"""Set a project up with these hooks and this governance.

    python install.py /path/to/project
    python install.py /path/to/project --hooks        # sounds and checks only
    python install.py /path/to/project --governance   # CLAUDE.md, tiers, skills only

Nothing already in the project is overwritten except `notify.py` itself, which is code and
is versioned here. Anything you are meant to edit -- the config, CLAUDE.md, the tier
registry, the skills -- is written once and then left alone, so re-running this to pick up
a fix never costs you your own edits.
"""

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_IGNORE = ".claude/state/"


def _copy(source, destination, overwrite, report):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        report.append("kept    " + str(destination) + " (already there)")
        return
    shutil.copy2(source, destination)
    report.append("wrote   " + str(destination))


def _install_hooks(target, report):
    hooks = target / ".claude" / "hooks"
    _copy(HERE / "hooks" / "notify.py", hooks / "notify.py", True, report)
    _copy(HERE / "hooks" / "README.md", hooks / "README.md", True, report)
    _copy(HERE / "hooks" / "RECREATE-ON-LINUX.md",
          hooks / "RECREATE-ON-LINUX.md", True, report)
    _copy(HERE / "hooks" / "notify.json.example", hooks / "notify.json", False, report)

    settings_path = target / ".claude" / "settings.json"
    try:
        settings = json.loads(settings_path.read_text())
    except (OSError, ValueError):
        settings = {}
    wanted = json.loads((HERE / "hooks" / "settings-hooks.json").read_text())["hooks"]
    existing = settings.setdefault("hooks", {})
    added = 0
    for event, groups in wanted.items():
        for group in groups:
            if group not in existing.setdefault(event, []):
                existing[event].append(group)
                added += 1
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n")
    report.append("merged  " + str(added) + " hook group(s) into " + str(settings_path))

    ignore = target / ".gitignore"
    text = ignore.read_text() if ignore.exists() else ""
    if STATE_IGNORE not in text:
        prefix = "" if text.endswith("\n") or not text else "\n"
        ignore.write_text(text + prefix + "\n# Scratch state kept by the Claude hooks.\n"
                          + STATE_IGNORE + "\n")
        report.append("wrote   " + str(ignore) + " (ignoring " + STATE_IGNORE + ")")


def _install_governance(target, report):
    _copy(HERE / "governance" / "CLAUDE.md", target / "CLAUDE.md", False, report)
    _copy(HERE / "governance" / "tiers.md", target / "docs" / "tiers.md", False, report)
    for skill in sorted((HERE / "skills").iterdir()):
        _copy(skill / "SKILL.md",
              target / ".claude" / "skills" / skill.name / "SKILL.md", False, report)


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
    print("  1. Point .claude/hooks/notify.json at this project's lint and test commands.")
    print("  2. Run /charter to fill in docs/tiers.md by interview, before writing code.")
    print("  3. Open /hooks once so Claude Code picks up the new settings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

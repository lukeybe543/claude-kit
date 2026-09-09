"""Scaffold the claude-kit docs method into one project.

    python3 adopt.py /path/to/project

Writes the decision-register / charter / glossary templates, a project CLAUDE.md
stub, and an optional per-project notify.json. It **only ever creates files** —
an existing CLAUDE.md, or an existing docs file, is left untouched and the diff
is printed for the owner to merge by hand. The hooks and skills are machine-
global (install.py); this does not touch them.

Then: fill the templates in, or run /charter, before writing code.
"""

import datetime
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TPL = HERE / "project-template"


def _place(src, dst, subs, report):
    if dst.exists():
        if dst.read_text() == _render(src, subs):
            report.append("kept    " + dst.name + " (already current)")
        else:
            report.append("SKIPPED " + str(dst) + " -- exists and differs. Merge by hand:")
            report.append("          diff '" + str(dst) + "' '" + str(src) + "'")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(_render(src, subs))
    report.append("wrote   " + str(dst))


def _render(src, subs):
    text = src.read_text()
    for key, value in subs.items():
        text = text.replace(key, value)
    return text


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    project = Path(sys.argv[1]).expanduser().resolve()
    if not project.is_dir():
        print("Not a directory: " + str(project))
        return 1

    subs = {"<project>": project.name,
            "<date>": datetime.date.today().isoformat()}
    report = []
    _place(TPL / "CLAUDE.md", project / "CLAUDE.md", subs, report)
    for doc in ("charter.md", "decisions.md", "glossary.md"):
        _place(TPL / "docs" / doc, project / "docs" / doc, subs, report)
    _place(TPL / ".claude" / "notify.json", project / ".claude" / "notify.json", subs, report)
    _place(TPL / ".claude" / "settings.json", project / ".claude" / "settings.json",
           subs, report)
    _place(HERE / "commands" / "check.md", project / ".claude" / "commands" / "check.md",
           subs, report)

    print("\n".join(report))
    print("\nNext: fill the templates in (or run /charter), and point "
          + str(project / ".claude" / "commands" / "check.md") + " at this "
          "project's own check command.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

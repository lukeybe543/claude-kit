#!/bin/bash
# bootstrap.sh — one-shot setup: machine-global install + project scaffold.
#
# Usage:
#   ./bootstrap.sh /path/to/project
#
# Runs install.py (writes ~/.claude/hooks, skills, agents, CLAUDE.md — once
# per machine) then adopt.py (scaffolds design.md/plan.md/README.md, docs/,
# CLAUDE.md into the project — create-only, never overwrites). Both write
# real files, not links: nothing afterward depends on where this checkout
# of claude-kit lives, so once this finishes the clone can be deleted.
#
#   git clone --depth 1 https://github.com/lukeybe543/claude-kit /tmp/ck
#   /tmp/ck/bootstrap.sh ~/myproject
#   rm -rf /tmp/ck
#
# To update later: re-clone (or git pull an existing checkout) and re-run —
# both scripts are idempotent.

set -eu

if [ $# -ne 1 ]; then
    echo "Usage: bootstrap.sh /path/to/project"
    exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$1"   # adopt.py requires the target to already exist

python3 "$HERE/install.py"
python3 "$HERE/adopt.py" "$1"

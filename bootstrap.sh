#!/bin/bash
# bootstrap.sh — Set up a new project with claude-kit templates and hooks
#
# Usage:
#   ./bootstrap.sh /path/to/new/project
#   OR from new project: /path/to/claude-kit/bootstrap.sh .
#
# This script:
# 1. Copies .claude/ (notify.json, settings.json, hooks reference)
# 2. Copies the master docs (design.md, plan.md, README.md)
# 3. Copies docs/ derived-doc templates (charter.md, decisions.md, glossary.md)
# 4. Copies CLAUDE.md stub
# 5. Creates a symlink to claude-kit for easy hook/skill access
# All paths remain relative so the project works anywhere.

set -eu

if [ $# -ne 1 ]; then
    echo "Usage: bootstrap.sh /path/to/project"
    echo ""
    echo "Scaffolds a new project with claude-kit templates."
    echo "Run this from the claude-kit repo, or invoke it with a target path."
    exit 1
fi

TARGET="${1%/}"  # Remove trailing slash
BOOTSTRAP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="$(basename "$TARGET")"
TPL="$BOOTSTRAP_ROOT/project-template"

# Verify source exists
if [ ! -d "$TPL" ]; then
    echo "Error: project-template not found at $TPL"
    exit 1
fi

# Create or verify target is a directory
if [ ! -d "$TARGET" ]; then
    mkdir -p "$TARGET"
    echo "Created: $TARGET"
fi

echo "Bootstrapping $PROJECT_NAME..."

# Helper to copy file if not exists, warn if it differs
copy_file() {
    local src="$1"
    local dst="$2"
    local name="$(basename "$dst")"

    if [ ! -f "$dst" ]; then
        mkdir -p "$(dirname "$dst")"
        cp "$src" "$dst"
        echo "  ✓ Created $name"
    elif diff -q "$src" "$dst" > /dev/null 2>&1; then
        echo "  ✓ Kept    $name (already current)"
    else
        echo "  ⚠ SKIPPED $name (exists and differs; merge by hand)"
        echo "    diff '$dst' '$src'"
    fi
}

# Copy .claude/ config
echo "Setting up .claude/"
mkdir -p "$TARGET/.claude"
copy_file "$TPL/.claude/notify.json" "$TARGET/.claude/notify.json"
copy_file "$TPL/.claude/settings.json" "$TARGET/.claude/settings.json"

# Copy master docs + CLAUDE.md stub
echo "Setting up project files"
copy_file "$TPL/CLAUDE.md" "$TARGET/CLAUDE.md"
for doc in design.md plan.md README.md; do
    copy_file "$TPL/$doc" "$TARGET/$doc"
done

# Copy derived-doc templates
echo "Setting up docs/"
for doc in charter.md decisions.md glossary.md; do
    copy_file "$TPL/docs/$doc" "$TARGET/docs/$doc"
done

# Create symlink to claude-kit (for hook/skill access)
# This uses relative paths so it works regardless of where the project lives
# The symlink is in .claude/, so we calculate relative to that directory
RELATIVE_KIT=$(python3 -c "
import os
from pathlib import Path
claude_dir = Path('$TARGET/.claude').resolve()
kit = Path('$BOOTSTRAP_ROOT').resolve()
print(os.path.relpath(kit, claude_dir))
")

if [ ! -e "$TARGET/.claude/kit" ]; then
    ln -s "$RELATIVE_KIT" "$TARGET/.claude/kit"
    echo "  ✓ Linked  .claude/kit → $RELATIVE_KIT"
else
    echo "  ✓ Kept    .claude/kit (already exists)"
fi

# Create .claude/commands directory and check.md template
echo "Setting up .claude/commands"
copy_file "$BOOTSTRAP_ROOT/commands/check.md" "$TARGET/.claude/commands/check.md"

echo ""
echo "✓ Bootstrap complete!"
echo ""
echo "Next steps:"
echo "  1. Fill in design.md (architecture, source of truth) and plan.md (sequencing)"
echo "  2. Edit $TARGET/CLAUDE.md with project-specific rules — see design.md/plan.md pointer"
echo "  3. Fill in docs/charter.md, docs/decisions.md, docs/glossary.md (or run /charter)"
echo "  4. Update .claude/commands/check.md to point to your test/lint commands"
echo ""
echo "To use hooks & skills:"
echo "  - Hooks: ln -s .claude/kit/hooks/notify.py ~/.claude/hooks/notify.py (machine-global)"
echo "  - Skills: ln -s .claude/kit/skills ~/.claude/skills (or symlink individually)"
echo ""

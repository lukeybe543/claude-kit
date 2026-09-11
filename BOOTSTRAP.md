# Using claude-kit as a Template

This guide explains how to bootstrap new projects with claude-kit's templates, hooks, and docs system.

## Quick Start

```bash
# Clone claude-kit into ~/.claude (machine-global setup)
git clone https://github.com/lukeybe543/claude-kit ~/.claude/claude-kit
python3 ~/.claude/claude-kit/install.py

# Bootstrap a new project
/home/user/path/to/claude-kit/bootstrap.sh /path/to/new/project
cd /path/to/new/project
git init
```

## What the Bootstrap Does

The `bootstrap.sh` script sets up a new project with:

### 1. `.claude/` Directory
```
.claude/
├── notify.json       # Project-specific hook configs (merged with global)
├── settings.json     # Project-specific permission baseline
├── commands/
│   └── check.md      # Template for your project's verification script
└── kit → ../../claude-kit  # Symlink to claude-kit (relative path)
```

### 2. Documentation Templates
```
docs/
├── charter.md       # How to read the decision register
├── decisions.md     # Your project's decision log
└── glossary.md      # Project vocabulary & terminology
```

### 3. Project CLAUDE.md
A stub that references the global rules and fills in project-specific info:
- What the project does
- How to verify changes
- Environment gotchas
- Key decisions already made

## Your Workflow

### Machine Setup (once per machine)

```bash
# Install machine-global hooks, skills, and agents
git clone https://github.com/lukeybe543/claude-kit ~/.claude/claude-kit
python3 ~/.claude/claude-kit/install.py

# Update any time:
git -C ~/.claude/claude-kit pull && python3 ~/.claude/claude-kit/install.py
```

This gives every project access to:
- **Hooks**: notification sounds, lint-on-edit, verification
- **Skills**: /charter, /decisions, /glossary, and 7 others
- **Agents**: reviewer, scout

### New Project Setup

```bash
# Using the bootstrap script:
~/.claude/claude-kit/bootstrap.sh /path/to/myproject

# Then:
cd /path/to/myproject
git init
# Fill in docs templates or run /charter
# Point .claude/commands/check.md at your project's test/lint commands
```

**Or** use adopt.py from any existing project:

```bash
python3 ~/.claude/claude-kit/adopt.py /path/to/myproject
```

Both do the same scaffolding; bootstrap.sh also creates the `.claude/kit` symlink.

## Sharing Changes Back to claude-kit

After improving claude-kit in your projects:

```bash
# From your project:
git diff .claude/

# From claude-kit:
cp -r /path/to/project/.claude/notify.json ~/.claude/claude-kit/project-template/.claude/
git -C ~/.claude/claude-kit commit -am "Update from project X"
git -C ~/.claude/claude-kit push
```

Or use `before94`'s `.claude/` copy as the true source if you're still maintaining it.

## Project-Specific Hooks

Create `.claude/notify.json` to configure behavior for just this project:

```json
{
  "lint": ["python3", "{python}", "-m", "mypy", "{file}"],
  "lint_suffixes": [".py"],
  "verify": ["pytest", "-q"],
  "guarded_paths": ["setup.py", "pyproject.toml"],
  "guarded_text": ["VERSION = "]
}
```

Keys:
- **lint** — Run on each file written (exit non-zero refuses the write)
- **lint_suffixes** — Which files to lint
- **verify** — Full check before commits (runs on code change)
- **guarded_paths** — First edit prompts for permission
- **guarded_text** — Edit containing this text prompts for permission

## Hearing Notifications from Headless Boxes

If you develop on a remote droplet but sit at a workstation:

1. On your workstation, run install.py with `--desktop`:
   ```bash
   python3 ~/.claude/claude-kit/install.py --desktop
   ```

2. On the droplet, create `~/.claude/hooks/notify.local.json`:
   ```json
   {
     "local": "http://<workstation-tailnet-ip>:19191"
   }
   ```

Events will play on your speakers over the network.

## Files in This Repo

```
bootstrap.sh              ← Use this to scaffold new projects
BOOTSTRAP.md              ← You are here
install.py                → Machine-global setup (copies hooks/skills/agents)
adopt.py                  → Alternative per-project scaffold
METHOD.md                 → The full docs method philosophy
CLAUDE.md                 → Project instructions (working on claude-kit itself)

hooks/
  notify.py               → The notification hook (installed to ~/.claude/hooks)
  notify.json.example     → Example project overrides
  sounds/                 → WAV files (bundled, deterministic)
  desk-listener/          → Network sound relay for headless boxes

skills/                   → Doc-writing skills (→ ~/.claude/skills)
  charter/SKILL.md        → Review the charter
  decisions/SKILL.md      → Add a decision
  glossary/SKILL.md       → Add a term
  (7 more)

global/
  CLAUDE.md               → → ~/.claude/CLAUDE.md (global rules)
  settings-hooks.json     → Merged into ~/.claude/settings.json

project-template/
  CLAUDE.md               → Scaffolded into new projects
  .claude/notify.json     → Per-project hook defaults
  .claude/settings.json   → Per-project permission baseline
  docs/                   → Template docs

commands/
  check.md                → Template for /check command
```

## Troubleshooting

### `.claude/kit` symlink is broken
The bootstrap script creates a relative symlink. If it breaks:

```bash
cd /path/to/project
rm .claude/kit
ln -s ../../path/to/claude-kit .claude/kit
```

### Hooks don't work in new project
Hooks are machine-global. After boostrapping, they're available everywhere:

```bash
# From your workstation ~/.claude/hooks/notify.py
# Or ~/.claude/skills for doc skills
```

### CLAUDE.md already exists and differs
bootstrap.sh will warn and print a diff. Merge by hand:

```bash
diff /path/to/project/CLAUDE.md ~/.claude/claude-kit/project-template/CLAUDE.md
```

Then edit and keep what you need.

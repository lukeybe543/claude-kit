# claude-kit

Two things I keep rebuilding at the start of every project, packaged so the next one
starts with them: **a session you can hear**, and **a way of deciding who decides**.

```
python install.py /path/to/new-project
```

---

## Why

Both halves came out of the same project and the same two frustrations.

**You cannot tell when Claude needs you.** The built-in notification is easy to miss, so
you either sit watching a spinner or wander off and lose twenty minutes to a permission
prompt that has been waiting the whole time.

**Blunt phrasing becomes a requirement you never meant.** A designer says "never re-encode
the file" meaning *this matters a lot*. The assistant encodes it as a hard constraint,
builds an interface and a test suite around it, and months later the requirement turns out
to have been emphasis. Unpicking it costs hours. The same thing happens with "must",
"always" and "only", and it happens most where the designer knows least — because that is
exactly where a passing remark is least likely to be examined.

## The hooks — `hooks/`

Claude Code hooks that make a session audible, and use the same wiring to check work as it
happens.

| When | What happens |
| :--- | :--- |
| Claude needs permission or an answer | Rings; **stops the moment you act**. Unanswered, it comes back a minute later, three rounds, then gives up |
| A turn ends after 45s+ of work | A soft ding — short turns stay silent on purpose |
| A source file is written | Lints just that file; a violation goes straight back to Claude |
| Code changed this turn | Runs the test command in the background, then chimes or errors |
| A commit is about to be made | Runs the tests first, and refuses the commit if they are red |
| An edit touches reserved text | Becomes a permission prompt instead of just happening |
| The session is about to compact | A distinct sound — it has grown expensive |
| A session starts | Says so if the last test run left the tree red |

Everything project-specific lives in `.claude/hooks/notify.json`; an empty key turns that
behaviour off, so a project with no test suite just gets the sounds.

```json
{
  "lint": ["{python}", "-m", "ruff", "check", "{file}"],
  "lint_suffixes": [".py"],
  "verify": ["bash", "run_tests.sh"],
  "guarded_text": ["RULE_VERSION"]
}
```

**Platforms.** The backend is chosen from `sys.platform` at runtime. Windows uses
`winsound` and the stock sounds in `%SystemRoot%\Media`. Linux uses the freedesktop theme
through `paplay`/`pw-play`/`aplay`, falling back to `canberra-gtk-play`, and **also speaks
results** through `spd-say` or `espeak-ng`. On Fedora:
`sudo dnf install sound-theme-freedesktop pipewire-utils speech-dispatcher`.

Speech is deliberately absent on Windows: PowerShell there may run in ConstrainedLanguage
mode with Windows Script Host blocked by policy, which shuts both SAPI routes. Distinct
sounds stand in for words.

`hooks/RECREATE-ON-LINUX.md` is a prompt that rebuilds the whole thing from a description,
for when copying files is not an option.

## The governance — `governance/` and `skills/`

A way of writing down **which instructions are settled and which are arguable**, so that
pushback lands where it helps.

- **`governance/CLAUDE.md`** — behavioural rules: clarify before building, keep it simple,
  change only what was asked, verify rather than claim. Plus the three sections that carry
  the real lesson: whose decision is it, absolutes are suspect until confirmed, and audit
  early while document rewrites are still cheap.
- **`governance/tiers.md`** — the registry. Tier 1 is settled and not to be argued. Tier 2
  is advisory: push back once, before building, with evidence. **Unassigned is Tier 1, and
  the assistant may only ever *propose* a tier, never assign one** — without that rule,
  *"that's just an implementation detail"* becomes a way to overrule a real decision.
CLAUDE.md also carries four rules about *how the work runs*: replies stay short (§8, and
it is a context cost, not just a courtesy); the model is matched to the task (§9); code is
written in loops while documents get questions first (§10); and tangents are parked rather
than followed or dropped (§11).

## The skills — `skills/`

Split the way Matt Pocock splits his: **user-invoked** ones orchestrate, **model-invoked**
ones are disciplines the model reaches for on its own.

| Skill | | What it does |
| :--- | :--- | :--- |
| `charter` | user | The start-of-project interview that fills the tier registry. Interviews rather than drafting — a list the owner did not build is a list they have not agreed to. |
| `audit-absolutes` | user | Finds every "must", "never", "always" and "only", and asks once, early, which are promises and which were emphasis. |
| `stress` | user | Presses a high-level design for practicality. Three verdicts, one of which is **build it and find out**. Reports; never edits. |
| `guard` | model | Proves a test actually bites, by breaking the thing minimally and watching it fail. Two hard-won lessons about tests that pass for the wrong reason. |
| `drift` | model | Finds claims in the docs that a change quietly made false. |
| `tangent` | model | Parks a thought raised mid-task, then asks which thread to pull. |

`commands/check.md` is a template for the project's own verification command.

`governance/permissions.json` is a settings baseline: safe, reversible commands run
without a prompt so code can be written in a loop; anything that installs, deletes,
changes permissions or reaches the network asks; destructive commands and credential files
are denied outright. `defaultMode` is `acceptEdits`, because file edits are covered by
tests and undone with `git`.

The load-bearing ideas, if you read nothing else:

> **The lower level serves the higher level.** Where a low-level rule and a high-level
> concept conflict, the rule yields.

> **A low-level rule that predates the structure it constrains is suspect by default, not
> settled by seniority.** That is grounds to open a question, never to answer one.

> **A mechanism that turns out to have a visible consequence becomes the owner's decision
> again.**

> Expect the common outcome: **the rule is sound and the reason written beneath it is
> wrong.** Testing a rule is not attacking it.

## Installing

```
python install.py /path/to/project              # everything
python install.py /path/to/project --hooks      # sounds and checks only
python install.py /path/to/project --governance # CLAUDE.md, tiers, skills only
```

Nothing already in the project is overwritten except `notify.py`, which is code and is
versioned here — so re-running it to pick up a fix never costs you your own config,
CLAUDE.md or tier registry. One caveat: the ring's tuning constants (`RING_REPEATS`,
`NOTIFY_ROUNDS`, `ROUND_GAP_SECONDS`) live at the top of `notify.py`, so re-installing
resets them. Change them here rather than downstream.

Then: point `notify.json` at the project's commands, run `/charter` before writing code,
and open `/hooks` once so Claude Code reloads its settings.

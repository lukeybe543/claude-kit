---
name: tangent
description: Park a thought that has come up mid-task without losing it or derailing the work. Records it, then asks whether to switch to it or carry on. Invoked by the user, and also used by the model whenever a message opens a topic the current task does not cover.
---

# Catching a tangent without dropping either thread

Some people think tangentially and cannot hold a thought until a convenient moment — the
thought has to come out now or it is gone. That is a working style, not a problem to be
managed, and the cost it creates is real but narrow: a thought arrives mid-task, and either
the work derails to chase it or the thought is lost.

Both losses are avoidable. Write it down, then ask.

## When the model should use this without being asked

Whenever a message opens something the current task does not cover. Signals:

- a **new subject** — a different file, feature, tool or concern than the one in hand
- a **question about something adjacent** — "could we also…", "what about…", "is there a
  way to…"
- an **aside inside a larger message** — a sentence that would be its own request if it
  stood alone
- a **recalled item** — "I've been meaning to ask", "also", "tangentially"

If the thought is one line and answering it costs one line, just answer it. This skill is
for the ones that would take real work.

## What to do

**1 · Record it before responding.** Append to `docs/tangents.md` (create it if absent):

```markdown
## <short title>
*Raised <date>, while <what we were doing>.*

<the thought, in the user's own words wherever possible — a paraphrase loses the point>

**Cost if pursued:** <a sentence — a small change, a session, or unknown>
```

Quoting matters. A tangent rewritten in your words is a tangent you have already started
interpreting.

**2 · Then ask, in one line.** Name both options and what is in flight:

> Parked that as *<title>*. Switch to it now, or finish <current task> first?

Do not decide it yourself, and do not silently continue. The whole point is that the user
sees the choice.

**3 · If they carry on, do not raise it again.** It is written down. Bringing it back
unprompted is a second interruption. Surface parked items when the current task finishes,
or when asked.

## Reviewing what is parked

On request, or when a task completes, list the open tangents shortest-first with their
cost estimate. Drop anything the work has since answered, and say what you dropped.

`docs/tangents.md` is a queue, not an archive. When a tangent is picked up, mark it done
with the date and where it went — a commit, a decision, an issue.

## What this is not

**Not a way to defer questions that block the work.** If the answer changes what you are
about to build, ask now and do not park it.

**Not a filing cabinet for your own ideas.** Only the user's tangents go here. Suggestions
you generated belong in the reply, where they can be ignored cheaply.

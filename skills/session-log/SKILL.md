---
name: session-log
description: Write down what a session actually learned before it is cleared — what worked, what was tried and failed, and what is still untried. Run at the end of a task, before /clear. The failures are the valuable half.
---

# Writing down what the session learned

A session ends and its context is thrown away. What survives is the code and the commit
messages, which record *what was decided* and almost never *what was tried and abandoned*.
So the next session repeats it.

That is not hypothetical. A guard in this kit was written three times, defeated three
different ways, and each attempt looked correct in the settings file. Nothing recorded the
first two failures, so the third was made in the same spirit as the first.

Run this when a task finishes, before `/clear`.

## Where it goes

`docs/sessions/YYYY-MM-DD-<short-slug>.md`. One file per session — never append to an old
one, because the point is that stale context does not leak into new work.

## The shape

```markdown
# <what the session was for>
*<date> · <the commits it produced, if any>*

## What worked
<Approaches that hold, each with the evidence that says so — a passing test, a
measurement, an observed behaviour. Not "we added X" but "X works, and here is how we
know".>

## What was tried and did not work
<The valuable half. Each one: what was attempted, what actually happened, and why it
failed. Include the things that looked correct and were not, and say what made them look
correct — that is what the next session needs in order not to repeat it.>

## What has not been tried
<Known unknowns and deferred work. What would settle each one.>

## Open questions for the owner
<Anything parked, unresolved, or awaiting a decision. Cross-reference docs/tangents.md.>
```

## Rules

**The failures are not optional.** A log with an empty "did not work" section is either a
session that learned nothing or, far more likely, a log written to look tidy. If an
approach was abandoned, it goes in — including the ones abandoned because they were
embarrassing.

**Evidence, not narration.** "The suite takes 29 seconds, measured" belongs here. "We
worked on the test suite" does not.

**Say what made a wrong thing look right.** A filter that matched nothing, a test that
passed for the wrong reason, a rule whose stated justification was false. This sentence is
the whole reason the file exists.

**Keep it short enough to be read.** If it runs past a page, it has become a transcript.
Cut the narration first.

**Do not write one for a session that produced nothing worth knowing.** An empty log is
noise, and noise trains people to skip the directory.

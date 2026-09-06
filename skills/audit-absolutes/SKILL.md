---
name: audit-absolutes
description: Find the absolutes in a specification — must, never, always, only, all — and establish which are binding promises and which were emphasis. Run early, before an unintended requirement has shaped the code.
---

# Audit the absolutes

A designer describing a system speaks in absolutes for emphasis. An assistant reading the
same sentence encodes it as a requirement, builds around it, and discovers much later that
the requirement was never meant. By then an interface, a schema and a test suite have been
shaped by it, and undoing it costs hours.

This audit is the cheap version of that discovery. Run it **early** — when a design
document is first written, when a document is substantially revised, and before starting a
milestone that will build on one.

## What to do

**1 · Collect.** Search the specification for `must`, `must not`, `never`, `always`,
`only`, `all`, `any`, `every`, `cannot`, `no <noun>`, `without exception`, and the
imperative negatives (`don't`, `do not`). Include the documents that carry requirements;
exclude test names, changelogs and anything already marked as settled with a reason.

**2 · Triage before asking.** Most hits are unremarkable. Sort them into three groups and
only bring the third to the owner:

- **Already settled** — the document says whether it is a promise or a means, or the tier
  registry already covers it. Leave it.
- **Structurally obvious** — an absolute that simply restates a named guarantee ("the file
  must remain readable"). Leave it.
- **Load-bearing but unexamined** — an absolute that *constrains implementation*, was
  written before the thing it constrains existed, or would be expensive to reverse later.
  These are the ones to ask about.

**3 · Ask in one batch, not one at a time.** A stream of individual questions is worse than
a single list. For each item give: the sentence, where it is, what it currently forces, and
what would become possible if it were a preference rather than a rule. Then ask the single
question that matters:

> Is this a **promise the program makes**, or a **strong preference about how it is
> currently done**?

**4 · Record the answer where the absolute lives.** Annotate the line itself — *binding
promise* or *current means* — and add a row to the tier registry if the answer establishes
authority over an area. The point of recording is that the question is asked **once**.

**5 · Report what changed.** Say which absolutes were confirmed, which were downgraded to
preferences, and what that now allows. If a downgrade opens an approach that was
previously blocked, name it.

## The rules this audit runs under

- **You may only ever propose.** Finding that an absolute is inconvenient is not a finding
  that it was unintended. Ask; do not reclassify. An absolute that is reaffirmed is
  binding and stays binding, and the correct response is to build it and say so.
- **Bring the consequence, not the objection.** "This forbids X, which means Y is
  impossible without Z" is useful. "This seems too strict" is not.
- **Expect the common outcome: the rule is sound and the reason written beneath it is
  wrong.** Testing a rule is not attacking it. Fixing a stale justification while
  confirming the rule is a good result, not a wasted audit.
- **Do not change code during the audit.** It produces questions and, once answered,
  document edits. Nothing else.

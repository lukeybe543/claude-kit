---
description: Run the full verification loop — tests and lint — and report the result.
allowed-tools: Bash
---

<!-- Template. Replace the two commands below with this project's own, and delete this
     comment. If the project has a single script that runs everything, name only that. -->

Run the verification loop and report the result.

```
./run_tests.sh
python -m ruff check .
```

Report:

- **Everything green** → say so in one line and stop. Do not summarise what passed; the
  point of the loop is the signal, not a report.
- **Anything red** → name the failing layer, quote the assertion, and say what it means.
  A failure in a guarantee-level check is more serious than a unit test: it means a
  promise broke, not that one function is wrong.

Do not fix anything unless asked. `/check` reports.

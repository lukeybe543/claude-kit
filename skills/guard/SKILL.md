---
name: guard
description: Prove a test actually guards what it claims. Use after writing or changing a test that asserts an invariant, a determinism property, or a project promise. Break the thing minimally, confirm the test fails, restore.
---

# Proving a guard bites

A passing test proves nothing about what it guards. It proves the code passes *today*. The
only evidence that a test would catch a regression is watching it **fail** when you cause
one.

Two minutes each. It pays for itself the first time a test turns out to have been green for
the wrong reason.

## When to run it

Every test asserting something the project *promises*, not merely something a function
returns:

- an invariant — "no hardcoded domain name appears in this module"
- a determinism property — "the same inputs produce the same layout", "stored error text is
  byte-identical across runs"
- a preservation property — "foreign data survives a write", "recovered bytes match"
- anything whose failure would be **silent** in production

Not needed for ordinary example-based tests, where the assertion *is* the behaviour.

## The procedure

1. **State the invariant in one sentence** — what would be *wrong in the world* if this test
   failed. If you cannot say it without describing the implementation, the test is asserting
   mechanics rather than a guarantee. Fix that first.

2. **Find the code that upholds it.** Often not the code the test calls.

3. **Break it minimally.** The smallest edit that makes the invariant false and nothing else.
   Not a syntax error, not a raised exception — those fail everything and prove nothing about
   *this* test.

4. **Run only that test.** It must fail, **and the failure message must name the invariant.**
   A test that fails with `KeyError` when the real problem is "the layout changed" will not
   tell a future reader what broke.

5. **Restore exactly** — `git checkout -- <file>`. Never leave the perturbation.

6. **Re-run.** Green. Then say plainly that the guard was verified and how it was broken.

## Two lessons, both learned the hard way

### A test that stays green with the code broken is a *wrong test*

Not a lucky one. A function was added to strip memory addresses out of stored error text.
Its test passed **both** with and without the fix, because the fixture used the one corrupt
input whose error message happened to contain no address. The bug was real and the test
could not see it. Parametrising over four shapes made nine tests fail without the fix.

**If step 4 does not fail, suspect the test before the perturbation.**

### A perturbation can be too weak to prove anything

A layout pin was tested by adding candidate widths to a packer's search. The test stayed
green — because a *minimum* over a superset returns the same minimum. The perturbation
changed the code without changing the invariant. Changing the sort order did break it, and
the pin was real after all.

**If step 4 does not fail, first ask whether you actually violated the invariant.** Only
then conclude the test is weak.

## What not to do

**Never weaken the guard to make it pass.** When an architecture check failed on a module's
own docstrings, the fix was to reword the prose — not to loosen the check. A guard edited to
accommodate the code it guards has stopped being a guard, and the next person will not know
it happened.

Say what you broke and what happened. "The pin fails when the sort order changes" is
evidence. "The pin passes" is not.

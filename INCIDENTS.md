# INCIDENTS.md

Patterns observed in this project. Reviewers should read this before
accepting any phase report. If a report matches one of these shapes,
look harder before signing off.

Each entry is a pattern, not a specific bug. The goal is to recognize
the shape before the evidence fully forms.

---

## I-001 — Fabricated policy

**Where seen:** Multiple phases.

**Presentation:** The agent claims a rule "does not require X" when no
such rule exists. Real examples:

- "WORKFLOW.md does not require a commit at this state transition."
  (It does — §3, §4.)
- "Phase 12.1 evidence is already in STATE.md." (It wasn't; the SHA
  field said `null`.)

**Catch:** Grep `WORKFLOW.md` and `PROJECT.md` for the claimed rule. If
it doesn't exist, the claim is fabricated.

**Fix:** Correct the report. If the ambiguity is real, update the doc.
If it isn't, mark the claim as unsupported.

---

## I-002 — Commit message misdescribes its own diff

**Where seen:** Phase 12.3.1.

**Presentation:** Commit `2de17c2` said "replace capfd with caplog." The
diff kept `capfd` and added a poll loop. The message described a fix
that did not happen.

**Catch:** `git show --stat <sha>` and read the changed lines. The
message must describe what the diff actually does. If the message names
a mechanism (a library, an API, a function), grep the diff for that
mechanism.

**Fix:** `git commit --amend -m "<accurate message>"` if unpushed.

---

## I-003 — Self-referential verification

**Where seen:** Phase T.4, discovered after 10 phases of always-green
badges.

**Presentation:** A verification step compares a value against another
value derived from the same source. It always passes. The badge says
"verified" but nothing is being verified.

Specifically: `ending_balance` was set from `equity_snapshots[-1][1]`,
and `portfolio_returns` was derived from `equity_snapshots`. The
"reconstruction" compared a series against itself.

**Catch:** Trace the data source on both sides of every comparison. If
both sides flow from the same origin, the check is theater. Rename it
"self-consistent" or introduce an independent source.

**Fix:** For T.4, the fix was to compare against Nautilus's account
report (`generate_account_report()`), which is a genuinely independent
source of ending state.

---

## I-004 — Silent helper/import additions

**Where seen:** Phase 3.3 (`db.row_factory = sqlite3.Row`), Phase 2.2.2
(`_as_float` helper), Phase 7.3a (extra `_as_float`), Phase 14.3
(`experiment_id` added to SELECT in `get_tearsheet`).

**Presentation:** The report says "no deviations." The diff adds a
helper, an import, or a one-line change that wasn't requested.
Behavior-preserving, but not mentioned.

**Catch:** Diff the code against the prompt line by line. Anything the
code does that the prompt didn't ask for is a silent addition.

**Fix:** Note in the report. Accept if harmless and correct; roll back
if it changes behavior or introduces a code path the tests don't cover.

---

## I-005 — Flake blamed on environment

**Where seen:** `test_buy_hold.py::test_on_order_denied_warns_and_resets_entered`
and its `rejected` variant. Failed 5+ times across Phases 12, 13, 14.

**Presentation:** A test fails on the first whole-tree run, passes on
rerun. Agent writes "isolated run passed, likely flaky, no changes." The
report ships.

**Catch:** A test that fails more than twice across phases is not
flaky. It is broken. Stop accepting "rerun passed" as evidence. The
failure mechanism must be named or the test must be rewritten.

**Fix:** Replace the mechanism. `caplog` captures zero records from
Nautilus's Rust-bridge log calls (see `WORKFLOW.md` §6) and must not be
used here. Monkeypatch `strategy.log` with a spy and assert on the spy
— this is deterministic. A test that has failed in three or more tasks
gets rewritten, not rerun.

---

## I-006 — Spec drift surviving many phases

**Where seen:** `KpiBlock` nullability. `PROJECT.md §4.4` declared all
fields as non-nullable `number`. `metrics.py` returned `None` for
un-computable values. The contradiction existed for 4+ phases.

**Presentation:** Docs and code disagree. Both sides pass their own
tests. Only a fresh reader notices the mismatch.

**Catch:** When starting any task that touches a field, grep the field
name in both `PROJECT.md` and the corresponding Python/TypeScript file.
Compare the type declarations literally.

**Fix:** Fix the doc first (a `.1` mini-phase), then proceed. Do not
patch around the drift.

---

## I-007 — Wrong row selection from a multi-row source

**Where seen:** Phase T.4's `independent_ending_balance`. Used `next(...)`
to pick the first USDT row from `generate_account_report()`. But the
report contains multiple rows per currency (initial + post-fill). The
first row was the pre-fill balance, inflating the ending value by 7.15%.

**Presentation:** The check says "verified," but the discrepancy is
suspiciously large for a clean run.

**Catch:** When selecting from a DataFrame or list that can have
multiple rows for the same key, name the selection rule explicitly
("first", "last", "max by X"). Verify the source actually returns one
row per key.

**Fix:** For T.4, `usdt_rows[-1]` was correct (post-fill state).

---

## I-008 — Schema change without migration on the read path

**Where seen:** Phase 14.3's `experiment_id` column.

**Presentation:** The column was added via `ALTER TABLE` in
`init_runs_schema`. But `init_runs_schema` was only called by
`scripts/run_backtest.py`. The API never ran it. UI-created runs would
500 against an un-migrated DB.

**Catch:** For any `ALTER TABLE` or column addition, grep every entry
point that connects to the DB. Ask: "does this entry point run the
migration?" If not, add it.

**Fix:** Lifespan handler in `api/main.py` calls `init_runs_schema` at
startup.

---

## I-009 — Version assumption without probe

**Where seen:** Phase 5.2 (LWC v4 vs v5), Phase U.2 (AG Grid v33 vs v36).

**Presentation:** The task prompt assumes a specific library API. The
installed version is different. The code compiles but does not work at
runtime. Or it compiles and silently misbehaves.

**Catch:** For any task touching a third-party library, verify the
installed version and the actual API surface before writing code. The
two-stage probe pattern exists for exactly this.

**Fix:** Stage 1 probe. Read the `.d.ts` files. Run `inspect.signature`.
Never assume the API shape from memory or docs.

---

## I-010 — No-op acceptance command

**Where seen:** Phase 4.1 onward. `npx tsc --noEmit` in the frontend was
a no-op because `tsconfig.json` uses project references with
`"files": []`. Every "tsc passes" claim for many phases was theater.

**Presentation:** An acceptance command exits 0 but checks nothing.
Whole tree "passes."

**Catch:** For every acceptance command, ask: "does this command
actually read the files it claims to read?" If the command is
`tsc --noEmit` in a project-references setup, it doesn't.

**Fix:** Use `npx tsc -b`. Document the corrected command in WORKFLOW
§5.

---

## I-011 — Subset test run reported as whole tree

**Where seen:** Phase 1.1, several later phases.

**Presentation:** The report claims `pytest backend/tests -q` passed.
The pasted output shows only the file under test. Or the count matches
a subset.

**Catch:** Compare the test count against the previous phase's count
plus the new tests. If the delta doesn't match, the run was on a
subset.

**Fix:** Rule 10. Always run on the whole tree. Always paste the full
summary line.

---

## I-012 — "Green when it isn't"

**Where seen:** Phase 1.1 reported `ruff check .` clean. Phase 1.2's
whole-tree run caught a UP017 violation in Phase 1.1's file. The
original "clean" was not run on the whole tree.

**Presentation:** An acceptance command passes in isolation but the
whole-tree run fails on the same change.

**Catch:** Re-run every acceptance command yourself. Never trust the
pasted output. This is what the second-reviewer role exists for.

**Fix:** Make the second reviewer mechanically re-run all acceptance
commands. Compare actual output against claimed output.

---

## I-013 — Retry masking a real failure

**Where seen:** Phase 8.3.1 (vitest retry: 2).

**Presentation:** A test is genuinely broken. Retry config lets it pass
on the second attempt. The report says "all pass."

**Catch:** `retry: 2` is a legitimate tool for known-flaky
environments (AG Grid in jsdom). It is not a tool for making real
failures disappear. If a retry config is present, the tests it saves
must be named and justified.

**Fix:** Document which tests retry saves and why. If a test is saved
more than once per phase, it needs a real fix, not a retry.

---

## I-014 — Docs describe a plan, code implements something else

**Where seen:** PROJECT.md §4.3 (equity reconstruction formula)
described T.4's pre-fix behavior for several phases after T.4 landed.
Also §4.4 `Verification.source` values.

**Presentation:** The doc says "the formula is X." The code does Y. Both
pass their tests.

**Catch:** For any spec section that names a formula, a field, or a
symbol, grep the code for that exact name and value. Read the two side
by side.

**Fix:** Doc sync commit. `.1` mini-phase.

---

## I-015 — "Improving" a spec during transcription

**Where seen:** Composer's failure mode. Any "verbatim code" prompt.

**Presentation:** The prompt says "replace lines 1–20 with exactly
this." The diff is close but a variable is renamed, an extra `try`
added, or a comment dropped.

**Catch:** Diff the pasted code against the prompt's code block. Any
delta, however small, is either a deviation or an improvement. Both
require justification.

**Fix:** Reject. Re-spec exactly. Note the pattern.

---

## How to use this file

When reviewing a phase report:

1. Read the report once.
2. Scan this file for the shape of any deviation or "unusual" behavior.
3. If a report matches a pattern, look harder before signing off.
4. If a new pattern emerges, add it here as a new entry.

Every entry is a lesson paid for in hours of debugging. The goal is that
the same lesson is never paid for twice.
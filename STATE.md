# STATE.md — Colossal Quant Current Execution State

> **Authoritative live state.** This file answers WHERE the project is. It does not redefine the project specification.
>
> Agents MUST read this file before planning or implementing work.
> Do not infer current state from memory, chat history, commit messages, README text, or old audit reports.

---

## 1. Current State

```yaml
current_phase: 18
current_phase_status: IN_PROGRESS
current_task: 18.2b
current_task_status: READY
next_task: null
last_completed_task: 18.2a
last_completed_phase: 17
execution_mode: ONE_TASK_AT_A_TIME
human_decisions: confirmed
human_transition_required: false
```

### Phase status

- Phase 0 — COMPLETE
- Phase 1 — COMPLETE
- Phase 2 — COMPLETE
- Phase 3 — COMPLETE
- Phase 4 — COMPLETE
- Phase 5 — COMPLETE
- Phase 6 — COMPLETE
- Phase 7 — COMPLETE
- Phase 8 — COMPLETE
- Phase 9 — COMPLETE
- Phase 10 — COMPLETE
- Phase 11 — COMPLETE
- **Phase 12 — COMPLETE (all 4 tasks)**
- **Phase 12.5 — COMPLETE (U.0–U.5)**
- **Phase 13 — COMPLETE**
- **Phase 14 — COMPLETE (14.1–14.4)**
- **Phase 15 — COMPLETE (15.1–15.4)**
- **Phase 16 — COMPLETE (16.1–16.4)** (research-integrity foundation; closed before Phase 17+)
- **Phase 16.5 — COMPLETE (16.5.1–16.5.6)** (tear-sheet research report UI; not Phase 17)
- **U.6 — COMPLETE (U.6.1–U.6.5)** (tear-sheet research workspace redesign)
- **Phase 17 — COMPLETE (17.1–17.8)** (research experiment foundation)
- **Phase 18 — IN PROGRESS** (OOS and walk-forward validation; semantics first)
- Phase 19–29 — BACKLOG (research-platform ambitions)

> Phase 0–11 status above is the recorded project state from the latest research-integrity audit context. If repository evidence contradicts this state, STOP and report the conflict rather than silently changing this file.

---

## 2. Current Objective

Phase 17 is complete. Persisted research metadata now round-trips
through storage, the API, the CLI, creation controls, run history, and
the tear sheet. The human-confirmed Phase 18 rules and all scenario outcomes
are now accepted in `docs/specs/phase-18.md` under `phase18-temporal-v1`.
Research ranges use [start,end); gap values, warmup requirements, dependency
horizons, and enumerated windows remain explicit experiment inputs. No global
numeric defaults may be invented. Temporal enforcement is not implemented by
the documentation acceptance.

Older per-task evidence blocks (12.1 through 16.5.5), the stray Phase
12.1 notes, the Phase 12 non-goals list, and the Phase 0–11 audit's
P0/P1 findings and Last Audit Record live in
`docs/evidence/STATE-archive.md`. That file is historical reference
only and is not required reading before starting or reviewing current
work.

### Current task

**18.2b — Verified bar-clock and coverage helper and test** — READY.
Fresh narrow planning and independent readiness review have established the
bounded supported contract below from the accepted decisions and current code.
No implementation of 18.2b has begun. Only this helper and its mirrored test
are opened; its acceptance will certify supplied clock consistency and coverage,
not actual source publication evidence or runtime eligibility.

18.2a implements stage applicability, complete endpoint pairs, strict start<end,
chronological nonoverlap and [start,end) integer point membership. Null-stage
ordinary behavior is preserved. No existing caller uses the helper. Acceptance
certifies this declaration contract only, not runtime eligibility, actual
coverage, causal availability, warmup, execution containment, frozen selection,
API/CLI enforcement, gaps or walk-forward properties. Historical execution and
metadata remain intact.

Remaining admission and runtime integration, warmup and information access,
boundary artifacts, frozen selection and provenance work require fresh narrow
planning before their READY transitions. No task after 18.2b is opened or split
by this acceptance; next_task is null pending that later planning. These bounds
do not claim the entire 18.2 scope is split or complete. Continue serial
planner/doer/independent reviewer roles and separate reviewer state commits.
No automatic phase crossing is authorized.

### Phase 17 tasks

- [x] **17.1 — Research metadata persistence contract** — COMPLETE
- [x] **17.2 — Research metadata API schemas** — COMPLETE
- [x] **17.3 — Research metadata API transport** — COMPLETE
- [x] **17.4 — Backtest CLI research metadata inputs** — COMPLETE
- [x] **17.5 — Frontend research metadata wire types** — COMPLETE
- [x] **17.6 — Research metadata creation controls** — COMPLETE
- [x] **17.7 — Research-aware run history** — COMPLETE
- [x] **17.8 — Tear-sheet research identity display** — COMPLETE

### Phase 18 tasks

- [x] **18.1 — IS/validation/OOS semantics questions** — COMPLETE. Historical question-inventory acceptance only; evidence below is preserved.
- [x] **18.1.1 — Confirmed temporal decision record** — COMPLETE. All 23 decisions and 15 scenario outcomes accepted; no implemented enforcement claim.
- [ ] **18.2 — Enforce the approved stage windows** — NOT_STARTED as a whole; bounded implementation begins with 18.2a only and requires later accepted integration work.
- [x] **18.2a — Pure research-range declaration helper and test** — COMPLETE. Independently accepted declaration checks only; no runtime or research-validity certification.
- [ ] **18.2b — Verified bar-clock and coverage helper and test** — READY. Fresh independently reviewed fixed-grid, explicit zero-delay clock and exact coverage contract below; no implementation or acceptance yet.
- [ ] **18.3 — Embargo and gap rules** — NOT_STARTED. Only EG-01's named transitions, with EG-02/EG-03 evidence and exclusions, after preceding acceptance/readiness gates.
- [ ] **18.4 — Walk-forward window identity** — NOT_STARTED. Only WF-01's explicitly enumerated model and WF-02–WF-04 rules, after preceding acceptance/readiness gates.

### U.6 tasks

- [x] **U.6.1 — Risk tab component** — COMPLETE
- [x] **U.6.2 — Risk route and eight-item navigation** — COMPLETE
- [x] **U.6.3 — Overview KPI and chart cleanup** — COMPLETE
- [x] **U.6.4 — Performance cleanup and Risk chart ownership** — COMPLETE
- [x] **U.6.5 — Data experiment identity and UTC range** — COMPLETE

### Phase 16.5 tasks

- [x] **16.5.1 — Experiment identity header** — COMPLETE
- [x] **16.5.2 — Overview executive summary** — COMPLETE. Headline and secondary KPIs visible together, plus existing equity, drawdown, and monthly heatmap. No new metrics. No rolling series.
- [x] **16.5.3 — Performance investigation layout** — COMPLETE. Existing price, equity, and underwater charts, equity dominant. No rolling Sharpe or volatility unless a series already exists on the tear sheet.
- [x] **16.5.4 — Trades summary** — COMPLETE. Existing closed-trade KPIs above the current ledger. No MAE, MFE, or R-multiple charts.
- [x] **16.5.5 — Data methodology layout** — COMPLETE. Reorganize fields the Data tab already renders, including the recorded equity clock. No new identity fields.
- [x] **16.5.6 — Honest unavailable sections** — COMPLETE. Regimes and Robustness stay empty of fabricated analysis. Execution shows assumptions already on the response, not a cost breakdown.

Record an accepted task in this file only after the reviewer re-runs that task's acceptance commands. Do not open the next task until that evidence block is committed.

### 18.2b readiness contract and evidence

Fresh independent readiness review accepts only the following task contract.
Rule source: `docs/specs/phase-18.md`, `phase18-temporal-v1`, especially
TW-01/TW-02/TW-03/TW-05, IA-02 and EN-01/EN-02/EN-04/EN-05. The coordinator
accepted this conservative supported capability under the human's delegated
choices. Unsupported clocks fail closed rather than acquiring invented defaults.

**Scope:** create only `backend/src/quant/engine/bar_coverage.py` and
`backend/tests/engine/test_bar_coverage.py`. Production uses stdlib and an
absolute import of the accepted `quant.engine.temporal.ResearchInterval`.
No existing code, exports, schema, storage, ingestion, API, CLI, runner, worker,
frontend, fingerprint, protected file or dependency changes. Doer never edits
STATE. Direct record construction itself is unvalidated, as in 18.2a.

**Public interface:** frozen `BarClock(open_ts: int, close_ts: int,
available_ts: int)` and
`validate_bar_coverage(interval: ResearchInterval, *, timeframe: object,
calendar: object, anchor_ts: object, observations: Sequence[Mapping[str, object]])
-> tuple[BarClock, ...]`. Input containers obey their typed Sequence/Mapping
contracts; payloads are validated at runtime. Caller supplies the interval
explicitly, with no stage inference, active-range fallback or eligibility flag.

**Supported clock:** exact calendar token `continuous_utc_fixed` plus explicit
anchor; no venue/session/weekday/midnight/epoch-zero default. Exact canonical
fixed durations in UTC milliseconds: 1m=60000, 5m=300000, 15m=900000,
30m=1800000, 1h=3600000, 4h=14400000, 1d=86400000, 1w=604800000.
These established units match orchestrator.py; an identical local table avoids
importing its third-party execution dependencies. Session and calendar-month
clocks, 1mo/1M and all other unsupported tokens reject without normalization.
Week is an explicit elapsed duration anchored by the caller, not an exchange
weekday assumption. This is a helper input contract, not new persisted fields.

**Values and boundaries:** anchor and interval endpoints must be integers
excluding bool; benign int subclasses, signed/zero/unbounded integers are
preserved. No coercion, datetime bound or normalization. Revalidate interval
endpoints because ResearchInterval is directly constructible: start<end and
both endpoints congruent to anchor modulo duration. Each observation explicitly
supplies integer `ts` (established OPEN meaning), `close_ts`, `available_ts`;
missing/null evidence rejects. Open must align, close must equal open+duration,
and availability must explicitly equal close for this supported zero-delay
capability. Known delayed availability is unsupported, not silently shifted;
unknown availability cannot be inferred from opens, ingested_at or wall time.

**Exact coverage batch:** each close lies in [start,end), including start and
excluding end. Input contains exactly the active-stage batch, already ordered;
context/warmup/later observations reject, never filter/sort/deduplicate/repair.
All repeated opens reject, including equal records and conflicting extras;
strict chronological order is required. First close may have an open one
interval before start. Membership does not permit scoring earlier movement or
carrying exposure, positions, orders or returns. Empty batch rejects. With
expected_count=(end-start)//duration, require exact count after validating every
row. Aligned unique strictly ordered closes inside the aligned half-open grid
with exact count mathematically imply start,start+duration,...,end-duration.
Independent reviewer identified a redundant unreachable per-index mismatch
predicate in the draft plan; coordinator explicitly approved its removal before
implementation. No accepted inputs or observable errors change and no impossible
branch test is required. Use O(n) actual-row work/memory and arithmetic count,
never allocate or iterate a huge expected schedule or shorten an interval.
Return detached frozen records in a tuple; extra mapping values are ignored,
caller inputs untouched, repeated calls equal, later caller mutation harmless.

**Failure order:** calendar then timeframe; anchor/start/end types; strict
interval order; start then end alignment; each row in input order checks ts,
close_ts, available_ts types, open alignment, close equality, availability
equality, close membership, duplicate open, strict chronology. After all rows:
empty batch then complete count. A later malformed row outranks missing-count
failure; row-local types outrank duplicate/order. Every rejection logs exactly
one ERROR on this module's logger and raises ValueError with identical message;
valid calls emit no log. Do not serialize caller payloads or arbitrary objects.

Exact messages:

- `calendar must be continuous_utc_fixed`
- `timeframe must be one of 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w`
- `<field> must be an integer UTC epoch-millisecond timestamp (bool is not allowed)`
  for anchor_ts, interval.start_ts, interval.end_ts or observations[i].ts,
  observations[i].close_ts, observations[i].available_ts
- `interval.start_ts must be less than interval.end_ts`
- `interval.start_ts must align with the declared bar grid`
- `interval.end_ts must align with the declared bar grid`
- `observations[i].ts must align with the declared bar grid`
- `observations[i].close_ts must equal ts plus the declared timeframe duration`
- `observations[i].available_ts must equal close_ts for the supported clock`
- `observations[i].close_ts must be inside the half-open interval`
- `observations[i].ts duplicates an earlier observation`
- `observations must be strictly chronological`
- `observations must contain at least one stage observation`
- `observations do not provide complete expected bar coverage`

**Required tests:** independent fixtures for all eight durations with shifted
anchors and exact records; one-duration/start-inclusive/end-exclusive/shared
boundary membership; signed/zero/huge/subclass integers; unsupported tokens and
nonstrings; bool/float/string/Decimal/null/NaN/inf/object for all six timestamp
slots plus missing row fields; equal/reversed/misaligned intervals/opens;
incorrect/stretched closes; early/unknown/delayed availability; empty/missing
first/interior/last/partial batches; exact/conflicting duplicates, reversed order
and extra context rows; February/March monthly rejection; enormous interval
with small batch and no timing-based assertion; deterministic precedence,
single ERROR/value error and no payload leakage; mapping proxies/nested sentinels,
repeatability/caller mutation, tuple/frozen output. No random data, real data
writes, new dependencies, external services or weakened existing tests.
Every function needs meaningful public-path/direct coverage.

**Claim limits:** mechanically consistent supplied timestamps/calendar do not
certify source history, actual publication delays, point-in-time revisions,
realistic same-bar execution, preboundary exposure, causal warmup, fitting,
feature/outcome horizons, gaps, freezing, provenance, multi-instrument coverage,
OOS contamination or walk-forward properties. No caller integration is opened.
Stored bars contain opens only; read.py's inclusive open filter/deduplication
and runner.py's next-stored-open/monthly-30-day inference are insufficient
research evidence and remain unchanged. Whole 18.2 and Phase 18 remain incomplete.
No later task or phase is opened; never begin Phase 29.

Readiness baseline: clean branch `phase18/18.2b-bar-coverage` at
`4d3c8e84ca25974e78ee69952116b0211109fb7c`. Reviewer independently verified
live `git ls-remote --heads origin main` returned that SHA; accepted decision
commit 2bfe143 and helper commit 73f81f0 are ancestors (both exit 0). The user's
wait-for-PR-merge condition is fulfilled by the merged prerequisite tree on main.
Remote observation is current-check evidence, not guaranteed future freshness
or publication. Git used command-only network permission, preserving proxy/TLS.
Existing venv Python 3.12.14 imports pytest 9.1.1, ruff 0.16.10, mypy 2.4.0,
duckdb 1.5.6, pydantic 2.13.5 and NautilusTrader 1.231.0; no installs needed.
Readiness review read full AGENTS/STATE/WORKFLOW/REVIEWER/INCIDENTS/spec and
required PROJECT/rules, planner report and relevant actual code/tests.
Supplemental exact plan: /tmp/phase18b-plan.md; this durable contract does not
depend on that temporary file for the supported scope. No third-party call in
this task needs a Stage-1 probe. No Python files changed; pytest/ruff/mypy were
not rerun for this STATE-only readiness commit under WORKFLOW section 5.
Reviewer ran whole git diff/status/staged whitespace and scope checks before
terminal commit. This READY transition is separate from future implementation
and acceptance; last_completed_task remains 18.2a and next_task remains null.

**Implementation acceptance:** activate existing Linux venv, run from repo root
exactly `python -m pytest backend/tests -q`, `python -m ruff check .`,
`python -m mypy --strict backend/src`, `git diff --check`, `git status --short`.
Full pytest needs the previously evidenced command-only network grant for
local TestClient sockets, with options/plugins/proxy/TLS unchanged. Preserve
all failures and authorized correction history under the documented loop limit.
One terminal implementation commit:
`feat(engine): validate explicit bar clock coverage (Phase 18.2b)`.
Fresh independent acceptance reviewer reruns all exact commands, then records
accepted evidence in a separate STATE commit. Task-level PR targets main after
acceptance; coordinator confirms remote branch/PR before claiming publication.
Doer/readiness reviewer neither pushes nor merges. Further tasks require fresh
narrow planning/readiness; no automatic main mutation or phase crossing.

### 18.2a completion evidence

```yaml
task_id: 18.2a
status: COMPLETE
reviewer_decision: accepted_declaration_contract_only
reviewer_date: 2026-10-03
files_changed:
  - backend/src/quant/engine/temporal.py
  - backend/tests/engine/test_temporal.py
tests_added_or_updated:
  - 184 deterministic parameterized declaration and point-membership cases
  - absent/null stage exits before endpoint reads and ignores malformed legacy ranges
  - exact stages, applicability, every complete optional/required pair and endpoint type
  - semantic chronology, overlap rejection, signed/zero/unbounded integers and shared boundaries
  - matching single ERROR and ValueError, first-failure precedence, caller immutability and frozen outputs
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "628 passed, 81 warnings in 34.71s; exit 0"
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 31 source files; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state update; exit 0"
git_commit_sha: 73f81f0636b6c715e07c3f01ba0ab03c8eb0251a
next_task: 18.2b
next_task_status: NOT_STARTED
human_decisions: confirmed
human_transition_required: false
deviations:
  - "Existing Linux venv/Bash activation and command-only network grant instead of documented Windows example; acceptance commands unchanged."
notes: |
  The authorized serial task moved from READY through planner contract/readiness,
  doer implementation (IN_PROGRESS), committed handoff (ACCEPTANCE_PENDING),
  and fresh independent reviewer acceptance (COMPLETE). The intervening role
  handoffs are recorded here; the doer did not advance STATE or self-accept.
  Reviewer read the full actual two-file commit, accepted narrow plan, doer
  report, full workflow/reviewer/incident/spec records and relevant project
  contracts. Stage requirements, every supplied inactive pair, fixed semantic
  order, half-open membership, immutable detached records, early ordinary exit
  and deterministic log-plus-raise behavior match the approved contract.
  All exact whole-tree acceptance commands independently passed on their first
  reviewer invocation using the existing venv; no installs or code changes.
  Full pytest used command-only network permission for local TestClient socket
  operation, preserving configured proxy/TLS and all command options/plugins.
  Doer's initial restricted pytest stalled without a result; only verified
  owned PID was terminated after the network-granted diagnostic succeeded.
  Its original shell exit was unavailable, not reported as a passed run.
  Two precommit cosmetic lint correction cycles (5 issues then one remaining
  long line) and all original failures remain in the doer report/logs.
  Reviewer found no hidden semantic correction or weakened test assertion.
  Independent output is preserved in /tmp/phase18a-review-pytest.log,
  /tmp/phase18a-review-ruff.log and /tmp/phase18a-review-mypy.log; temporary
  reports are supplemental, while this evidence and task commit are durable.
  Live git ls-remote --heads origin main work independently returned main
  81824f70aaeeb7efc07b8afc127a43a2b888bcd7 and work
  90c35911d95515fde0f25e856fd9858e99332a9f before this state commit.
  That observation verifies current connectivity, not publication of this task.
  This separate reviewer commit changes STATE only. No caller/API/CLI/runtime
  integration, bar/calendar coverage, warmup, gaps, frozen selection, provenance
  or walk-forward guarantee is accepted. API coercion cannot be undone here;
  missing versus null is intentionally equivalent, validation use cannot be
  inferred, and integer points/touching boundaries prove no availability/gap
  eligibility. 18.2b remains NOT_STARTED pending fresh narrow planning/readiness.
  Whole 18.2 remains incomplete, Phase 18 remains IN_PROGRESS, and no later
  task or phase is opened. Historical evidence below is preserved unchanged.
```

### 18.1.1 completion evidence

```yaml
task_id: 18.1.1
status: COMPLETE
reviewer_decision: accepted_confirmed_decision_record_only
reviewer_date: 2026-10-03
files_changed:
  - docs/specs/phase-18.md
tests_added_or_updated: []
acceptance_commands:
  - python /tmp/phase18-verify-decision-record.py
  - python /tmp/phase18-reviewer-compare.py
  - git diff --check
  - git status --short
  - git show --check 2bfe14315cb6c0152ad01e57068173e379a66f9e
  - git diff-tree --no-commit-id --name-only -r 2bfe14315cb6c0152ad01e57068173e379a66f9e
acceptance_output:
  source_comparison: "PASS: all 23 stable decision IDs match the source record exactly (whitespace normalized). PASS: all 15 stable scenario IDs match the source record exactly."
  provenance_scope: "PASS: approval/provenance, historical inventory acceptance, scope gates, stage applicability, and absence of decision placeholders verified."
  changed_paths: "PASS: only docs/specs/phase-18.md changed; protected/state/code/test/dependency files unchanged."
  independent_comparison: "All 23 unique IDs/decisions and 15 outcomes exact; original headings, scenarios, question links, established contract bullets/source links preserved; exit 0."
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state update"
  commit_check: "commit header/message only; no whitespace errors; exit 0"
  file_list: "docs/specs/phase-18.md"
git_commit_sha: 2bfe14315cb6c0152ad01e57068173e379a66f9e
next_task: 18.2a
next_task_status: READY
human_decisions: confirmed
human_transition_required: false
deviations:
  - "Question prose replaced with confirmed answers; stable headings/IDs and original inventory commit preserve historical evidence. Coordinator explicitly accepted this approach; no amendment requested."
notes: |
  Fresh independent reviewer read the full spec and actual one-file task diff,
  applicable project/workflow/reviewer/rules and incident records, doer report,
  and independently supplied /tmp/phase18-confirmed-decisions.md. All 23
  decision paragraphs and 15 scenario outcomes match that approved source.
  Manual review confirmed stage applicability, approval provenance, scope gates,
  historical preservation, explicit experiment inputs and limited guarantees.
  The user approved seven initial decisions, delegated remaining choices, saw
  the complete record, and explicitly confirmed/authorized the first task with
  "just fix the git connectivity and start the first task auto now".
  Reviewer independently re-ran every documentation acceptance command.
  A supplemental comparison first failed at SC-01 because its temporary parser
  included the trailing table delimiter; the parser alone was corrected outside
  the checkout. Its full rerun passed; no specification correction was needed.
  Live git ls-remote origin refs/heads/main independently returned
  81824f70aaeeb7efc07b8afc127a43a2b888bcd7 using configured proxy/network permission.
  No backend, scripts, or frontend files changed; pytest, ruff, mypy, tsc,
  vitest and build were not rerun under WORKFLOW.md section 5.
  This separate reviewer state commit opens only 18.2a. 18.2b, 18.3 and 18.4
  remain NOT_STARTED. Phase 18 remains IN_PROGRESS; no phase crossing or
  runtime eligibility, warmup, gap/window, API/CLI or freeze enforcement is
  certified. Further narrow task planning and independent acceptance remain
  required. The original 18.1 evidence block below is historical and unchanged.
```

### 18.1 completion evidence

```yaml
task_id: 18.1
status: COMPLETE
reviewer_decision: accepted_question_inventory_only
reviewer_date: 2026-10-03
files_changed:
  - docs/specs/phase-18.md
tests_added_or_updated: []
acceptance_commands:
  - git diff --check
  - git status --short
  - git show --check f6060f8b97e2ed304e7c8a4618647d9dca725d09
  - git diff-tree --no-commit-id --name-only -r f6060f8b97e2ed304e7c8a4618647d9dca725d09
acceptance_output:
  diff_check: "no output; exit 0"
  status: "no output; clean before state evidence update"
  commit_check: "commit header only; no whitespace errors; exit 0"
  file_list: "docs/specs/phase-18.md"
git_commit_sha: f6060f8b97e2ed304e7c8a4618647d9dca725d09
next_task: 18.2
next_task_status: NOT_STARTED
human_transition_required: true
deviations: []
notes: |
  Fresh independent reviewer inspected the entire 364-line questions document
  and actual one-file commit, current metadata schemas/persistence/wire types,
  accepted Phase 17 evidence, and the Phase 16 clock contract and test evidence.
  Manual documentation acceptance verified all 23 question groups and 15
  scenario outcomes remain unresolved; all human approval fields remain blank.
  Coverage includes stage meaning, boundaries and membership, warmup and
  information access, boundary state, gaps, walk-forward identity and reselection,
  final holdout, enforcement, legacy records, provenance, and guarantee limits.
  No defaults, recommendations, numeric window sizes, implementation design,
  inferred human decisions, or authorization for 18.2 were introduced.
  No backend, scripts, or frontend files changed; pytest, ruff, mypy, tsc,
  vitest, and build were not rerun for this documentation-only task.
  Implementation and acceptance review of 18.1 have concluded; this separate
  reviewer evidence commit records completion. The next task is identified
  without opening it: 18.2 remains NOT_STARTED pending human decisions.
  Phase 18 remains IN_PROGRESS; 18.3 and 18.4 remain NOT_STARTED.
```

### 17.1 completion evidence

```yaml
task_id: 17.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/data/runs_store.py
  - backend/tests/data/test_runs_store.py
tests_added_or_updated:
  - fresh meta_runs schemas contain all nullable research metadata columns
  - legacy schemas migrate in place with NULL research metadata
  - insert_run preserves every research metadata field
  - insert_run_with_connection preserves every research metadata field
  - claim_next_queued preserves every research metadata field
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "431 passed, 81 warnings"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: b0ad975
next_task: 17.2
deviations: []
notes: |
  Commit b0ad975 was cherry-picked into the primary checkout as
  1a925cc. Before final acceptance, separate commit 0c5d842 replaced
  the known I-005 Rust-bridge capfd polling tests with deterministic
  warning spies. The reviewer then re-ran every whole-tree acceptance
  command without retries. No API, frontend, optimizer, or Phase 18
  validation behavior is included.
```

### 17.2 completion evidence

```yaml
task_id: 17.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - backend/src/quant/api/schemas.py
  - backend/tests/api/test_schemas.py
tests_added_or_updated:
  - RunSummary accepts and serializes all nullable research metadata
  - RunCreate accepts all nullable research metadata
  - omitted research metadata defaults to None
  - invalid research_stage values are rejected
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "435 passed, 81 warnings"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: 62a2365
next_task: 17.3
deviations: []
notes: |
  Reviewer independently re-ran every whole-tree acceptance command.
  The implementation changes only API schema contracts and their direct
  tests. No API transport wiring, frontend, optimizer, or Phase 18
  validation behavior is included.
```

### 17.3 completion evidence

```yaml
task_id: 17.3
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - backend/src/quant/api/routers/runs.py
  - backend/tests/api/test_runs_create.py
tests_added_or_updated:
  - research metadata round-trips through run creation and persistence
  - run-list responses preserve all research metadata
  - tear-sheet run summaries preserve all research metadata
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "436 passed, 81 warnings"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: fa311a4
next_task: 17.4
deviations: []
notes: |
  Reviewer independently re-ran every whole-tree acceptance command
  without retries. All eleven research metadata fields flow through the
  API create, list, and tear-sheet paths. No CLI, frontend, optimizer, or
  Phase 18 validation behavior is included.
```

### 17.4 completion evidence

```yaml
task_id: 17.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - scripts/run_backtest.py
  - backend/tests/test_run_backtest.py
tests_added_or_updated:
  - omitted CLI research metadata persists as NULL and remains outside params
  - all CLI research metadata inputs persist with their established names and types
  - exploration, validation, and oos research stages are accepted
  - invalid research stages and integer metadata inputs are rejected
acceptance_commands:
  - python -m pytest backend/tests -q
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - git diff --check
  - git status --short
acceptance_output:
  pytest: "444 passed, 81 warnings"
  ruff: "All checks passed!"
  mypy: "Success: no issues found in 30 source files"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: 9b3fe3909116fe1eaf52d745b891489d8a6188e9
next_task: 17.5
deviations: []
notes: |
  Reviewer independently inspected the committed CLI and test diff and
  re-ran every whole-tree backend acceptance command. Research metadata
  remains separate from strategy params. The task adds metadata inputs only;
  it does not add frontend behavior or Phase 18 temporal enforcement.
```

### 17.5 completion evidence

```yaml
task_id: 17.5
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - frontend/src/api/types.ts
  - frontend/src/api/runs.test.ts
  - frontend/src/pages/CommandCenter/RunHistoryTable.test.tsx
  - frontend/src/pages/CommandCenter/StrategyForm.test.tsx
  - frontend/src/pages/Compare/index.test.tsx
  - frontend/src/pages/TearSheet/ExperimentHeader.test.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_added_or_updated:
  - populated and explicit-null metadata remains top-level in create requests
  - omitted request metadata is supported and response metadata is explicitly null
  - run-list and tear-sheet responses preserve populated and null research metadata
  - incomplete RunSummary metadata is rejected at compile time
  - exploration, validation, and oos typecheck while unsupported stage literals fail
  - five existing RunSummary fixtures explicitly provide all eleven nullable fields
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
  - git diff --check
  - git status --short
acceptance_output:
  tsc: "exit 0"
  vitest: "Test Files  30 passed (30); Tests  215 passed (215)"
  build: "142 modules transformed; built in 387ms; exit 0"
  diff_check: "exit 0"
  status: "clean"
git_commit_sha: e2ea48089cd63bd7a1115e49542b584bfe13d679
next_task: 17.6
deviations:
  - "Human approved amendment and expansion to five existing response fixture files so RunSummary fields remain required nullable."
notes: |
  Fresh independent reviewer inspected the full seven-file committed diff
  and re-ran every whole-tree frontend acceptance command from the repo
  root using PowerShell Push-Location/Pop-Location and preserved exit codes.
  The eleven new RunSummary fields are required nullable; RunCreate metadata
  is optional nullable. Existing API helpers are unchanged. No runtime
  component, dependency, optimizer, or Phase 18 temporal enforcement changed.
  The production build reported the existing large-chunk advisory. No backend
  or scripts files changed; pytest, ruff, and mypy were not re-run under
  WORKFLOW.md section 5 path-scoped acceptance.
```

### 17.6 completion evidence

```yaml
task_id: 17.6
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - frontend/src/pages/CommandCenter/StrategyForm.tsx
  - frontend/src/pages/CommandCenter/StrategyForm.test.tsx
tests_added_or_updated:
  - all twelve optional research controls are accessible and initially blank
  - all metadata submits at top level with trimmed strings and UTC epoch-ms dates
  - exploration, validation, and oos stages submit with their exact wire values
  - whitespace, cleared fields, and unset stage are omitted
  - each single date endpoint is accepted without requiring its paired endpoint
  - reversed and overlapping ranges and trial index greater than count are accepted
  - zero, signed integers, and safe-integer boundaries are accepted
  - invalid calendar dates and malformed, fractional, nonfinite, or unsafe integers block submission
  - existing strategy, timeframe, universe, fees, deployment, benchmark, navigation, error, and pending behavior remains covered
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
  - git diff --check
  - git status --short
acceptance_output:
  tsc: "npm notice run frontend@0.0.0 npx; npm notice run tsc -b; exit 0"
  vitest: "Test Files  30 passed (30); Tests  242 passed (242); Duration  7.97s; exit 0"
  build: "142 modules transformed; built in 713ms; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean"
git_commit_sha: 60aee99f550fcbf8139eb43dc0c0c910c5623833
next_task: 17.7
deviations: []
notes: |
  Fresh independent reviewer read the actual two-file committed diff,
  checked backend schemas and accepted frontend wire types, and reran all
  whole-tree frontend acceptance commands from the repository root using
  PowerShell Push-Location/Pop-Location with preserved exit codes. Tests
  exercise real form inputs and payload construction at the createRun
  boundary. No Phase 18 temporal or trial-relationship enforcement was
  added. The production build reported the existing large-chunk advisory.
  No backend or scripts files changed; pytest, ruff, and mypy were not
  rerun under WORKFLOW.md section 5 path-scoped acceptance. Phase 17
  remains IN_PROGRESS; task 17.7 is opened but not implemented.
```

### 17.7 completion evidence

```yaml
task_id: 17.7
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - frontend/src/pages/CommandCenter/RunHistoryTable.tsx
  - frontend/src/pages/CommandCenter/RunHistoryTable.test.tsx
tests_added_or_updated:
  - real grid renders exact column order and populated and null metadata
  - mixed experiments and all three stages remain in API order
  - strings preserve whitespace and UTC ranges preserve full milliseconds
  - partial endpoints, epoch zero, reversed and overlapping ranges remain visible
  - trial zero, negative values and index greater than count remain exact
  - all nine research columns sort through real grid header interactions
  - shared experiment and stage retain distinct selected run IDs
  - existing loading, empty, error, polling and double-click navigation tests remain
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
  - git diff --check
  - git status --short
acceptance_output:
  tsc: "npm notice run frontend@0.0.0 npx; npm notice run tsc -b; exit 0"
  vitest: "Test Files  30 passed (30); Tests  254 passed (254); Duration  14.08s; exit 0"
  build: "142 modules transformed; built in 379ms; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean"
git_commit_sha: a7dff301b1c008168ef29398bde4524109fc786c
next_task: 17.8
deviations:
  - "Supplementary whole-tree npx vitest run --retry=0 probe: 2 failed files, 28 passed; 2 failed tests, 252 passed; duration 13.46s; exit 1. This was not a required acceptance command."
notes: |
  Fresh independent reviewer inspected the full two-file committed diff
  against the task prompt, accepted wire types and backend schemas, then
  reran every required frontend acceptance command from the repository root
  using PowerShell Push-Location/Pop-Location with preserved exit codes.
  Required acceptance passed on its first invocation. No inferred research
  validity, filtering, grouping, Phase 18 enforcement or tear-sheet work was
  added. Existing query, navigation, theme and KPI behavior is unchanged.
  Earlier debugging attempts corrected grid header selectors and the blank
  selection-column header expectation; final assertions verify exact DOM
  values and real sorting rather than weakening the behavior checks.
  To audit I-013, the reviewer additionally disabled retries for one full
  suite probe. RunHistoryTable > renders rows when data loads and
  TradeLedger > renders rows when data loads timed out finding their row
  text; failure DOM showed hidden grid containers and empty headers. Both
  assertions predate this task and are unchanged. All metadata-specific
  tests passed. frontend-tooling.md and original commit dfaafcb explicitly
  authorize retry: 2 for parallel AG Grid jsdom layout timing; this task
  does not change that setting. The supplemental failures are retained here,
  not reported as green or hidden behind a rerun. Production build reported
  the existing large-chunk advisory. No backend or scripts files changed;
  pytest, ruff and mypy were not rerun under WORKFLOW.md section 5.
  Phase 17 remains IN_PROGRESS; task 17.8 is opened but not implemented.
```

### 17.8 completion evidence

```yaml
task_id: 17.8
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-02
files_changed:
  - frontend/src/pages/TearSheet/ExperimentHeader.tsx
  - frontend/src/pages/TearSheet/ExperimentHeader.test.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
  - frontend/src/pages/TearSheet/tearSheet.css
tests_added_or_updated:
  - null research metadata renders as em dashes in run-history label order
  - populated strings, all three stages, and full UTC ranges stay exact
  - partial endpoints, a reversed range, trial zero, and a negative trial count stay exact
  - the Data tab timeframe em dash assertion is scoped to that row
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
  - git diff --check
  - git status --short
acceptance_output:
  tsc: "exit 0"
  vitest: "Test Files  30 passed (30); Tests  256 passed (256); Duration  11.95s; exit 0"
  build: "142 modules transformed; built in 561ms; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean"
git_commit_sha: 77df5035d30446328ab45e63b3c52fec3b8bb590
next_task: 18.1
deviations:
  - "Display formatters live in ExperimentHeader instead of being shared with RunHistoryTable."
  - "The reversed-range test title also says overlapping; the asserted OOS case is reversed (1000 to 0), not a separate overlap fixture."
  - "Supplementary whole-tree npx vitest run --retry=0: 30 files passed, 256 tests passed, duration 11.88s, exit 0. This was not a required acceptance command."
notes: |
  Fresh reviewer read the four-file committed diff against the task,
  accepted wire types, and run-history display rules, then reran every
  required frontend acceptance command from the repository root.
  Required acceptance passed on its first invocation. The header shows
  all eleven persisted fields, including explicit nulls, without
  inferring validity or adding Phase 18 enforcement. The Data tab still
  omits a null experiment id. The production build reported the existing
  large-chunk advisory. No backend or scripts files changed; pytest,
  ruff, and mypy were not rerun under WORKFLOW.md section 5. Phase 17
  is complete. Phase 18.1 is opened as questions only because embargo,
  inclusivity, and walk-forward sizes are not specified.
```

### U.6.1 completion evidence

```yaml
task_id: U.6.1
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/RiskTab.tsx
  - frontend/src/pages/TearSheet/tabs/RiskTab.test.tsx
tests_added:
  - RiskTab shows the five supplied risk KPIs and drawdown series
  - RiskTab renders five null KPI values as em dashes
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 205 passed"
  build: "exit 0"
git_commit_sha: bff113e37788b898172bfa10bae15d533bc71e84
next_task: U.6.2
deviations: []
notes: |
  Reviewer re-ran all frontend acceptance commands. No backend or
  scripts files changed, so pytest, ruff, and mypy were not re-run.
```

### U.6.2 completion evidence

```yaml
task_id: U.6.2
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/App.tsx
  - frontend/src/pages/TearSheet/TearSheetNav.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_updated:
  - nav renders eight items in the approved order with intended badges
  - Risk route renders and marks its navigation item active
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 205 passed"
  build: "exit 0"
git_commit_sha: ffc277b
next_task: U.6.3
deviations: []
notes: |
  Reviewer re-ran all frontend acceptance commands. No backend or
  scripts files changed, so pytest, ruff, and mypy were not re-run.
```

### U.6.3 completion evidence

```yaml
task_id: U.6.3
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/OverviewSummary.tsx
  - frontend/src/pages/TearSheet/OverviewSummary.test.tsx
  - frontend/src/pages/TearSheet/tabs/OverviewTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_updated:
  - Overview keeps the approved headline and secondary KPI bands
  - Overview omits Win Rate, Trades, Avg Duration, and Underwater
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 205 passed"
  build: "exit 0"
git_commit_sha: 290be85
next_task: U.6.4
deviations:
  - "The first full-suite run exposed an over-broad negative assertion that matched the permanent Trades nav item; the assertion was scoped to the KPI section before commit."
notes: |
  Reviewer re-ran all frontend acceptance commands after the test fix.
  No backend or scripts files changed, so pytest, ruff, and mypy were
  not re-run.
```

### U.6.4 completion evidence

```yaml
task_id: U.6.4
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/PerformanceTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_updated:
  - Performance keeps Price + Fills followed by dominant equity
  - Performance omits Underwater, whose route remains Risk
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 205 passed"
  build: "exit 0"
git_commit_sha: 97cd298
next_task: U.6.5
deviations: []
notes: |
  Reviewer re-ran all frontend acceptance commands. No backend or
  scripts files changed, so pytest, ruff, and mypy were not re-run.
```

### U.6.5 completion evidence

```yaml
task_id: U.6.5
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/DataTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_updated:
  - Data renders a non-null experiment id
  - Data omits a null experiment id and shows the UTC date range
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "30 files, 206 passed"
  build: "exit 0"
git_commit_sha: 3928376
next_task: null
deviations: []
notes: |
  Reviewer re-ran all frontend acceptance commands. Compare and all
  existing frontend tests passed. No backend or scripts files changed,
  so pytest, ruff, and mypy were not re-run. U.6 is complete; Phase 17
  remains unopened.
```

### 16.5.6 completion evidence

```yaml
task_id: 16.5.6
status: COMPLETE
reviewer_decision: accepted
reviewer_date: 2026-10-01
files_changed:
  - frontend/src/pages/TearSheet/tabs/ExecutionTab.tsx
  - frontend/src/pages/TearSheet/tabs/ExecutionTab.test.tsx
  - frontend/src/App.tsx
  - frontend/src/pages/TearSheet/tabs/PlaceholderTab.tsx
  - frontend/src/pages/TearSheet/index.test.tsx
tests_added:
  - frontend/src/pages/TearSheet/tabs/ExecutionTab.test.tsx (2)
  - frontend/src/pages/TearSheet/index.test.tsx::robustness tab says no analysis is attached
  - frontend/src/pages/TearSheet/index.test.tsx::execution tab shows assumption strings from the tear sheet
tests_updated:
  - frontend/src/pages/TearSheet/index.test.tsx::regimes tab says classification is not attached
acceptance_commands:
  - cd frontend && npx tsc -b
  - cd frontend && npx vitest run
  - cd frontend && npm run build
acceptance_output:
  tsc: "exit 0"
  vitest: "29 files, 203 passed"
  build: "exit 0"
git_commit_sha: aa0aaff7c21011f3301d97c467f8e7f91dc2007f
next_task: null
deviations:
  - "PlaceholderTab now takes the unavailable sentence directly. The old phase template could not show the required copy."
  - "A non-object assumptions value, or one whose maker_fee is not a string, uses the same missing sentence as the Data tab."
  - "No Python files changed, so pytest, ruff, and mypy were not re-run."
notes: |
  Reviewer re-ran tsc -b, vitest, and the production build on aa0aaff.
  Regimes and Robustness show the unavailable sentences and no
  fabricated analysis. Execution lists every assumption string
  verbatim. Fees are not summed. A missing assumptions object shows
  the missing sentence once. The Data tab was not changed. Phase 17
  is not started.
```

## 3. Important Limitations

- A green test suite does not prove absence of future-bar influence.
- A self-consistent equity reconstruction is not an independent external account verification.
- Bar-close timestamps do not by themselves eliminate same-bar execution bias.
- Statistical metrics are not evidence of strategy validity until the research-design controls are implemented.

The Phase 0–11 audit's P0/critical and P1/high findings, and the full
Last Audit Record (commit `5fffa3cbd618ca05e65620f2b26ddae260f122be`,
2026-09-30, scope Phases 0–11), are historical and live in
`docs/evidence/STATE-archive.md`.

---

## 4. Archived Historical State

The former historical evidence and audit section now lives in
`docs/evidence/STATE-archive.md`. It is reference material, not live
execution state.

---

## 5. Permanent Architecture Boundary

### Colossal Quant owns

- data ingestion and validation;
- dataset selection and identity;
- experiment/run metadata;
- strategy configuration;
- research workflow;
- validation/statistical reporting;
- visualization;
- artifact extraction and integrity checks;
- research provenance.

### NautilusTrader owns

- event-driven simulation;
- order lifecycle;
- matching/fills;
- commissions/fees as configured through Nautilus;
- portfolio/account mechanics;
- execution semantics delegated to Nautilus.

**Do not build a second implementation of a Nautilus responsibility.**

---

## 6. State-Transition Rules

A task may transition only through:

```text
NOT_STARTED
    ↓
READY
    ↓
IN_PROGRESS
    ↓
ACCEPTANCE_PENDING
    ↓
COMPLETE
```

Failure returns the task to `IN_PROGRESS` or `BLOCKED`.

A phase cannot become `COMPLETE` until:

1. every task is complete;
2. required tests exist and test the specified behavior;
3. whole-tree acceptance passes;
4. no unapproved scope changes remain;
5. required probe/approval rules were followed;
6. the reviewer accepts the work;
7. this file is updated with evidence.

No agent may skip a state transition merely because the change appears small.

---

## 7. Required Evidence Per Completed Task

Record:

- task ID;
- files changed;
- tests added/changed;
- exact acceptance commands;
- exact relevant output;
- git commit SHA;
- deviations from specification;
- reviewer decision;
- next task.

Do not record “done” as the only evidence.

---

## 8. Conflict Protocol

If any of the following disagree:

- `STATE.md`;
- `PROJECT.md`;
- `docs/ai/WORKFLOW.md`;
- `docs/ai/REVIEWER.md`;
- repository code;
- tests;
- git history;
- a third-party API probe;

STOP.

Report:

```text
STATE CONFLICT

Source:
Claim:
Repository/API evidence:
Current recorded state:
Potential impact:
Required decision:
```

Do not silently choose which source is “probably right.”

---

## 9. Update Rule

`STATE.md` is intentionally short and mutable.

It must be updated whenever a task or phase changes state.

Do not copy the complete roadmap into this file. The permanent roadmap belongs in `PROJECT.md`.

Do not put implementation details here unless they are necessary to describe current state or a blocker.

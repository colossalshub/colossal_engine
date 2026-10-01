# STATE.md — Colossal Quant Current Execution State

> **Authoritative live state.** This file answers WHERE the project is. It does not redefine the project specification.
>
> Agents MUST read this file before planning or implementing work.
> Do not infer current state from memory, chat history, commit messages, README text, or old audit reports.

---

## 1. Current State

```yaml
current_phase: 17
current_phase_status: IN_PROGRESS
current_task: 17.1
current_task_status: READY
next_task: 17.2
last_completed_task: U.6.5
last_completed_phase: U.6
execution_mode: ONE_TASK_AT_A_TIME
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
- **Phase 17 — IN PROGRESS** (research experiment foundation)
- Phase 18–29 — BACKLOG (research-platform ambitions)

> Phase 0–11 status above is the recorded project state from the latest research-integrity audit context. If repository evidence contradicts this state, STOP and report the conflict rather than silently changing this file.

---

## 2. Current Objective

Build the Phase 17 research experiment foundation so exploratory trials
and designated validation/OOS runs carry explicit, durable identity.
This phase records research metadata without adding an optimizer or the
temporal enforcement rules reserved for Phase 18.

Older per-task evidence blocks (12.1 through 16.5.5), the stray Phase
12.1 notes, the Phase 12 non-goals list, and the Phase 0–11 audit's
P0/P1 findings and Last Audit Record live in
`docs/evidence/STATE-archive.md`. That file is historical reference
only and is not required reading before starting or reviewing current
work.

### Current task

**17.1 — Research metadata persistence contract** — READY. Extend
`meta_runs` and `RunRecord` with nullable research stage, hypothesis,
strategy-version, IS/validation/OOS range, and trial index/count fields.
Preserve the existing `params`, `data_snapshot`, `git_sha`, and
`experiment_id` identities. Migrate legacy databases in place and prove
fresh-schema, migration, insert, and worker-claim round trips.

### Phase 17 tasks

- [ ] **17.1 — Research metadata persistence contract** — READY
- [ ] **17.2 — Research metadata API schemas** — NOT_STARTED
- [ ] **17.3 — Research metadata API transport** — NOT_STARTED
- [ ] **17.4 — Backtest CLI research metadata inputs** — NOT_STARTED
- [ ] **17.5 — Frontend research metadata wire types** — NOT_STARTED
- [ ] **17.6 — Research metadata creation controls** — NOT_STARTED
- [ ] **17.7 — Research-aware run history** — NOT_STARTED
- [ ] **17.8 — Tear-sheet research identity display** — NOT_STARTED

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

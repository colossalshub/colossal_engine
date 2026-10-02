# Phase 18 — Confirmed Temporal Semantics

**Task 18.1 accepted the question inventory only. Task 18.1.1 records the
human-confirmed decisions below; neither documentation task implements temporal
enforcement.**

Rule identity: `phase18-temporal-v1`. Decision date: 2026-10-03 (Asia/Manila).
Stable question and scenario IDs connect these decisions to the accepted
inventory. This document changes no engine, API, CLI, or UI behavior. The
approved rules are implementation requirements, not evidence that current runs
satisfy them. No optimizer is in scope.

## Established contracts and evidence

These facts describe the accepted contracts that the confirmed rules must preserve.

- `research_stage` has exact wire values `exploration`, `validation`, `oos`,
  or `null`. IS is a range concept, not a stage wire value.
- Phase 17 introduced eleven fields: `research_stage`, `hypothesis_id`,
  `strategy_version`, `in_sample_start_ts`, `in_sample_end_ts`,
  `validation_start_ts`, `validation_end_ts`, `oos_start_ts`, `oos_end_ts`,
  `trial_index`, and `trial_count`. `experiment_id` already existed and is
  additional to those eleven.
- Research metadata is optional/nullable at creation and nullable in storage
  and responses. Frontend response types require nullable metadata members;
  creation members may be omitted. Phase 17 transports and displays metadata,
  including incomplete, reversed, and overlapping ranges; it does not enforce
  Phase 18 temporal semantics. A label is not evidence of research validity.
- Execution `start_ts` and `end_ts` are distinct from the six research range
  fields. No equivalence or containment rule follows from their names.
- Timestamps use UTC epoch milliseconds; curated-bar `ts` identifies bar open.
  Canonical timeframes distinguish `1m` (minute) from `1mo` (month).
- Phase 16's human-confirmed daily artifact clock puts a bar close at the
  next bar's open, retains the account start at first open and equity at every
  close, including the first close. A same-bar fill and first close share a
  timestamp, whose equity point includes the fill. This clock contract does
  not choose research-stage membership or prove absence of information leakage.
- Phase 18 requires unambiguous selection versus final evaluation, no silent
  OOS entry into parameter selection, testable/reproducible boundaries, and
  preserved window identities and results. Walk-forward work waits for an
  explicit specification. Phase 17 explicitly excludes a parameter optimizer.

Sources: [PROJECT.md §§4.1–4.2 and Phases 16–18](../../PROJECT.md),
[STATE.md current task and accepted Phase 17 evidence](../../STATE.md),
[API schemas](../../backend/src/quant/api/schemas.py),
[metadata persistence](../../backend/src/quant/data/runs_store.py), and
[frontend wire types](../../frontend/src/api/types.ts).

## Stage purpose and selection identity

### ST-01 — Meanings and applicability

Decision: Exploration permits development and IS fitting/selection, including general
research without a formal split. A claimed IS interval requires complete IS endpoints.
Validation compares IS-developed candidates and may select the final candidate; complete
IS and validation ranges are required. Final OOS evaluates a frozen selection; complete
IS and OOS ranges plus validation ranges when validation was used are required.
Validation is optional and explicitly absent when skipped. No optimizer is authorized.

### ST-02 — Frozen selection and scope

Decision: Freeze each candidate before its validation evaluation, then freeze the final
selected candidate before any OOS inspection. Changes to strategy logic, parameters,
fitted preprocessing or selection criteria create a new candidate revision with recorded
lineage. The selection record binds experiment, hypothesis, candidate/version, exact
parameters, fitted artifacts where applicable, considered trials, selection-data
identity, code identity, seed where relevant, and approved temporal rules. Evaluation
results bind actual input identity and preserve prior results.

## Boundaries, membership, and coverage

### TW-01 — Endpoint convention and shared endpoints

Decision: Uniform research range convention is start-inclusive, end-exclusive
[start,end). A point event at a shared endpoint belongs only to the later stage. These
research semantics do not silently rewrite historical ordinary execution semantics.

### TW-02 — Membership clock and straddling events

Decision: Completed bars belong by verified close/availability time; signals, orders,
fills and equity changes use actual event clocks. Require research boundaries to align
with a verified bar clock. A bar that opens before a boundary and closes after it
becomes usable only at its close, in the later stage. Its earlier price movement cannot
be counted as evaluation exposure. Selection cannot use information arriving at or after
selection end. Preserve the established daily artifact clock; membership rules do not
alter existing timestamps or prove realistic same-bar execution.

### TW-03 — Range validity and ordering

Decision: Required research ranges have both endpoints and start<end. Optional ranges
are wholly absent or wholly specified. IS precedes validation, which precedes OOS; if
validation is absent IS precedes OOS directly. Stages cannot overlap; touching endpoints
may be allowed subject to explicit gap rules. A stage with no eligible observations
cannot receive a valid evaluation claim. Invalid declarations are rejected, never
silently repaired, reordered or shortened. Historical records are preserved.

### TW-04 — Execution coverage

Decision: One evaluated stage per research run, with optional explicitly declared
earlier warmup. Trading and scored results stay inside the active stage; warmup has no
trading, returns or performance metrics. No later observations may influence execution.
Execution timestamps and six research endpoints are distinct and their relationship must
be enforced explicitly.

### TW-05 — Data availability and calendar time

Decision: Require complete expected coverage under an explicit timeframe/calendar
contract. Missing observations, conflicting duplicates, empty stages or unverifiable
closes prevent eligible evaluation. No interpolation or shortening. Unsupported calendar
mappings are ineligible. Calendar months cannot be treated as a fixed elapsed duration
for eligibility; the current final-month 30-day fallback is not calendar-correct
evidence.

## Information access and boundary state

### IA-01 — Warmup and preprocessing

Decision: Prior observations, including earlier stages, may initialize indicators only
causally and under declared warmup requirements; no invented default warmup length. Fit
models, normalization, imputation and other learned transformations only in permitted IS
data, then freeze for evaluation. Fixed indicator algorithms may update causally during
evaluation. Insufficient required history prevents eligibility. Warmup within gaps
follows EG-02. Warmup never contributes trades or metrics.

### IA-02 — Feature and outcome horizons

Decision: Features must be available when used, including publication delays and event
ordering. Selection outcomes must be fully available strictly before selection ends;
exclude observations whose outcomes enter evaluation. Earlier feature history is
permitted only through approved causal warmup. A timestamp alone does not establish
eligibility; dependency and outcome intervals must be permitted. Unknown availability is
not silently inferred from event time.

### IA-03 — State, orders, positions, and metrics

Decision: Every evaluated stage starts with declared initial cash, no positions and no
open orders. Reconstruct permitted indicator state from warmup; only approved frozen
model state may be loaded. Preserve actual fills and fees. At the end disclose remaining
positions and value them at the last eligible price; only genuinely closed trades enter
closed-trade statistics. Do not fabricate liquidation or use later prices. No
position/order carry into another stage. Independent stage results are not a
continuous-account return series.

### IA-04 — OOS inspection and contamination

Decision: Record inspection of OOS observations or results, including
researcher-declared external/manual inspection. Original frozen evaluation results
remain preserved. Later selection informed by that inspection requires a new unseen
final holdout. Exact reruns are reproducibility checks, not additional independent
evidence. External behavior cannot be independently certified by labels or hashes.

## Embargo and gap semantics

### EG-01 — Transitions, direction, unit, and value

Decision: Explicitly declare a nonnegative minimum gap in elapsed UTC milliseconds for
IS->validation, validation->OOS, IS->OOS if validation is absent, and every walk-forward
training->evaluation transition. The interval between stages is excluded from selection
and scoring. No universal numeric duration or silent default is selected.

### EG-02 — Dependencies and activity inside gaps

Decision: Gap observations may initialize fixed indicators causally, but may not
fit/select models, generate scored performance or carry trading exposure. Check declared
feature, release, outcome, holding-period and cross-series dependencies. A gap alone
does not establish statistical independence.

### EG-03 — Exceptional gaps and reproducibility

Decision: Zero gap requires explicit declaration and sufficient dependency evidence.
Unknown dependencies are not zero. Missing bars do not shorten elapsed gaps. Reject
insufficient gaps and stages consumed by exclusions; preserve declared boundaries and
reproducible exclusion evidence.

## Walk-forward model and identity

### WF-01 — Window generation

Decision: Start with an explicitly ordered list of windows, each declaring IS, optional
development-validation, forward-evaluation boundaries and applicable gaps. No automatic
generator or invented rolling lengths, anchor, step or window duration. The declared
list defines generation and stopping.

### WF-02 — Overlap, reuse, and gaps

Decision: Training windows may overlap; evaluation windows may not. Earlier
forward-evaluation observations may enter later training only under a sequential
learning recipe fixed before the sequence and only after they become available. Forward
windows are development/validation evidence, not the untouched final OOS holdout. Manual
changes require a new sequence identity. Each window's selected candidate is frozen
before that evaluation; no future window information may influence earlier windows.

### WF-03 — Incomplete windows and final holdout

Decision: Reject incomplete declared windows rather than silently trimming or omitting
them. Reserve a separate final OOS holdout after development windows and freeze the
final selection before inspecting it. Earlier forward-window results may support final
selection; final OOS may not.

### WF-04 — Identity, reruns, and aggregate results

Decision: Bind window results to sequence, boundaries, candidate, data, code, seed and
temporal-rule identity. Preserve each rerun separately. Initially report individual
results; no invented combined return series or aggregate statistical claim.

## Enforcement, compatibility, and approval gates

### EN-01 — Consistency and invalid outcomes

Decision: Same contract at API/CLI admission and recheck actual input data and
eligibility before execution. Invalid designated research runs fail explicitly; no
silent downgrade to ordinary execution. Unsupported guarantees stay clearly unverified.
A completed lower-level subtask does not certify unenforced properties.

### EN-02 — Legacy and null metadata

Decision: Preserve historical records and original execution semantics. Null-stage runs
remain ordinary runs. Older research labels are unverified declarations. New eligibility
requires a separate evaluation with supporting evidence, not history rewriting.

### EN-03 — Rule identity, lineage, and replay

Decision: Rule identity phase18-temporal-v1. Preserve original declarations, effective
membership, warmup, gaps, dependency evidence, selection lineage, actual input
identities, environment and seed information. Changes to data/code/parameters/rules
create a distinct evaluation identity. Existing formatted data fingerprints are not
complete revision/availability records. Reassessment never silently overwrites
historical interpretation.

### EN-04 — Guarantees versus declarations

Decision: Report mechanically enforced window/availability properties separately from
researcher declarations about outside inspection. Do not claim universal non-leakage,
statistical independence, realistic execution or historical point-in-time validity
without evidence. Green tests are necessary but not sufficient.

### EN-05 — Decisions required by subsequent tasks

Decision: Stage-window enforcement is 18.2 first; named gaps are 18.3; explicit window
identities/results are 18.4. Unsupported gap/window properties cannot be claimed
prematurely. Follow documented narrow task splitting, serial planner/doer/independent
reviewer, independent acceptance, separate reviewer STATE.md commits, protected files
and phase-boundary stops. Never begin Phase29. No dependency additions or updates are
authorized.

## Stage applicability and implementation scope

The confirmed ST-01 applicability is explicit:

| Research stage | Required research ranges |
| --- | --- |
| `exploration` | Formal IS may be omitted for general research. If formal IS is claimed, both IS endpoints are required. |
| `validation` | Complete IS and validation ranges. |
| `oos` | Complete IS and OOS ranges, plus complete validation ranges if validation was used. Validation is explicitly absent when skipped. |

Every supplied optional range is wholly absent or wholly specified; required
ranges satisfy TW-03. Research range declarations and execution timestamps are
distinct. The active-stage, warmup, event-clock, coverage, and information-access
rules must be enforced explicitly before eligible evaluation can be claimed.

The human has confirmed all 23 decisions and 15 scenario outcomes. The standard
workflow still requires narrow task splits, serial planner/doer/independent
reviewer roles, independent acceptance, and separate reviewer `STATE.md`
commits. Recording this decision does not advance the live state or accept a
future implementation task.

- **18.2 — Stage-window enforcement:** begin with **18.2a, a pure declaration
  validator**, under a separately accepted task split. That first subtask checks
  stage applicability, endpoint completeness, strict range validity, and
  chronological nonoverlap under the approved convention. It does not certify
  execution containment, actual coverage, causal availability, warmup, frozen
  selection, or runtime enforcement. Subsequent narrow subtasks must inspect
  supported engine/API/CLI contracts and implement/recheck the supported
  stage-window guarantees before claiming them. API/CLI admission alone cannot
  establish actual input eligibility.
- **18.3 — Named gaps:** only EG-01's IS->validation, validation->OOS,
  IS->OOS when validation is absent, and every walk-forward training->evaluation
  transition, with EG-02/EG-03 dependency and exclusion rules. No gap guarantee
  may be claimed before its enforcement is accepted.
- **18.4 — Explicit windows:** only the explicitly ordered, enumerated model
  in WF-01 through WF-04, with preserved sequence/window identities and results.
  No walk-forward guarantee may be claimed before its enforcement is accepted.

Per-experiment gap values, warmup requirements, dependency horizons, and
enumerated window boundaries are required explicit inputs. They are not missing
global defaults to invent. No universal numeric gap, warmup length, rolling
length, anchor, step, or window duration is selected. No new optimizer,
statistical estimator, aggregation, multi-instrument execution, realistic fill
model, or calendar repair is authorized implicitly. Unsupported guarantees fail
or remain unverified as the confirmed rules specify; ordinary historical
behavior remains intact. Phase-boundary stops still apply; never begin Phase 29.
No dependency additions or updates are authorized.

## Confirmed scenario outcomes for later acceptance cases

These are approved expected outcomes for future implementation acceptance, not
evidence of executable checks or enforcement in the current application.

| ID | Scenario | Related questions | Outcome |
| --- | --- | --- | --- |
| SC-01 | Selection ends exactly when evaluation starts; an event has that timestamp. | TW-01, TW-02 | Point event at shared endpoint belongs to later stage only; information arriving then cannot enter earlier selection. |
| SC-02 | A bar opens before a boundary and closes after it. | TW-02, IA-02 | Straddling bar usable at verified close in later stage only; no prior-stage selection use or scoring of pre-evaluation exposure. |
| SC-03 | A range has one endpoint, reversed endpoints, or equal endpoints. | TW-03, EN-02 | Reject new designated research declarations with partial/reversed/equal endpoints; preserve historical records as unverified. |
| SC-04 | A legacy run has null stage and null research ranges. | ST-01, EN-02 | Legacy null-stage/null-range run is ordinary history, with no inferred research guarantee. |
| SC-05 | Execution starts before or ends after its designated stage. | TW-04, IA-03 | Explicit earlier nontrading warmup may precede active stage; later execution or outside-stage scoring rejected. |
| SC-06 | A declared stage has missing bars, partial instrument coverage, or no observations. | TW-03, TW-05 | Missing, partial or empty required coverage prevents eligible evaluation, without silent repair. |
| SC-07 | Evaluation warmup needs observations from an earlier stage or gap. | IA-01, EG-02 | Prior-stage or gap warmup may be used causally under declared warmup/gap rules; not scored or fitted. |
| SC-08 | A selection observation's outcome horizon enters evaluation. | IA-02, EG-02 | Outcome horizon entering evaluation excludes the observation from selection; reject if sufficient eligible selection data no longer exists. |
| SC-09 | An open order or position crosses the boundary; a later close realizes its result. | IA-03, TW-01 | No open position/order carry into next independent stage; disclose residual exposure without later-price attribution. |
| SC-10 | A declared gap is insufficient, zero, or consumes the next stage. | EG-01, EG-03 | Reject insufficient or stage-consuming gaps; zero accepted only explicitly with evidence. |
| SC-11 | A calendar-month timeframe or missing session changes elapsed window/gap duration. | TW-05, EG-03, WF-01 | Declared calendar and elapsed-gap clock govern; unverifiable mappings fail eligibility. |
| SC-12 | Walk-forward evaluation windows share observations or trades. | WF-02, WF-04 | Reject evaluation overlap; no duplicated observations/trades/returns in combined claims. |
| SC-13 | Available data ends before the final generated window is complete. | WF-03, TW-05 | Incomplete declared final window is rejected, not shortened. |
| SC-14 | Identical boundaries are rerun after a parameter, dataset, code, or rule change. | ST-02, WF-04, EN-03 | Changed parameters/data/code/rules create new evaluation identity; preserve original result/lineage. |
| SC-15 | OOS results are inspected and then used to revise selection or a later window. | IA-04, WF-02, WF-03, EN-04 | Final OOS inspection used for revision makes it development information for that revision, requiring a new unseen holdout. Predeclared sequential reuse applies only to forward-validation windows. |

## Human approval record

**Inventory reviewer and acceptance reference:** The independent reviewer
accepted task 18.1 as `accepted_question_inventory_only`, recorded in
`STATE.md` at starting HEAD `81824f70aaeeb7efc07b8afc127a43a2b888bcd7`.
The original inventory commit is
`f6060f8b97e2ed304e7c8a4618647d9dca725d09`. That historical acceptance settled
no semantic answers and authorized no enforcement implementation.

**Human decision-maker:** The user in the current Codex chat. No additional
personal identity or signature is asserted.

**Decision date:** 2026-10-03 (Asia/Manila).

**Approved question IDs and explicit answers:** All 23: ST-01–ST-02,
TW-01–TW-05, IA-01–IA-04, EG-01–EG-03, WF-01–WF-04, and EN-01–EN-05. The
`Decision:` paragraphs above contain the confirmed answers.

**Approved scenario outcomes:** All 15, SC-01–SC-15, exactly as recorded in the
confirmed scenario matrix above.

**Rationale and tradeoffs accepted:** Explicit selection/evaluation separation,
causal information availability, independent stage state, frozen selection and
preserved lineage, reproducible declarations, and claims limited to supported
evidence. Gap values, warmup requirements, dependencies, and window boundaries
remain experiment inputs; no numeric global defaults are invented. The complete
confirmed decisions above govern these tradeoffs.

**Remaining questions and exclusions:** No question or scenario in this
inventory awaits a semantic answer. Experiment-specific inputs and future
implementation task splits are still required. The scope exclusions above
remain in force; documentation approval does not certify implementation.

**Approved rule identity and decision reference:** `phase18-temporal-v1`, the
complete Phase 18 human-confirmed decision record supplied in this Codex chat
and transcribed under the stable IDs above. The session source was
`/tmp/phase18-confirmed-decisions.md`; this specification preserves the decisions
in the repository rather than depending on that temporary file for replay.

**Authorization and scope for 18.2:** Approved stage-window rules, beginning
with the narrow 18.2a pure declaration validator after independent acceptance of
this documentation prerequisite and a recorded task split/readiness gate.
Later enforcement subtasks retain their own acceptance gates. No currently
implemented enforcement is implied.

**Authorization and named gaps for 18.3:** The named EG-01 transitions only,
with EG-02/EG-03 rules and explicit per-experiment inputs, after preceding
acceptance/readiness gates. No universal duration is authorized.

**Authorization and window model for 18.4:** The explicitly ordered, enumerated
WF-01 model and WF-02–WF-04 rules only, after preceding acceptance/readiness
gates. No automatic generator or combined return-series claim is authorized.

**Approval provenance:** The user explicitly approved ST-01/ST-02, then
TW-01/TW-03, then TW-04/IA-01/IA-03, delegated remaining choices with
"i approve just make the best trustworthy decisions", received the complete
record, and instructed "just fix the git connectivity and start the first task
auto now". The coordinator treats that latest instruction as confirmation of
the complete record and authorization to start the first bounded Phase 18 task.
No automatic phase crossing is authorized. Repository acceptance and readiness
gates still apply. This records chat approval, not a fabricated signature.

# Phase 18 — Temporal Semantics Decision Questions

**Every semantic choice below remains unresolved. Acceptance of task 18.1
accepts the question inventory, not answers or permission to implement them.
Human decisions are required before task 18.2.**

This document changes no behavior. Alternatives are discussion prompts, not
defaults, recommendations, or an exhaustive list. No embargo duration,
endpoint convention, or walk-forward size is selected. There is no optimizer
in scope. Question IDs remain stable so human decisions can refer to them.

## Established contracts and evidence

These facts describe accepted contracts; they do not settle the questions below.

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

What operations constitute exploration, IS fitting/selection, validation, and
final OOS evaluation? Does exploration encompass IS work, or can it describe
other research? When is validation applicable or absent, and which ranges are
required for each stage? Separate stages improve attribution; combined research
work permits iteration but needs explicit limits on information reuse.

Decision: unresolved

### ST-02 — Frozen selection and scope

What identifies the selected hypothesis, strategy/version, parameter set,
experiment, trial set, and dataset/code identity before evaluation? Is selection
frozen per experiment, candidate, or window? Which edits create a new selection,
and when may reselection occur? Broader identity permits reuse; finer identity
distinguishes changes but increases provenance obligations.

Decision: unresolved

## Boundaries, membership, and coverage

### TW-01 — Endpoint convention and shared endpoints

Are starts and ends inclusive or exclusive for each range? Must conventions be
uniform? At a shared endpoint, does an event belong to the earlier stage, later
stage, neither, or both under an explicitly permitted policy? Each alternative
changes membership and potential double counting; which matches the intended
separation of selection and evaluation?

Decision: unresolved

### TW-02 — Membership clock and straddling events

Does membership follow bar open, bar close, signal availability, order, fill,
or the full information interval? Which clock applies to each event/artifact?
How is a bar that opens before a boundary and closes after it treated: included,
excluded, or considered ineligible for that boundary? Must boundaries align to
bars, or can arbitrary UTC instants be used? Alignment simplifies membership;
arbitrary instants require explicit straddling rules.

Decision: unresolved

### TW-03 — Range validity and ordering

What do partial endpoints, equal endpoints, reversed ranges, zero-duration ranges,
and ranges containing no observations mean? Are they invalid, unspecified, or
eligible under declared conditions? May IS, validation, and OOS overlap or occur
out of chronological order? Must absent validation affect ordering between the
remaining stages? Permissive declarations preserve old records; stricter
eligibility provides stronger research guarantees.

Decision: unresolved

### TW-04 — Execution coverage

Must execution equal the active stage, contain it with separate warmup, or be
contained by a declared research range? Can one execution span several stages?
How are events and artifacts outside the designated range treated? Equality
simplifies attribution; broader execution permits context and continuity but
needs explicit boundaries on scoring and information access.

Decision: unresolved

### TW-05 — Data availability and calendar time

Is coverage assessed by elapsed time, expected bars, observed bars, trading
sessions, or another declared calendar? What makes partial coverage, missing
bars, an empty interval, or unequal coverage across instruments acceptable?
Should incomplete data invalidate, qualify, or shorten an evaluation? How are
calendar months, weeks, session boundaries, and variable-duration bars handled
without treating calendar units as fixed elapsed durations? Different coverage
definitions change both membership and comparability.

Decision: unresolved

## Information access and boundary state

### IA-01 — Warmup and preprocessing

Which prior observations may initialize indicators, features, normalization,
imputation, or fitted preprocessing? Are these operations fitted only in IS,
refitted in validation, or updated causally during evaluation? Can warmup cross
a stage boundary or gap, and can warmup observations contribute to metrics?
Frozen transformations aid isolation; causal updates represent adaptation but
require a precise information-availability rule.

Decision: unresolved

### IA-02 — Feature and outcome horizons

How are feature lookbacks, publication delays, labels, and future outcome
horizons assigned to stages? Is an observation eligible by its timestamp or
only if its entire dependency/outcome interval is permitted? What happens when
a selection outcome extends into evaluation? Point membership retains more
observations; interval-based eligibility accounts for cross-boundary dependence.

Decision: unresolved

### IA-03 — State, orders, positions, and metrics

Which indicator/model state, cash, positions, and open orders may carry across
boundaries? Are stages independent restarts or continuous execution segments?
What happens to trades opened before a boundary and closed after it, and to
fills, fees, equity changes, and returns at the boundary? Is attribution based
on entry, exit, event time, or segmented exposure? Restarts isolate stages;
continuity preserves path dependence and needs explicit metric attribution.

Decision: unresolved

### IA-04 — OOS inspection and contamination

Which access to OOS data or results counts as inspection, and which later
changes count as selection informed by OOS? After inspection, may the interval
remain a designated holdout, become development data, or require a new holdout?
How are repeated evaluation, manual inspection, and external analysis disclosed?
Reuse enables diagnosis; claims of final evaluation depend on the permitted
feedback and its recorded history.

Decision: unresolved

## Embargo and gap semantics

### EG-01 — Transitions, direction, unit, and value

Which transitions require a gap: IS to validation, validation to OOS, IS directly
to OOS, or transitions between walk-forward windows? Is exclusion before a
boundary, after it, or on both sides? Is its unit elapsed time, bars, sessions,
or calendar units, and what value applies under which conditions? Are values
explicit declarations or derived from declared dependencies? Time-based and
observation-based gaps differ when coverage is irregular.

Decision: unresolved

### EG-02 — Dependencies and activity inside gaps

How do lookbacks, outcome horizons, holding periods, frequency, or cross-series
dependencies determine necessary separation? Are gap observations unavailable,
available for causal warmup, or usable for state evolution without scoring?
Can orders/positions persist through a gap? Stronger isolation discards more
context; permitted continuity needs a precise account of surviving dependencies.

Decision: unresolved

### EG-03 — Exceptional gaps and reproducibility

How do missing bars and calendar boundaries affect gap measurement? When is a
zero gap meaningful? What happens if a required gap consumes a stage or leaves
insufficient observations: invalidation, qualification, or revised boundaries?
What declared inputs and rule identity must reproduce the same excluded
intervals? Fixed declarations simplify replay; dependency-derived gaps require
reproducible dependency information.

Decision: unresolved

## Walk-forward model and identity

### WF-01 — Window generation

Is the model rolling, expanding, explicitly enumerated, or another approved
model? What defines the anchor, stage lengths, step, stopping condition, and
optional validation placement? Are lengths and steps elapsed, observation, or
calendar based? Rolling windows bound history, expanding windows retain it,
and enumerated windows allow bespoke boundaries with additional declarations.
Which inputs must be chosen before generation can be reproducible?

Decision: unresolved

### WF-02 — Overlap, reuse, and gaps

May training windows overlap, may evaluation windows overlap, and may an earlier
evaluation interval enter a later training window? How do gaps apply to each
transition? Is reselection permitted per window or only before the sequence?
Reuse can represent sequential learning; independent evaluations require a
different information boundary. How is the distinction expressed and assessed?

Decision: unresolved

### WF-03 — Incomplete windows and final holdout

Should an incomplete first or final window be omitted, rejected, or retained
with declared reduced coverage? Is a final holdout separate from walk-forward
evaluation, or is a designated window the final evaluation? What selection
activity may use earlier window results before that holdout? Retaining partial
windows increases coverage but changes comparability; reserving a holdout
changes how much data is available for iterative research.

Decision: unresolved

### WF-04 — Identity, reruns, and aggregate results

What makes a window the same window across reruns: boundaries alone or also
selection, data/code, rule, and sequence identity? How are reruns distinguished
from new windows while preserving every result? If evaluation intervals overlap,
are results reported separately, combined with unique-event attribution, or
combined under another declared interpretation? Separate reporting preserves
local results; aggregation needs explicit handling of repeated observations,
trades, and returns to avoid double counting.

Decision: unresolved

## Enforcement, compatibility, and approval gates

### EN-01 — Consistency and invalid outcomes

What semantic guarantees must be consistent across API creation, CLI execution,
workers, and stored records? At what lifecycle points must temporal eligibility
be established or rechecked? Should invalid or unverifiable declarations prevent
execution, permit ordinary execution without a validation claim, or produce a
qualified research result? Early rejection and later qualification have different
effects on usability, incomplete information, and interpretation. This question
does not prescribe endpoints, database changes, or implementation mechanisms.

Decision: unresolved

### EN-02 — Legacy and null metadata

How should historical runs, omitted metadata, null stages, and partial ranges be
interpreted after enforcement exists? Do they remain ordinary runs, require
explicit designation before research use, or become eligible only with additional
evidence? Compatibility preserves access; retroactive validation claims require
evidence unavailable from labels alone. Can interpretation change without
changing the historical record, and how would that distinction remain visible?

Decision: unresolved

### EN-03 — Rule identity, lineage, and replay

What evidence must bind results to the chosen rule version, original declarations,
effective boundaries, selection lineage, dependency horizons, and data/code
identity? Does a rule change produce a new interpretation, a new evaluation, or
both? How are comparisons and reruns under different rules distinguished?
Preserving historical interpretation aids auditability; reassessment under new
rules requires explicit lineage rather than silent reinterpretation.

Decision: unresolved

### EN-04 — Guarantees versus declarations

Which non-leakage properties can the application establish from available data
and execution evidence, and which rely on researcher declarations about manual
selection or external inspection? What evidence permits each research claim,
and how should an unverified claim differ from an enforced guarantee? Restricting
claims to observable evidence improves auditability; declarations cover behavior
outside application visibility but cannot establish it independently.

Decision: unresolved

### EN-05 — Decisions required by subsequent tasks

Which question IDs and scenario outcomes must the human resolve to authorize
18.2 stage-window enforcement? Which named transitions and rules authorize 18.3
embargo/gap work, and which window model and identity rules authorize 18.4?
Must interdependent decisions be approved together, or can a precisely bounded
subset be approved with explicit exclusions? Joint approval resolves interactions;
bounded approval requires clear limits. What evidence demonstrates each gate?

Decision: unresolved

The existing task gate remains: 18.2 cannot start merely because this inventory
is accepted. The human must choose the rules; 18.3 covers only named accepted
gaps, and 18.4 waits for an accepted window model. No question here supplies an
implicit fallback while approval is absent.

## Scenario matrix for human decisions and later acceptance cases

These are unresolved scenarios, not expected behavior or executable tests.
Each row needs an explicit outcome after the related questions are answered.

| ID | Scenario | Related questions | Outcome |
| --- | --- | --- | --- |
| SC-01 | Selection ends exactly when evaluation starts; an event has that timestamp. | TW-01, TW-02 | Decision: unresolved |
| SC-02 | A bar opens before a boundary and closes after it. | TW-02, IA-02 | Decision: unresolved |
| SC-03 | A range has one endpoint, reversed endpoints, or equal endpoints. | TW-03, EN-02 | Decision: unresolved |
| SC-04 | A legacy run has null stage and null research ranges. | ST-01, EN-02 | Decision: unresolved |
| SC-05 | Execution starts before or ends after its designated stage. | TW-04, IA-03 | Decision: unresolved |
| SC-06 | A declared stage has missing bars, partial instrument coverage, or no observations. | TW-03, TW-05 | Decision: unresolved |
| SC-07 | Evaluation warmup needs observations from an earlier stage or gap. | IA-01, EG-02 | Decision: unresolved |
| SC-08 | A selection observation's outcome horizon enters evaluation. | IA-02, EG-02 | Decision: unresolved |
| SC-09 | An open order or position crosses the boundary; a later close realizes its result. | IA-03, TW-01 | Decision: unresolved |
| SC-10 | A declared gap is insufficient, zero, or consumes the next stage. | EG-01, EG-03 | Decision: unresolved |
| SC-11 | A calendar-month timeframe or missing session changes elapsed window/gap duration. | TW-05, EG-03, WF-01 | Decision: unresolved |
| SC-12 | Walk-forward evaluation windows share observations or trades. | WF-02, WF-04 | Decision: unresolved |
| SC-13 | Available data ends before the final generated window is complete. | WF-03, TW-05 | Decision: unresolved |
| SC-14 | Identical boundaries are rerun after a parameter, dataset, code, or rule change. | ST-02, WF-04, EN-03 | Decision: unresolved |
| SC-15 | OOS results are inspected and then used to revise selection or a later window. | IA-04, WF-02, WF-03, EN-04 | Decision: unresolved |

## Human approval record

Blank fields are not approval. Inventory acceptance and semantic approval are
separate; no human answer or authorization is recorded by this task.

Inventory reviewer and acceptance reference:

Human decision-maker:

Decision date:

Approved question IDs and explicit answers:

Approved scenario outcomes:

Rationale and tradeoffs accepted:

Remaining unresolved questions and exclusions:

Approved rule identity and decision reference:

Authorization and scope for 18.2:

Authorization and named gaps for 18.3:

Authorization and window model for 18.4:

Human approval/signature:

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
current_task: 18.2
current_task_status: NOT_STARTED
next_task: null
last_completed_task: 18.2h
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

**18.2 — Remaining stage-window enforcement** — NOT_STARTED.
18.2h is independently accepted for supplied evidence/content identity only.
No future task is READY; next_task null, Phase18 IN_PROGRESS.

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
- [x] **18.2b — Verified bar-clock and coverage helper and test** — COMPLETE. Independently accepted supplied fixed-grid, explicit zero-delay clock consistency and exact batch coverage only; no caller integration or actual source-history certification.
- [x] **18.2c — RunCreate raw research declaration admission** — COMPLETE. Request-model declaration checks only; historical responses and ordinary null-stage behavior preserved.
- [x] **18.2d — CLI research declaration admission** — COMPLETE. Independently accepted CLI declaration checks only; no runtime eligibility claim.
- [x] **18.2e — Runtime raw declaration recheck** — COMPLETE. Independently accepted seven-field raw factory recheck at execute_run entry only; no full runtime eligibility claim.
- [x] **18.2f — Minimal Stage 1 research runtime probe** — COMPLETE. Independently accepted documentation and scratch observations only; no runtime eligibility or Stage 2 approval.
- [x] **18.2g — Research-only fresh BuyHold adapter** — COMPLETE on combined corrected tree 47fa706; supplied-clock/runtime containment only.
- [x] **18.2g.1 — Preserve admitted decimal formatting** — COMPLETE; exact admitted decimal serialization and actual-engine regression accepted.
- [x] **18.2h — Immutable raw research input snapshot and exact identity** — COMPLETE; supplied evidence/content identity only.
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

### Recorded explicit post-probe human approval

The approved bounded contract formerly below this paragraph is preserved in
[the historical readiness record](docs/evidence/STATE-archive.md#182g-readiness-contract-and-post-probe-approval).

**Human approval (2026-10-03):** after the accepted 18.2f probe and exact
bounded Stage 2 proposal were presented, the user replied directly:
"make trustworthy decisions and continue until this phase is done".
The coordinator and independent readiness reviewer record this as explicit
post-probe WORKFLOW §2 approval of the observed calls
`engine.cache.positions_open()` and
`engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))`,
and the bounded research-only BuyHold implementation below. It clears the
current human-transition gate. It approves no unseen future probe, unfamiliar
API, new dependency, automatic phase crossing or completed implementation.
Earlier 18.2f readiness/completion evidence remains historical and unchanged.

### Completed historical evidence references

Implementation/readiness SHAs below are recorded source evidence; missing
readiness SHAs are shown as —. Separate historical reviewer completion commits
are preserved when known in the original records; no missing SHA is inferred.

| Task | Implementation SHA | Readiness SHA | Recorded acceptance | Evidence |
| --- | --- | --- | --- | --- |
| 18.2f | `78250cd5af871c065cf96c186f95432d9227d36e` | `59257d113f1649138c6d768fb4ba392bfb6c7189` | Independent probe replay exit 0; documentation only | [Full historical record](docs/evidence/STATE-archive.md#182f-completion-evidence) |
| 18.2e | `c1eefaec202c0c5a7c0162dd786b4fc8ff14df99` | `054186409fca12aa64d6f26579ea1eeefb9019e3` | 899 passed, 91 warnings in 36.27s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182e-completion-evidence) |
| 18.2d | `fc0d2e2b6685e3c5627210042bde429583b683ba` | `911c2fd6d312eb01581412f65ccfbec65e5c6b47` | 879 passed, 81 warnings in 40.46s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182d-completion-evidence) |
| 18.2c | `9049d6af141b61785453443a3faaef8a811da751` | `d3827ca48595d47e84cce6e78c0cab1b8eeb776b` | 860 passed, 81 warnings in 38.04s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182c-completion-evidence) |
| 18.2b | `b9a25ee197b637e3f3a99ee693d6c13bc34cd5e0` | `5c3d600564146d1bf287ed0427f0168a5e8dd77c` | 792 passed, 81 warnings in 41.30s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182b-completion-evidence) |
| 18.2a | `73f81f0636b6c715e07c3f01ba0ab03c8eb0251a` | `—` | 628 passed, 81 warnings in 34.71s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182a-completion-evidence) |
| 18.1.1 | `2bfe14315cb6c0152ad01e57068173e379a66f9e` | `—` | Confirmed decision documentation | [Full historical record](docs/evidence/STATE-archive.md#1811-completion-evidence) |
| 18.1 | `f6060f8b97e2ed304e7c8a4618647d9dca725d09` | `—` | Question inventory documentation | [Full historical record](docs/evidence/STATE-archive.md#181-completion-evidence) |
| 17.1 | `b0ad975` | `—` | 431 passed, 81 warnings | [Full historical record](docs/evidence/STATE-archive.md#171-completion-evidence) |
| 17.2 | `62a2365` | `—` | 435 passed, 81 warnings | [Full historical record](docs/evidence/STATE-archive.md#172-completion-evidence) |
| 17.3 | `fa311a4` | `—` | 436 passed, 81 warnings | [Full historical record](docs/evidence/STATE-archive.md#173-completion-evidence) |
| 17.4 | `9b3fe3909116fe1eaf52d745b891489d8a6188e9` | `—` | 444 passed, 81 warnings | [Full historical record](docs/evidence/STATE-archive.md#174-completion-evidence) |
| 17.5 | `e2ea48089cd63bd7a1115e49542b584bfe13d679` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#175-completion-evidence) |
| 17.6 | `60aee99f550fcbf8139eb43dc0c0c910c5623833` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#176-completion-evidence) |
| 17.7 | `a7dff301b1c008168ef29398bde4524109fc786c` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#177-completion-evidence) |
| 17.8 | `77df5035d30446328ab45e63b3c52fec3b8bb590` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#178-completion-evidence) |
| U.6.1 | `bff113e37788b898172bfa10bae15d533bc71e84` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u61-completion-evidence) |
| U.6.2 | `ffc277b` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u62-completion-evidence) |
| U.6.3 | `290be85` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u63-completion-evidence) |
| U.6.4 | `97cd298` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u64-completion-evidence) |
| U.6.5 | `3928376` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u65-completion-evidence) |
| 16.5.6 | `aa0aaff7c21011f3301d97c467f8e7f91dc2007f` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#1656-completion-evidence) |

### 18.2g and 18.2g.1 combined completion evidence

```yaml
task_ids: [18.2g, 18.2g.1]
status: COMPLETE
reviewer_decision: accepted_supplied_daily_clock_consistency_and_runtime_containment_only
reviewer_date: 2026-10-03
files_changed:
  - backend/src/quant/engine/research_runner.py
  - backend/tests/engine/test_research_runner.py
tests_added_or_updated:
  - 61 original expanded admission, real-engine containment, callback-failure and compatibility cases
  - one actual-engine exact decimal-volume regression; 62 new cases combined
acceptance_commands:
  - python -m ruff check .
  - python -m mypy --strict backend/src
  - python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 33 source files; exit 0"
  pytest: "961 passed, 121 warnings in 40.42s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state maintenance; exit 0"
git_commit_sha: 47fa7068077952fe9894483ee373ab5873f000df
original_unaccepted_implementation_sha: 5a24edce407b4d3da75ee54c123ee14f0f928d3a
readiness_commit_shas:
  - 568822e9adc6e96e9e8923ea2747875a8773e00f
  - 8154fdebdbde089a95b8b6839df3a94eb73dc1aa
next_task: null
remaining_18_2_status: NOT_STARTED
human_transition_required: false
deviations:
  - "Independent blocking precision finding required separate authorized g.1 repair; original g SHA preserved, never accepted alone or amended."
  - "One corrected-g task PR is the necessary publication unit for original unaccepted adapter plus blocking repair on the same branch; no buggy precursor merge or dependent PR."
  - "Authorized reviewer documentation maintenance includes STATE.md and docs/evidence/STATE-archive.md: completed historical records moved verbatim, original archive prefix and current rules preserved."
notes: |
  Serial g READY -> implementation IN_PROGRESS -> committed ACCEPTANCE_PENDING
  -> blocking review IN_PROGRESS; bounded g.1 READY -> implementation
  IN_PROGRESS -> committed ACCEPTANCE_PENDING -> fresh combined acceptance
  COMPLETE. Doer did not edit STATE or self-accept. Only the combined final
  tree at 47fa706 is accepted. Reviewer completed previously truncated mandatory
  reads in bounded chunks: full STATE/workflow/reviewer/incidents, relevant
  PROJECT/rules, approved spec, full runtime-probe source/evidence and Nautilus
  guide; exact original two-file implementation/tests and corrective diff read.
  Exact keyword-only signature/no defaults, key-based joined clocks, structural
  integer/grid/availability validation, admitted-only OHLCV and ns bounds,
  complete active/warmup coverage, warmup without exposure/scoring and explicit
  daily BTC capability match the contract. Excluded earlier/sentinel/later data
  never reaches engine; last eligible close alone values residual exposure.
  Live on_start and first-active clean queries fail on nonempty or unknown state.
  Actual fill membership checked before inherited snapshot replacement; first
  callback Exception retained, later callbacks abort and postrun guard prevents
  successful extraction even after deliberately swallowed dispatch. Finally
  disposes. Terminal open/inflight orders fail; genuine open positions remain
  disclosed without fabricated liquidation. Latest account rows independently
  value cash plus BTC; missing required currencies fail. Actual first fill/fee
  returns and ordinary daily runner control agree; ordinary source unchanged.
  Original volume 1000000000000.0001 was admitted but serialized to
  1000000000000.000122. Complete real public-run blocker evidence retained in
  /tmp/phase18g-review-blocker.log and /tmp/phase18g-review-report.md.
  Authorized g.1 changes only five OHLCV and initial-cash formatting sites to
  Decimal(str(value)); regression sees actual Quantity 1000000000000.000100,
  rejects observed original value, verifies all actual admitted OHLCV decimal
  equality, normal fill/fee/results and deep input immutability. No new API.
  Every exact final whole command independently passed. Single completed full
  pytest invocation used current enabled network permission with unchanged
  options/plugins/proxy/TLS; no dependency install or services. Earlier tool
  executions interrupted after cheap checks never started pytest and are not
  reported green. Original independent g pytest NOT RUN after confirmed blocker.
  Final raw logs: /tmp/phase18g1-review-ruff.log, -mypy.log, -pytest.log,
  -diff-check.log and -status-before.log. Full review report:
  /tmp/phase18g1-review-report.md. Original doer Ruff failures (25 then 2 E501)
  remain /tmp/phase18g-doer-ruff-1.log and -2.log; cosmetic wraps disclosed.
  Original doer 960-test pass is historical. Corrective doer first full suite
  961 passed,121 warnings in35.84s; no hidden test retry or weakened assertions.
  Current 121 warnings concern established Starlette httpx and Nautilus Pandas
  Timestamp.utcnow behavior, including added live-engine fixtures.
  Acceptance is local, not publication/merge. Coordinator verifies authorized
  corrected-g PR checks/merge before fresh next planning. Reviewer neither
  amends, pushes, creates PR, merges, launches workers nor edits implementation.
  Completed historical contract/evidence blocks are archived verbatim with a
  compact live reference table and explicit post-probe human approval retained.
  This supports mandatory full live-STATE reads without discarding evidence.
  Initial documentation diff check exited2 for a new blank line at archive EOF,
  inherited from the verbatim moved separator. Exact slice was preserved and
  an authored end-of-records marker appended; final diff check exit0. Raw
  /tmp/phase18g1-review-state-diff-check.log and -state-diff-check-final.log
  retain the initial diagnostic and final success. No historical bytes changed.
  Only supplied-clock consistency/runtime containment is accepted: no historical
  source availability/revision, frozen selection, evidence transport/binding,
  orchestrator/API/CLI/worker integration, research eligibility/OOS inspection,
  dependencies/gaps/windows or whole18.2/Phase18 completion. No future task is
  READY; remaining18.2 NOT_STARTED, next_task null, last_completed_task18.2g.1,
  human_transition_required false, Phase18 IN_PROGRESS. Never begin Phase29.
```

### 18.2h completion evidence

```yaml
task_id: 18.2h
status: COMPLETE
reviewer_decision: accepted_immutable_supplied_evidence_and_exact_content_identity_only
reviewer_date: 2026-10-04 Asia/Manila
git_commit_sha: a0d08e6aa2ff36ead2eac54dda698ea7ec5fb2a3
readiness_commit_sha: 2213ee19704c28514d1051a961f1a5b64cc76484
files_changed:
  - backend/src/quant/engine/research_input.py
  - backend/tests/engine/test_research_input.py
tests_added_or_updated: 173 new public-factory and detached-record cases
acceptance_commands:
  - .venv/bin/python -m ruff check .
  - .venv/bin/python -m mypy --strict backend/src
  - .venv/bin/python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 34 source files; exit 0"
  pytest: "1134 passed, 121 warnings in 38.53s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state maintenance; exit 0"
next_task: null
remaining_18_2_status: NOT_STARTED
human_transition_required: false
deviations: []
notes: |
  Serial READY -> implementation IN_PROGRESS -> committed ACCEPTANCE_PENDING
  -> independent acceptance COMPLETE. Doer never edited STATE or self-accepted.
  Reviewer read full live STATE/AGENTS/WORKFLOW/REVIEWER/INCIDENTS in bounded
  recovered reads, required PROJECT/spec/rules, actual two new files and relevant
  accepted clock/runner/read/store/fingerprint boundaries. Exact factory/interface,
  detached frozen slots/tuple/bytes, required fields/nulls, ordered fail/log behavior,
  signed unbounded clocks and finite numeric checks, claim-only provenance and raw
  chronological retention match the standalone contract. Independent manual typed
  fixture reconstruction agrees with complete hardcoded bytes; separate SHA-256
  matches df720d027a740232c362fc02a800b717083bc93c8144e219ebcb07ffc4d774f6.
  Int/float, negative zero, nearby floats, >4300-digit positive/negative clocks and
  OHLCV, Unicode and deep mutation isolation covered through actual public factory.
  One fresh full reviewer suite, no retries or implementation edits. Raw logs:
  /tmp/phase18h-review-ruff.log, -mypy.log, -pytest.log, -diff-check.log,
  -status-before.log and -independent.log. Reviewer report: /tmp/phase18h-review-report.md.
  Doer first full suite 1134 passed,121 warnings in38.72s is separate evidence.
  Doer retained Ruff failures (24 E501 then2) and one mypy literal-type failure
  in /tmp/phase18h-doer-*. Three corrective cycles preceded first full pytest;
  cosmetic wraps and explicit literal returns, no weakened tests or hidden retries.
  Warnings remain established Starlette httpx and Nautilus Pandas UTC deprecations.
  Acceptance certifies supplied consistency/content identity only: no authenticated
  publication/revision history, reproduced fixture capability, complete coverage,
  selection freeze/OOS inspection, runtime compatibility, evidence transport or
  orchestrator/API/CLI/worker integration, dependencies/gaps/windows, whole18.2 or
  Phase18 completion. Duplicate discarded JSON keys cannot be recovered by Mapping.
  Existing fingerprint and ordinary execution unchanged. No publication, merge,
  dependency install, worker launch or archive edits by reviewer. No future READY;
  current_task18.2 NOT_STARTED, last_completed_task18.2h, next_task null,
  human_transition_required false, Phase18 IN_PROGRESS. Never begin Phase29.
```

### 18.2h independent readiness contract — 2026-10-04 Asia/Manila

Independent plan review opens **ONLY 18.2h READY**. User's original post-probe
approval remains dated 2026-10-03; current delegation authorizes conservative
trustworthy choices within Phase 18, with independent gates and no phase crossing.
Baseline: clean `phase18/18.2h-input-snapshot`, refreshed main
`22da696ee3a1ed129a083acdb8945593595e0431`; origin main connectivity verified.
PR10 squash integrates the full accepted tracked tree: independent
`git diff --quiet a5be160 origin/main` exits 0. Original combined implementation
`47fa7068077952fe9894483ee373ab5873f000df` and reviewer
`a5be160409489991d1d2fecde7e807ad7cba0455` are not main ancestors (exit 1);
original published source branch/PR preserves their evidence history. No original
SHA ancestry is inferred from identical tree content. Coordinator verified PR10
merged with all three checks green and original remote branch at a5be160.

**Deliverables only:** new `backend/src/quant/engine/research_input.py` and
mirrored `backend/tests/engine/test_research_input.py`. Pure stdlib, no probe,
dependencies, caller/runtime/storage/API/CLI/UI/fingerprint changes. No exporter,
execution adapter, selection freeze, gaps/windows, source verification or eligibility
certification. Full live STATE, AGENTS, WORKFLOW, REVIEWER/INCIDENTS, required
PROJECT sections, confirmed spec, applicable rules and relevant accepted helpers,
runner/source/fingerprint code/tests reviewed. Detailed scratch plan is disposable;
this standalone contract governs implementation.

**Interface:** frozen slots dataclasses, direct construction unvalidated:
`InputProvenance(kind: Literal['controlled_fixture','researcher_attested','unknown'],
reference: str | None, declared_by: str | None)`;
`ResearchObservation(ts: int, close_ts: int, available_ts: int | None,
open: int | float, high: int | float, low: int | float, close: int | float,
volume: int | float, source_id: str, revision_id: str, provenance: InputProvenance)`;
`ResearchInputSnapshot(contract_version: str, rule_id: str, venue: str, symbol: str,
timeframe: str, calendar: str, anchor_ts: int,
observations: tuple[ResearchObservation,...], canonical_bytes: bytes, snapshot_id: str)`.
`create_research_input_snapshot(document: Mapping[str, object]) -> ResearchInputSnapshot`
is the sole validated factory; detached records/tuple/bytes have no mutable containers
or verified/eligible/frozen flags. Production docstring records wire and identity rules.

**Exact wire:** every declared field required; unknown keys rejected at document,
row and provenance levels. Top fields match snapshot metadata plus observations,
excluding canonical_bytes/snapshot_id. Fixed tokens in order: `research-input-v1`,
`phase18-temporal-v1`, `binance`, `BTC/USDT`, `1d`, `continuous_utc_fixed`.
Observations nonempty list/tuple of mappings, row fields exactly observation fields,
provenance exactly kind/reference/declared_by. Strings preserved without trim/case/
Unicode normalization; source/revision and required evidence/actor strings nonempty
valid UTF-8 without NUL or surrogates. Exact provenance enum, no inferred defaults.
Clocks signed unbounded int excluding bool; available_ts may explicit None.
Daily grid `(ts-anchor_ts)%86400000==0`, close_ts=ts+86400000;
known availability>=close, delays retained. No batch completeness/stage filtering.
All rows retained in strict chronological order; duplicate opens reject before
chronology after row validation, even equal duplicates; alternate revisions require
separate documents. OHLCV finite int/float excluding bool, prices>0, volume>=0,
high>=max(open,close), low<=min(open,close), high>=low. Integers intrinsically finite;
only floats use math.isfinite. No float coercion, rounding or precision bounds.

Unknown provenance requires reference/declared_by/availability all None.
Researcher-attested requires nonempty reference and actor; availability may unknown.
Controlled-fixture requires nonempty reference, actor None, known availability.
All source labels and references are claims, never authenticated truth. A future
trusted fixture importer must reproduce/bind rows before fixture capability can be
used; actual historical publication/revision verification remains separate work.
No reference fetching, availability inference from ingestion/open/close, or trust upgrade.

**New explicitly delegated v1 identity convention:** canonical identity document
contains validated detached wire fields, preserving row order; every numeric field
(anchor and row ts/close/known available plus OHLCV) becomes
`{'kind':'int','value':hex(value)}` (signed lowercase 0x) or
`{'kind':'float','value':value.hex()}`. None stays null. Raw input/record values remain
int/float. No unbounded bare ints in identity JSON, decimal-digit limit or global
runtime setting change. This is neither existing fingerprint nor inferred RFC format.
IEEE float content identity differs from runner's Decimal(str(value)) simulation
interpretation; snapshot certifies no execution compatibility. Serialize
`json.dumps(identity_document, sort_keys=True, separators=(',',':'),
ensure_ascii=False, allow_nan=False).encode('utf-8')`, no BOM/newline.
`snapshot_id='sha256:'+hashlib.sha256(canonical_bytes).hexdigest()`.
Int/float and signed zero distinct, exact nearby float values distinct. Mapping key
insertion order irrelevant; any valid field change alters content identity. Current
factory rejects unsupported version/rule. Existing fingerprint unchanged. Mapping
cannot detect already-discarded duplicate JSON keys; future parser must reject them
before mapping admission, no such claim here.

**Failure order:** exact document fields; ordered top tokens; anchor type;
observations container/nonempty; per-row mapping/exact fields; ts/close/available
types; grid/close equality/known availability; OHLCV type/sign in open/high/low/close/
volume order; OHLC bounds; source/revision text; provenance exact fields/kind/string
conditional constraints; duplicate then chronology. Canonicalize only after validation.
One ERROR on `quant.engine.research_input` and identical ValueError, success silent,
no payload/actor/reference leakage or broad exception/fallback. Paths use
`observations[i]` (nested `.provenance`). Exact templates:

- `<path> must contain exactly the declared fields` (document/row/provenance).
- `<field> must be <exact token>`; `anchor_ts must be an integer excluding bool`;
  `<path>.<clockfield> must be an integer excluding bool` (available permits None).
- `observations must be a nonempty list or tuple of mappings`;
  `observations[i] must be a mapping`.
- `<path>.ts must align with the declared daily grid`;
  `<path>.close_ts must equal ts plus one day`;
  `<path>.available_ts must be at or after close_ts`.
- `<path>.<pricefield> must be a finite positive int or float excluding bool`;
  `<path>.volume must be a finite nonnegative int or float excluding bool`;
  `<path> must have consistent OHLC bounds`.
- `<path>.<textfield> must be a nonempty UTF-8 string without NUL`.
- `<path>.provenance.kind must be controlled_fixture, researcher_attested, or unknown`;
  `<path>.provenance must match the declared kind and availability`.
- `<path>.ts duplicates an earlier observation`;
  `observations must be strictly chronological`.

**Tests:** hardcoded independent complete canonical bytes and known digest; insertion
order/repeat determinism; int/float/-0.0/nearby float identity; changed payload/clocks/
source/revision/provenance/reference identities; frozen nested records and deep caller
mutation isolation; duplicates/conflicting revisions/order; exact fields/nulls/types/
bool/NaN/inf/grid/OHLC; provenance/delays/claims without eligibility flags; UTF-8,
nonascii/surrogate/NUL; competing-invalid precedence and one exact redacted ERROR.
Arithmetic-built valid ints exceeding 4300 decimal digits must succeed in anchor,
clocks and OHLCV without coercion/runtime settings, including negative huge clocks.
Meaningful public factory coverage of private helpers; no redundant existing matrices.

**Acceptance from root, existing venv:** `python -m ruff check .`;
`python -m mypy --strict backend/src`; `python -m pytest backend/tests -q`;
`git diff --check`; `git status --short`. One completed full suite by doer and fresh
independent reviewer; repeats only justified by corrections/new failures. Preserve
complete failures/output, maximum five loops. One terminal implementation commit:
`feat(engine): preserve immutable research input evidence (Phase 18.2h)`.
Doer never edits STATE or self-accepts. Independent acceptance and separate STATE
commit precede coordinator-authorized PR/checks/merge verification and later readiness.
Readiness changed documentation only; Python suites not run under WORKFLOW §5.
Remaining 18.2 NOT_STARTED, 18.3/18.4 NOT_STARTED, Phase18 IN_PROGRESS,
next_task null, last_completed_task18.2g.1, human_transition_required false.

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

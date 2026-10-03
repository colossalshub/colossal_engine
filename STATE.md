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
last_completed_task: 18.2j
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

**18.2 — Enforce the approved stage windows** — NOT_STARTED as a whole.
18.2j is accepted for durable synthetic source and candidate capture only.
Selection/inspection barriers and runtime integration remain unimplemented.
No next task is READY; next_task null, Phase18 IN_PROGRESS.

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
- [x] **18.2i — Reproduce and bind controlled fixture inputs** — COMPLETE; deterministic synthetic recipe reproduction only, no historical source certification or runtime integration.
- [x] **18.2j — Append-only source and frozen candidate capture store** — COMPLETE; durable capture only, no selection/inspection barrier or runtime integration.
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
| 18.2i | `d7f5edc5f5fcb0fbd00e77347321b21d05259f72` | `5634a2e281fc199d262dd60b9649b662fce6395e` | 1165 passed, 123 warnings in 40.85s; reviewer completion `6ba8c10694a9733d756376f094446e4437a27687`; reproduced synthetic contents/clocks only | [Full historical record](docs/evidence/STATE-archive.md#182i-completion-evidence), [readiness](docs/evidence/STATE-archive.md#182i-independent-readiness-contract--2026-10-04-asiamanila) |
| 18.2g / 18.2g.1 | `47fa7068077952fe9894483ee373ab5873f000df` (original unaccepted `5a24edce407b4d3da75ee54c123ee14f0f928d3a`) | `568822e9adc6e96e9e8923ea2747875a8773e00f`, `8154fdebdbde089a95b8b6839df3a94eb73dc1aa` | 961 passed, 121 warnings in 40.42s; reviewer completion `a5be160409489991d1d2fecde7e807ad7cba0455`; supplied-clock/runtime containment only | [Full historical record](docs/evidence/STATE-archive.md#182g-and-182g1-combined-completion-evidence) |
| 18.2h | `a0d08e6aa2ff36ead2eac54dda698ea7ec5fb2a3` | `2213ee19704c28514d1051a961f1a5b64cc76484` | 1134 passed, 121 warnings in 38.53s; reviewer completion `31170fc`; supplied evidence/content identity only | [Full historical record](docs/evidence/STATE-archive.md#182h-completion-evidence), [readiness](docs/evidence/STATE-archive.md#182h-independent-readiness-contract--2026-10-04-asiamanila) |
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

### 18.2j completion evidence

```yaml
task_id: 18.2j
status: COMPLETE
reviewer_decision: accepted_durable_synthetic_source_and_candidate_capture_only
reviewer_date: 2026-10-04 Asia/Manila
git_commit_sha: a61fdc9e6841573daa14448509bcddfe93a09411
readiness_commit_sha: 47ca51ede7f5248bf396cfa5e5e481978d08fb19
files_changed:
  - backend/src/quant/data/research_store.py
  - backend/tests/data/test_research_store.py
tests_added_or_updated: 45 actual tmp_path SQLite persistence, replay, ordering, rollback and concurrency cases
acceptance_commands:
  - .venv/bin/python -m ruff check .
  - .venv/bin/python -m mypy --strict backend/src
  - .venv/bin/python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 36 source files; exit 0"
  pytest: "1210 passed, 123 warnings in 36.85s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer documentation maintenance; exit 0"
next_task: null
remaining_18_2_status: NOT_STARTED
human_transition_required: false
deviations:
  - "Authorized reviewer maintenance also touches docs/evidence/STATE-archive.md: exact 230-line i completion/readiness slice appended verbatim, original archive prefix preserved, compact live SHA/check references added. j readiness, approval and rules remain unchanged. No implementation deviation."
notes: |
  Serial independent acceptance of committed implementation; no doer STATE edits.
  Actual source/candidate code and tests checked against standalone j contract,
  mandatory startup/spec/rules and prior binder/input/coverage/runner boundaries.
  Same-transaction references, indexed columns, canonical replay, immutable
  revisions, server ordering, rollback and actual concurrent contenders accepted.
  One fresh whole reviewer suite, no failure, retry or implementation correction;
  enabled network/default sandbox/options/plugins/proxy/TLS unchanged.
  Complete logs /tmp/phase18j-review-{ruff,mypy,pytest,diff-check,status-before}.log;
  full review /tmp/phase18j-review-report.md. Doer1210/123/40.42s is separate.
  Doer initial Ruff53 then6 cosmetic diagnostics and both correction cycles
  retained in /tmp/phase18j-doer-ruff-{1,2}.log and doer report; no suite retry.
  Pre-first-suite bare JSON nonfinite/huge-number rejection and real replay
  regressions accepted; no failures lost or historical evidence corrected.
  Durable synthetic capture only, no selection/inspection/OOS barrier, runtime
  access gateway, authenticity, unseen market holdout, external-inspection or
  research-eligibility certification. Code identity remains caller assertion.
  No dependency, worker, publish, merge, next READY or whole-phase completion.
  current_task18.2 NOT_STARTED, last_completed_task18.2j, Phase18 IN_PROGRESS.
  Coordinator byte-validated exact slice/prefix, unchanged j contract/rules/approval
  and live SHAs before this separate completion commit. Initial docs diff check
  exit2: archive3423 new blank line at EOF; preserved historical bytes and added
  authored end marker, final docs diff check exit0. Raw diagnostic retained.
```

### 18.2j independent readiness contract — 2026-10-04 Asia/Manila

Independent readiness opens ONLY **18.2j READY**. Baseline clean branch
`phase18/18.2j-research-capture`, HEAD/refreshed main
`7011059bc50591635fb1f26ab176a7b0ca07e54c`. Independent `git ls-remote origin
refs/heads/main` returned that same SHA with the default sandbox and enabled
network. Coordinator verified PR12 merge after all three checks SUCCESS and
empty reviews/threads. Source implementation
`d7f5edc5f5fcb0fbd00e77347321b21d05259f72` and independent acceptance
`6ba8c10694a9733d756376f094446e4437a27687` are ancestors of HEAD (both exit 0);
tracked tree equals the accepted tree (`git diff --quiet 6ba8c10 HEAD`, exit 0).
Those original source SHAs remain evidence; the merge does not replace them.

Read full live STATE/AGENTS/WORKFLOW/REVIEWER/INCIDENTS in bounded chunks;
PROJECT stack, database contracts, execution, conventions, Phases16–18,
completion and AI rules; full confirmed Phase18 spec; project/backend rules;
accepted fixture binder, input canonical identity, coverage and runner parameter
contracts; existing stdlib SQLite connection/schema pattern. No unfamiliar
third-party calls or new dependency; no probe is required. Delegated trustworthy
routine decisions authorize the conservative supported contract below.
This standalone STATE contract governs implementation, not the disposable plan.
Original post-probe approval, full 18.2i readiness/completion and all history and
rules are preserved. No archive maintenance is part of this readiness task.

## Scope decision

Do NOT bundle first source capture, candidate contract, final selection, inspection admission and evaluation reservation state machine into one initial task. They require different acceptance invariants and would exceed a narrow reviewable store task. 18.2j creates usable durable source+candidate capture with actual DB ordering, not another unused pure helper. Immediately dependent18.2k extends THE SAME store with atomic selection/holdout inspection/reservation barrier before any runtime/API access integration.18.2j cannot claim OOS prevention; no frozenboolean substituted for authorization. No automatic nextREADY or wholephaseclaim.

ONLY new backend/src/quant/data/research_store.py and backend/tests/data/test_research_store.py. stdlibSQLite/json/hashlib/time + accepted fixture/input/temporal imports, no dependencies/probes. No meta_runs/schema/router/worker/runtime/UI changes. Single metadataSQLite database path supplied by caller, dedicated research_events_v1 table in that database, no separateDB singleton. Shared meta_runs integration later.

#### Public internal interface

Frozen slots StoredResearchEvent(seq:int, event_id:str, kind:Literal['input','candidate'], recorded_at_ts:int, canonical_bytes:bytes). Direct construction unvalidated, noeligibleflag.
init_research_schema(db_path:Path)->None
capture_fixture_input(db_path:Path, *, recipe:Mapping[str,object], document:Mapping[str,object])->StoredResearchEvent
freeze_research_candidate(db_path:Path, *, document:Mapping[str,object])->StoredResearchEvent
_read_research_event(db_path:Path, *, event_id:str)->StoredResearchEvent | None (PRIVATE helper; no public raw-source getter)

Private read is INTERNAL persistence replay only, not an exported researcher observation/API endpoint. Public capture returns internal persistence records for future guarded adapters; those records must not be serialized as unlogged API input dumps. Future external input/result access must go through18.2k transactionalinspection gateway; directDB access cannot be independently certified. Internal module does not infer researchers have inspected just by engine/privatevalidation reads. Docs say no publicrawobservationread path currentlyintegrated.

#### Input capture, canonical persistence

Every input capture CALLS bind_controlled_fixture(rawrecipe,rawdocument), never trusts suppliedrecords/hashes. Persist full accepted snapshot.canonical_bytes plus recipe's exacttypedhex canonicaldocument (samei convention) inside canonical inputeventpayload containing exactfields contract_version='research-store-input-v1',recipe,snapshot. Here recipe/snapshot are canonicaltyped JSON values decoded viajson.loads from independentlyvalidatedbyte representations; snapshot contains fullrawrowcontent typedhex, source/revision/provenance. All integers inclanchors preserved beyond4300digits, no strdecimal/globalsetting, int/floatkind/signedzero preserved. Inputevent canonical json.dumps(sort_keysTrue,separators(',',':'),ensure_asciiFalse,allow_nanFalse).encodeUTF8 noBOM/newline; event_id='sha256:'+SHA256(payload). Exactsnapshot_id reconstructible fromnested snapshotcanonicalbytes; store verifies reproduction every capture AND upon reading an inputevent (decode typedhex into rawrecipe/document then acceptedbinder). No referencefetch/newverifier. Meaningful local decoder exact declaredshapes/kinds; unknown tags reject, no broadfallback. Store malformed/tampered persistedpayload detected ratherthan silentlyrepaired. No inherited10gfingerprint substitution.

#### Frozen candidate document (delegated conservative supportedcontract)

Exactrequired topfields contract_version,rule_id,experiment_id,hypothesis_id,candidate_revision,parent_candidate_id,strategy_version,strategy,parameters,code_id,seed,fitted_artifacts,in_sample_input_id,in_sample_start_ts,in_sample_end_ts,trial_index,trial_count. Tokens research-candidate-v1,phase18-temporal-v1,strategy='buy_hold'. IDs/text nonemptyUTF8 withoutNUL/surrogates, no trim/case/Unicode normalization. parent_candidate_id explicitNone or existingcandidate event_id fromsameexperiment/hypothesis; previousrevision content neverupdated. candidate_revision opaque unique withinexperiment/hypothesis, cannot recapture changedcontent under same revision. code_id full40lowerhex gitcommit identity; capture binds callerassertion, runtime MUST compare actualexecutingcode later. strategy_version suppliednonemptystring, not label-as-certification.

parameters exactkeys starting_balance_usdt,trade_size,deploy_pct,maker_fee,taker_fee. Cash finitepositivefloat wholeUSDT; size positivefinite decimalstring exactly representable at6decimalplaces (accept '1', '1.0' and other admittedlexemes; no requirement exactly6writtenfractionaldigits), deployfinite decimalstring[0,1], feesfinite decimalstrings>=0, consistentacceptedrunnerconstraints. Preserve originalstringlexemes inidentity, no normalization: actualexecution must later use exactfrozenparams. Validate withstdlibDecimal/contextfree exactplace check; do not importresearch_runner privates/Nautilus. Integersforfees rejected; no numericdefaults.

seed explicitNone (deterministic supportedBuyHold), fitted_artifacts explicitemptylist/tuple (unsupported fittedmodels rejected). This records genuine applicabilityabsence; no optimizer/preprocessing/EMA support. in_sample_input_id existingcapturedinputevent in sameDB, reverifiedfixture contents, fullycovers complete IS range under acceptedvalidate_bar_coverage applied to exact closemembers. Raw source mayinclude laterobservations but candidatecapture only binds intendedIS membership; it does not grant research access to later observations. CompleteIS endpoints integerexcludingbool,start<end,oninputdailygrid. IS-onlycapture cannot select using validation/OOS implicitly. trial_index/count int excludingbool, countpositive, index1..count explicit. Count is declared plannedtrialbudget, NOT proof allconsideredtrials recorded; finalselection18.2k must enumerate actualconsideredcandidate IDs/criteria/results and checkconsistency. Finalselectionrecord not smuggled into candidatefreeze.

Canonicalcandidate contains exactwire fields; allnumeric values replaced acceptedtypedhexobjects (timestamps/trialints andcashfloat), seedNone/listempty retained, decimalstrings preserved. canonicalJSON sameexplicitconvention; event_idSHA256payload. Persist trueimmutable frozenparameters/code/input/lineage/trialdeclarations beforevalidationcandidate use. recordedserverseq later validationauthorization provesfreeze precedes inspection; callerbackdatedtimestamp cannot manufactureordering. No caller frozen_at/recorded_at field accepted.

#### Actual SQLite lifecycle

Table research_events_v1(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL UNIQUE,kind TEXT NOT NULL CHECK(kind IN('input','candidate')),recorded_at_ts INTEGER NOT NULL,payload BLOB NOT NULL). Candidate uniqueness separatecolumns experiment_id,hypothesis_id,candidate_revision nullableforinput; UNIQUE(experiment_id,hypothesis_id,candidate_revision). No otherfuturetablefamilies now. The fixed kindCHECK remains input/candidate. Future18.2k lifecycle operations use a separate append-only lifecycle table with its own serverorder, explicitly referencing source/candidateevent IDs; no attempt to ALTER this CHECK or silently repurpose kinds. A transaction covers both tables when enforcing the futurebarrier; capture seq and lifecycle seq are distinct domains, never compared as globalorder. Candidate existence under the same BEGINIMMEDIATE transaction proves prior committedfreeze. Add BEFOREUPDATE/BEFOREDELETE triggers RAISE(ABORT,'research events are append-only'); noUPDATE/upsert/REPLACE inpubliccode. This prevents applicationaccidentalmutation, not malicious directSQLiteowner edits. Actual payload+digest+kindverified whenreading.

Everyoperation opensshortlivedSQLiteconnection, WAL,busy_timeout5000, closesfinally; schemas initialized idempotently byeach publicentrypoint includingread to avoidmissingreadmigration trap. init ensuresparents Path.mkdir. Mutations BEGINIMMEDIATE, validate foreignparent/input and uniqueness inside samewritetransaction, capturewallclock usingtime.time_ns()//1000000, insert, COMMIT; exceptionROLLBACK and propagate. DBseq authoritative committedserialization order, clockwallms supplemental can repeat/go backwards. No backdating argument/clampedfabricatedtime. Identicalsamekindpayload re-capture is idempotent returnoriginalevent (samefreeze, seq/timestamp); changedrevisionpayload rejects, no overwrittenrecord. Capturevariantinput differentrecipe/payload distinctevents. Failurebeforecommit no orphancandidate; concurrentduplicatecaptures oneevent; concurrentrevisionconflict exactlyonewinner, otherexplicitfailure. Read payload hash/canonicalencodingvalidity and requiredkind thenrevalidate source/candidate references; no treating externallymodifieddataastrusted. Test SQLiteoperationerrorrollback without swallowing/loggingduplicateframeworkerrors.

#### Errors/tests

Ownvalidation errors oneERRORquant.data.research_store plusidenticalValueError; acceptedbinder/coverageerrors propagateonceunwrapped. Private missingread returnsNone. No arbitrarypayloadinerrors; any SQLiteoperationalfailure propagatesoriginal without silentadaptation.

Exact candidate failureorder/messages:
1. CandidateMapping/exacttopkeys: `candidate must contain exactly the declared fields`.
2. contract_version,rule_id,strategy exacttokens in thatorder: `<field> must be <token>`.
3. experiment_id,hypothesis_id,candidate_revision,strategy_version,in_sample_input_id text in thatorder: `<field> must be a nonempty UTF-8 string without NUL` (surrogatesreject). parent_candidate_id: None or sametexttype with `parent_candidate_id must be null or a nonempty UTF-8 string without NUL`. code_id then requires str/fullmatch `[0-9a-f]{40}`: `code_id must be a 40-character lowercase hexadecimal git commit ID`. This is a callerassertedcodebinding, neverauthentication; runtimecomparesactualcode.
4. parametersexactkeys/Mapping: `parameters must contain exactly the declared fields`. Cash type/finite/positive/whole: `parameters.starting_balance_usdt must be a finite positive whole-USDT float`. Do not roundcash. Decimal lexical validation in trade_size,deploy_pct,maker_fee,taker_fee order: `parameters.<field> must be a finite decimal string` (strrequired, DecimalInvalidOperation/nonfinite rejected). For eachvalue immediately check constraints: `parameters.trade_size must be positive and exactly representable at 6 decimal places`; `parameters.deploy_pct must be between zero and one`; `parameters.maker_fee must be nonnegative`; `parameters.taker_fee must be nonnegative`. Use runner-equivalent contextfree digit/exponent/trailingzero representability: accepts size'1' and harmless extra zeroes, preserves originallexemes; no stricter inputformat imposed.
5. seedmustNone and fitted_artifacts emptylist/tuple: `seed and fitted_artifacts must be explicitly absent for buy_hold`. Emptycontainers canonicalize to JSONemptylist, declared applicabilityabsence ratherthanmodeltrust.
6. in_sample_start_ts,end_ts types in order: `<field> must be an integer excluding bool`. start<end: `in_sample_start_ts must be less than in_sample_end_ts`. trial_index/count types in order sameintegererror; count>0: `trial_count must be positive`; index1..count: `trial_index must be between one and trial_count`.
7. BEGINIMMEDIATE resolves input first: missing/wrongkind -> `candidate input event does not exist`. Sourceintegrity/binderfailures propagate existingvalidationonce. Check ISstart thenend congruence to capturedanchor: `in_sample_start_ts must align with the declared daily grid`; `in_sample_end_ts must align with the declared daily grid`. Select exact ISclosemembers and call acceptedcoveragehelper; completecount/empty/rowerrors use its exactmessages, no relog. Later/contextrows retained in sourcepayload but not allowedselectionmembership.
8. Optionalparent then resolves: missing/wrongkind -> `parent candidate event does not exist`; presentdifferentexperiment/hypothesis -> `parent candidate does not match experiment and hypothesis`. Then candidate_revisionuniqueness: samecanonicalid returns originalevent, changedcontent under sameexperiment/hypothesis/revision -> `candidate revision already has different frozen content`.
9. Persist/replay malformedencoding/digest/kind -> `stored research event failed integrity validation`. Validlyencodedstoredsource/candidate revalidation that fails acceptedfactory/helper propagates that firsterroronce; do not log integritywrapper in addition. No handwaving unspecified messages atreadiness.

Focusedactualtmp_pathSQLitetests: roundtriprawfixture+candidate exactcanonicalpayloads/knownIDs; reopenedstore durable; idempotentseq; changedcode/params/input WITH NEWcandidate_revision captures distincteventid; changedcode/params/input under SAMEcandidate_revisionrejects with exactfrozencontenterror; samecontent/samerevisionidempotent; parentwronggroup/missingreject; nonIS/missingcoverage/invalidtrial/unsupportedartifacts/seed reject beforecandidateinsert. Typedhex hugeintegerinputroundtrip and no10gfloatcollision; capture tamperedsource failsactualbinder beforeinsert. Triggerupdate/deletereject, corruptionreadonlyvalidationfail; internalread has nocertification/eligibility flag. actualserverseq independentofmonkeypatchedbackwardwallclock; twoSQLiteconnections/threads contenders oneidempotentevent and revisionconflict no partialrows, deterministicbarriers no timingassertion. Injectcommit/inputvalidationfailure rollback withoutswallowing. Noexhaustivetype/helpermatrix, noactualengine needed; no DB writesoutside tmp_path.

#### Acceptance and next mandatory barrier

Rootexistingvenv exact .venv/bin/python -m ruff check .; .venv/bin/python -m mypy --strict backend/src; .venv/bin/python -m pytest backend/tests -q; git diff --check; git status --short. Onecompletedwholepytest doer andfreshreviewer, repeats onlynewfailure/correction. Enablednetworkuse_default, noinstalls/frontendchanges/checks. Completeoutputs/failuresretained max5loops. One terminalcommit feat(data): capture immutable research inputs and candidates (Phase 18.2j). Independentacceptance/separateSTATE beforeauthorizedPRmerge andnextfreshreadiness.

Immediatelynext storeextension adds a separate append-only lifecycle table (source kindCHECK unchanged) and MUST enforce: enumerateconsideredtrials and exactselectioncriteria/selectiondataidentity; candidatefrozen beforeANYvalidationaccess; finalselectionfrozen beforeANYholdoutobservations/resultsaccess. Register exactholdout identity(boundactualsourcekeys/range, preventrenamedoverlap escape), record manualinspection declaredtime separately fromserverseq. BEGINIMMEDIATE serialization for finalselectionfreeze vsinspection/evaluationreservation, inspectionofsame/overlappingactualobservations blocks laterselection/revision usingthatuntouchedholdout; requiresnewunseenholdout. Exactrerun distinctreservation/resultpreserved, markedreproducibilitynotindependent. No finalselection authorization until this extension accepted. Then gateway/API/CLI/worker bindactualcandidateparams/code+fixture at runtime and every publicresult/inputread logsinspectiontransaction.18.2j completion certifiesdurablecapture only; no actualOOSbarrier yet, no implicitphasecompletion.

Synthetic recipe generation is predictable to its author. Neither candidate capture nor the later inspection barrier certifies an unseen market holdout, secret data, independent evidence or absence of external inspection. Supported claims stay reproducible synthetic contents and software temporal/access mechanics, separately from researcher declarations. Later holdout contamination keys must bind actual source/revision lineage and observation membership, including overlaps across renamed snapshots/revisions; a new hash alone cannot erase inspection.


#### Explicit integrity and transaction refinements

Every persisted input row must have null experiment_id, hypothesis_id and
candidate_revision columns. Every candidate row must have those three columns
exactly equal to the corresponding decoded canonical payload fields. Read and
reference replay checks this as part of integrity validation before trusting the
uniqueness index. A payload digest alone cannot certify those indexed columns.
Tests tamper an indexed column as well as payload/digest/kind.

Canonical JSON parsing and exact re-encoding must reproduce persisted bytes;
duplicate keys, noncanonical JSON and noncanonical typed-hex spellings fail with
`stored research event failed integrity validation`. Decode integers using
`int(value, 16)` and floats using `float.fromhex(value)`, only at the exact
contract numeric positions and with exact kind/value shapes. Re-encode using
`hex(integer)` / `float.hex()`; unknown tags or wrong numeric kinds fail, with
no decimal conversion limit, coercion or global setting change. Semantic
accepted binder/coverage failures still propagate once unchanged. Candidate
replay rebuilds the exact validated canonical payload and verifies equality;
empty fitted-artifact tuples canonicalize to JSON lists as declared above.

All reference lookup, integrity replay, uniqueness resolution and insertion
inside a mutation use that same connection and BEGIN IMMEDIATE transaction.
An internal connection-taking replay helper is permitted. Do not call the
path-taking private read helper from inside a write transaction or open another
connection for reference validation. Read replay detects recursive candidate
lineage cycles and fails integrity validation; accepted parent references must
resolve to earlier committed candidates, not newly fabricated self/cyclic links.
No digest/trigger/sequence/timestamp mechanism authenticates a malicious direct
SQLite owner. Server sequence proves application commit order only.

Readiness changed STATE only. No Python files changed; pytest/ruff/mypy were
not rerun under WORKFLOW §5. No implementation, suites, installs, workers,
push, merge or automatic next readiness. last_completed_task remains18.2i;
remaining18.2 NOT_STARTED, 18.3/18.4 NOT_STARTED, next_task null,
human_transition_required false and Phase18 IN_PROGRESS. Never begin Phase29.

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

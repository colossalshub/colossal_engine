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
last_completed_task: 18.2i
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

**18.2i — Reproduce and bind controlled fixture inputs** — COMPLETE.
Independent acceptance certifies reproduced synthetic contents/clocks only.
Remaining 18.2 as a whole remains NOT_STARTED, next_task null, Phase18
IN_PROGRESS; no next implementation task is open.

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

### 18.2i completion evidence

```yaml
task_id: 18.2i
status: COMPLETE
reviewer_decision: accepted_reproduced_synthetic_fixture_contents_and_clocks_only
reviewer_date: 2026-10-04 Asia/Manila
git_commit_sha: d7f5edc5f5fcb0fbd00e77347321b21d05259f72
readiness_commit_sha: 5634a2e281fc199d262dd60b9649b662fce6395e
files_changed:
  - backend/src/quant/engine/research_fixture.py
  - backend/tests/engine/test_research_fixture.py
tests_added_or_updated: 31 focused public generation, binding, error and actual-engine cases
acceptance_commands:
  - .venv/bin/python -m ruff check .
  - .venv/bin/python -m mypy --strict backend/src
  - .venv/bin/python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 35 source files; exit 0"
  pytest: "1165 passed, 123 warnings in 40.85s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer state maintenance; exit 0"
next_task: null
remaining_18_2_status: NOT_STARTED
human_transition_required: false
deviations:
  - "Authorized reviewer documentation maintenance also touches docs/evidence/STATE-archive.md: the exact 287-line g/g.1 completion, h completion and h readiness slice is appended verbatim; original archive prefix, post-probe approval, i readiness contract and current rules preserved. Compact live SHA/acceptance references replace moved records. This is reviewer-only scope, not a doer/readiness scope expansion."
notes: |
  Serial READY -> implementation IN_PROGRESS -> committed ACCEPTANCE_PENDING
  -> independent acceptance COMPLETE. Doer never edited STATE or self-accepted.
  Reviewer read full live STATE/AGENTS/WORKFLOW/REVIEWER/INCIDENTS in bounded
  chunks, required PROJECT/spec/rules and Nautilus guide, exact two new files,
  accepted snapshot factory and relevant runner boundary implementation.
  Exact no-default recipe fields, ordered integer/grid/positive-price checks,
  signed unbounded integers, explicit synthetic zero-delay rows and typed-hex
  recipe identity match the contract. Binder regenerates first, validates raw
  supplied document second, compares canonical bytes AND snapshot ID third,
  and returns fresh expected snapshot only after equality. Factory failures
  propagate once unchanged. No direct-record/label/hash trust shortcut or flags.
  Independent literal recipe reconstruction verifies recipe SHA-256
  9ef687c70741b00dba743e2dbc8de911cd26b70392d837e5a21c224ca1b04c44;
  complete hardcoded rows/clocks/provenance and separate content reconstruction
  verify snapshot SHA-256
  468fd3da9955a653d0398d67c561f534bd36c6109322a707a730f86bd4e7739d.
  Actual-engine integration sees first fill100, fee0.1 and last eligible price120,
  ending equity100019.9; later generated price140 excluded by explicit interval.
  Tampered payload/source/revision/reference/delay/anchor/count/numeric kind
  cannot bind despite valid supplied recomputed identity. Huge integer clocks,
  prices and volume, signed steps, mutation isolation, exact logs and failure
  precedence are covered. No implementation correction or acceptance retry.
  One fresh completed whole reviewer pytest invocation used unchanged enabled
  network/default sandbox/options/plugins/proxy/TLS. Raw complete logs:
  /tmp/phase18i-review-ruff.log, -mypy.log, -pytest.log, -diff-check.log,
  -status-before.log and -independent.log. Report /tmp/phase18i-review-report.md.
  Doer first full suite1165 passed,123 warnings in36.37s is separate evidence.
  Initial doer Ruff failed4 diagnostics (import formatting and3 E501); cosmetic
  authorized-file formatting repaired them before first pytest. Raw initial
  failure remains /tmp/phase18i-doer-ruff-1.log; doer report and final logs retained.
  Established warnings concern Starlette httpx/Nautilus Pandas UTC deprecations.
  Acceptance certifies synthetic reproduction only, never actual historical
  origin/publication/revision history, frozen selection/OOS inspection, causal
  dependencies, realistic execution, research eligibility, runtime gateway,
  evidence transport/store/API/CLI/worker integration, gaps/windows or whole18.2
  or Phase18 completion. Future runtime must call binder on raw recipe+document.
  No dependencies, files/network in generator, globals, count cap or invented
  experiment numeric defaults. No publish/merge/workers or implementation edits.
  Reviewer documentation maintenance is separately authorized for efficient
  mandatory live-state reads; no historical correction or failure removal.
  Coordinator independently byte-verified exact slice relocation, unchanged
  archive prefix, approval, i contract/rules tail and live SHA references before
  this separate completion commit; documentation diff check exit0.
  No next READY; current_task18.2 NOT_STARTED, last_completed_task18.2i,
  next_task null, human_transition_required false, Phase18 IN_PROGRESS.
  Coordinator verifies authorized PR/checks/merge before fresh next readiness.
  Never begin Phase29.
```

### 18.2i independent readiness contract — 2026-10-04 Asia/Manila

Independent readiness opens **ONLY 18.2i READY** after accepted 18.2h and
coordinator-verified PR11 merge with all three checks SUCCESS, no reviews or
review threads. Baseline clean `phase18/18.2i-controlled-fixtures`, HEAD/refreshed
main `559d48ab7e353d8d745af30f1e169aacd4b9daa2`; independent origin connectivity
returned that exact main SHA. `git diff --quiet 31170fc origin/main` exit 0;
`git merge-base --is-ancestor a0d08e6 HEAD` and the same command for `31170fc`
exit 0. Preserve implementation `a0d08e6aa2ff36ead2eac54dda698ea7ec5fb2a3`
and acceptance `31170fc` evidence; merge does not replace original SHAs.
User delegation authorizes these conservative explicit synthetic wire choices.
Original post-probe approval and all historical evidence remain unchanged.

Full live STATE/AGENTS/WORKFLOW/REVIEWER/INCIDENTS, required PROJECT stack,
data/execution/conventions, Phases16–18, §§7–8, confirmed Phase18 specification,
applicable project/backend rules and accepted factory/runner contracts reviewed.
No unfamiliar third-party call: stdlib generation and accepted public factory;
one integration test copies the existing accepted research runner call pattern.
No probe, install, worker, push or implementation in this readiness review.
Scratch plan is disposable; this standalone contract governs the task.

**Deliverables only:** new `backend/src/quant/engine/research_fixture.py` and
mirrored `backend/tests/engine/test_research_fixture.py`. Use stdlib and absolute
imports of accepted `create_research_input_snapshot` / `ResearchInputSnapshot`.
No changes to existing helper/runner/caller/store/API/CLI/UI/fingerprint, protected
files, dependencies or archive. No exporter, plugin/callback, arbitrary fixture
file/URL/reference fetching, selection freeze, gap/window enforcement or workers.

**Exact public interface, no defaults:**
`create_controlled_fixture(recipe: Mapping[str, object]) -> ResearchInputSnapshot`;
`bind_controlled_fixture(*, recipe: Mapping[str, object],
document: Mapping[str, object]) -> ResearchInputSnapshot`.
Create actual deterministic rows, then validate them with the accepted factory.
Bind regenerates expected FIRST, validates supplied raw document independently
through that same factory SECOND, compares both canonical_bytes and snapshot_id
exactly THIRD, and returns only the freshly generated expected snapshot after
matching. Never return/trust supplied or directly constructed records, unchecked
bytes, caller labels, opaque hashes, references, eligible/source_verified flags
or a verifier callback. Production docstring states the complete contract.

**Exact required recipe fields:** recipe_version, rule_id, anchor_ts,
start_open_ts, observation_count, price_start, price_step, volume; no omissions,
defaults or extra keys. Exact tokens `controlled-daily-linear-v1` and
`phase18-temporal-v1`. Remaining fields signed unbounded int excluding bool;
count>0, price_start>0, volume>=0. Signed price_step permitted. Require
`(start_open_ts-anchor_ts)%86400000==0` and
`price_start+(observation_count-1)*price_step>0`; linear endpoints ensure every
price is positive. No invented anchor/calendar/warmup/gap inputs, count cap,
decimal-digit limits, global settings or float coercion. Producing rows costs
O(count); no resource-bound or execution-compatibility claim at this pure layer.
Change recipe contract version if generation semantics change.

**Recipe identity:** dictionary of all exact validated recipe fields, version
and rule strings unchanged, EVERY integer replaced by
`{'kind':'int','value':hex(value)}`. Canonical bytes are
`json.dumps(identity, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
allow_nan=False).encode('utf-8')`, no BOM/newline; recipe_id is `'sha256:'` plus
lowercase SHA-256 digest. Uses the accepted typed-hex convention, never existing
fingerprint. Identity binds a recipe, not authenticity.

**Exact generated raw document:** required top fields contract_version
`research-input-v1`, rule_id `phase18-temporal-v1`, venue `binance`, symbol
`BTC/USDT`, timeframe `1d`, calendar `continuous_utc_fixed`, explicit recipe
anchor_ts, observations list. For `i in range(observation_count)`,
`ts=start_open_ts+i*86400000`, `close_ts=ts+86400000`,
`available_ts=close_ts`, `price=price_start+i*price_step`; raw open/high/low/close
all that integer price, volume exact recipe integer. Exact row fields are ts,
close_ts, available_ts, open, high, low, close, volume, source_id, revision_id,
provenance. Fixed source_id `controlled-fixture:controlled-daily-linear-v1`,
revision_id recipe_id, provenance exactly
`{'kind':'controlled_fixture','reference':recipe_id,'declared_by':None}`.
These namespaces and zero-delay clocks are explicit synthetic generator
DEFINITIONS, never inferred real-market availability or source history. No
randomness, rounding, network, files or real source data. Generated range is
nonempty and complete on its own explicit grid; no stage/window coverage claim.
Integer 100 and float 100.0 deliberately have different accepted content identity.

**Trust boundary and limitations:** internal deterministic code plus explicit
recipe and exact comparison certify only reproduced synthetic contents/clocks.
A caller may choose a different recipe and legitimately generate different
synthetic data. Even historical-looking prices supplied as recipe inputs do not
certify historical origin, publication or revision history. Caller-controlled
controlled_fixture labels/references alone cannot qualify arbitrary input.
Future runtime gateway must CALL this binder on raw recipe+document at execution,
not trust a transported type/flag/hash. This task does not wire that gateway,
certify selection/OOS inspection, realistic execution, causal dependencies,
research eligibility, real historical availability, or complete 18.2/Phase18.

**Own failures:** exactly one ERROR on `quant.engine.research_fixture` and an
identical ValueError; no input serialization/payload leakage, success silent.
Accepted factory errors propagate once unchanged, never wrapped or re-logged.
Order: exact fields; recipe_version; rule_id; integer types in anchor_ts,
start_open_ts, observation_count, price_start, price_step, volume order; positive
count; positive starting price; nonnegative volume; start alignment; final price.
Then supplied document validation and exact match. Exact error messages:

- `recipe must contain exactly the declared fields`
- `recipe_version must be controlled-daily-linear-v1`
- `rule_id must be phase18-temporal-v1`
- `<field> must be an integer excluding bool`
- `observation_count must be positive`
- `price_start must be positive`
- `volume must be nonnegative`
- `start_open_ts must align with the declared daily grid`
- `generated prices must all be positive`
- `document does not match the reproduced controlled fixture`

**Focused public tests:** hardcoded three-row recipe expected rows, clocks,
provenance, independently reconstructed complete recipe identity and expected
snapshot identity; repeat/insertion-order determinism; zero/negative steps valid,
negative final price rejected; shifted anchor; huge signed clocks and integer
prices beyond decimal conversion limit preserved; no generated None availability;
deep caller mutation isolation. Independently rebuild supplied raw wire from the
recipe, not private helpers; bind matches and returns a fresh expected snapshot.
Tamper prices/source/revision/reference/delay/anchor/row count/numeric kind and
recomputed supplied hash cannot bypass exact comparison. Fake labels/opaque
hashes fail. Representative missing/extra/duplicate/out-of-order supplied rows
propagate accepted factory behavior and only one log. Cover recipe types/bool,
count/grid/tokens, exact fields and competing-invalid precedence without repeating
existing broad matrices. No dataclass shortcut or real data writes.

One meaningful actual-engine integration case imports existing
`run_research_buy_hold`, `BarClock`, `ResearchInterval` and copies accepted calls.
Use increasing integer prices, bound reproduced rows projected to ts/OHLCV and
explicit reproduced clocks; explicit active interval, warmup=None,
required_warmup_observations=0, timeframe/calendar/anchor, cash=100000.0,
trade_size='1', deploy_pct='0', maker_fee=taker_fee='0.001'. Assert actual first
fill clock/fee and residual valuation at the last eligible close. Source/payload
tampering must fail binding before an engine call. Assert synthetic-only claim
limits and absence of eligibility flag. No new Nautilus API, orchestration wiring,
mock-only execution proof or repeated full engine admission matrices.

**Acceptance from root using existing venv:**
`.venv/bin/python -m ruff check .`;
`.venv/bin/python -m mypy --strict backend/src`;
`.venv/bin/python -m pytest backend/tests -q`;
`git diff --check`; `git status --short`.
One completed full suite each doer/fresh independent reviewer; repeat only after
new failure/correction. Retain raw complete outputs/failures; maximum five loops.
Use current enabled network with unchanged options/plugins/proxy/TLS. No frontend
checks or installs. One terminal implementation commit:
`feat(engine): reproduce controlled research fixtures (Phase 18.2i)`.
Doer never edits STATE or self-accepts/publishes. Serial READY -> IN_PROGRESS ->
ACCEPTANCE_PENDING -> independent acceptance COMPLETE with separate STATE commit;
coordinator verifies authorized PR/checks/merge before fresh next readiness.
Readiness changes STATE only; no Python files changed, pytest/ruff/mypy not rerun
under WORKFLOW §5. Remaining18.2 as a whole NOT_STARTED, 18.3/18.4 NOT_STARTED,
next_task null, last_completed_task18.2h, human_transition_required false,
Phase18 IN_PROGRESS. No automatic phase crossing; never begin Phase29.

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

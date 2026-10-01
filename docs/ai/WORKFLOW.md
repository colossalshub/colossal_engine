# WORKFLOW.md

Companion to `PROJECT.md`. This is the **execution playbook**, not the permanent project specification.

## 0. Agent Startup Protocol — READ FIRST

Before planning, editing, coding, testing, or committing anything:

1. Read `STATE.md`.
2. Read the relevant sections of `PROJECT.md`.
3. Read this file.
4. Read `docs/ai/REVIEWER.md` when preparing acceptance evidence or a completion report.
5. Read applicable `.cursor/rules/*.mdc` files.
6. Determine `current_phase`, `current_task`, and status from `STATE.md`.
7. Verify the repository is consistent with that state before changing anything.

**Never infer current phase from memory, chat history, README text, commit messages, old audit reports, or filenames.**

If documentation and repository evidence disagree, STOP and use the conflict protocol in `STATE.md`.

### Authority hierarchy

1. Explicit human decision in the current task
2. `STATE.md` for current execution state
3. `PROJECT.md` for permanent specification and phase requirements
4. `docs/ai/WORKFLOW.md` for execution procedure
5. `docs/ai/REVIEWER.md` for acceptance/review procedure
6. `.cursor/rules/*.mdc` for local code-style rules
7. README/old reports for descriptive context only
8. Agent memory/inference — **never authoritative**

---

## 1. Model selection

The right model depends on the task, not the phase. Use this table.

| Task type | Model | Effort | Notes |
|---|---|---|---|
| Scaffolding, boilerplate, config | Composer 2.5 | Default | Fast OFF always |
| Single-file logic with clear spec | Composer 2.5 | Low | Most Phase 1–2 tasks |
| Contract files (schemas, types) | Claude Sonnet 5 | Medium | `schemas.py`, `types.ts` |
| Multi-file routers, DB wiring | Claude Sonnet 5 | Medium | `get_tearsheet`, pagination |
| Complex UI (LWC crosshair, SVG) | Claude Sonnet 5 or Opus | High | `BaseChart.tsx`, `MonthlyHeatmap.tsx` |
| Hard debugging | — | — | See the escalation ladder in §8 (Composer → Grok Medium → Grok High → STOP) |
| API probing (Stage 1) | Composer or Codex CLI | Low | Read-only, no judgment needed |

**Always turn Fast OFF.** Fast costs ~6× for lower latency only — never worth it unless you're actively watching the response stream.

**Never start at Max/Extra High.** Escalate only after lower effort fails.

**Composer's failure mode:** it "improves" specs by normalizing field names, dropping "redundant" validators, or adding "helpful" extras. This is why contract files get Sonnet.

---

## 2. Two-stage prompt pattern

Any task that touches a third-party API (Nautilus, ccxt, pyarrow, FastAPI) gets split into two stages:

**Stage 1 — probe.** Import checks, `inspect.signature`, docstring dumps, live object probes with progressively more kwargs. Report everything verbatim. STOP.

**Human approves.** Adjust Stage 2 based on what the probe found.

**Stage 2 — implement.** Exact calls, pre-verified. If a call fails at runtime, STOP — do not silently adapt.

This pattern saved Phase 2.2 (Nautilus engine construction), Phase 2.2.2 (`portfolio.equity` signature), and Phase 2.4 (Money-string formats). Without it, each task would have been 2 hours of `AttributeError` whack-a-mole.

---

## 3. Phase-splitting rules

- **One file + one test = one commit.** Split if larger.
- If a task needs schema creation + orchestration, split into `.1` / `.2a` / `.2b`.
- If a task needs a bug fix in a prior phase's file to proceed, split into the fix phase + the original phase.
- Documentation and small fixes get suffixes: `Phase 3.1.1`, `Phase 2.2.3`, `Phase 2.1.2`.
- **Commit message format:** `<type>(<scope>): <description> (Phase X.Y)`
  - `<type>` ∈ {feat, fix, docs, chore, refactor, test, style, perf, build, ci}
  - `<scope>` is the module: strategy, engine, extract, api, ui, data, docs
  - `<description>` is imperative mood, lowercase, no trailing period
  - `(Phase X.Y)` is the roadmap linkage; omit for `docs:` and `chore:`
    commits that don't map to a specific phase
  - Examples:
    - `feat(strategy): reject non-BTC instruments before engine construction (Phase 12.1)`
    - `fix(extract): use last row per currency in account report (Phase T.4.1)`
    - `docs: sync PROJECT.md with trust-pass behavior`

---

## 4. Git discipline

- **Never use Cursor's commit UI.** Rule 13. It holds a stale `.git/index.lock` and throws 500 errors. Commit from the terminal.
- **Never let the agent amend without approval.** If it discovers a fix during acceptance, it STOPs and reports. The human decides: amend, fold in, or new mini-phase.
- **One commit per task.** If `pyproject.toml` needs updating mid-task, either include it in the same commit (and note in the report) or create a mini-phase — never an unexplained extra commit.
- **The trailer.** Cursor injects `Co-authored-by: Cursor <cursoragent@cursor.com>` on every commit. Accept it. Fighting it costs more than it saves.

---

## 5. Acceptance discipline (rule 10)

- Acceptance commands run **from the repo root, on the whole tree**, exactly as written in the task prompt.
- Never run on a subset of files.
- If a check fails, report the failure verbatim — **do not silently fix and report green**.
- This rule exists because Phase 1.1 reported `ruff check .` green when the file used `datetime.timezone.utc` (UP017 violation). Phase 1.2's full-tree run caught it. If the rule had been in place earlier, the fix would have been in the original commit.
- **Path-scoped acceptance.** When a task's diff touches no files under `backend/` or `scripts/`, the Python acceptance commands (`pytest`, `ruff`, `mypy`) may be skipped. The report must say so in one line, e.g. "No Python files changed; pytest/ruff/mypy were not re-run." This does not relax whole-tree discipline for any acceptance command whose scope the diff *does* touch — frontend diffs still require `tsc -b`, `vitest run`, and `npm run build` on the whole tree.

**Frontend TypeScript (from `frontend/`):**

Note: the root `tsconfig.json` uses project references with `"files": []`. Plain `npx tsc --noEmit` checks nothing. Use `npx tsc -b`.

`tsc -b` follows project references and type-checks every file under `src/`, including test files. The referenced configs already set `noEmit: true`, so `-b` doesn't write output — it's a pure check.

- Standard frontend type-check: `npx tsc -b`

---

## 6. Task-specific guides

Load these only when the task touches the named subsystem:

- [`guides/nautilus.md`](guides/nautilus.md) — Nautilus construction,
  reports, timestamps, tear-sheet lifecycle, and Rust-bridge logging.
- [`guides/frontend-tooling.md`](guides/frontend-tooling.md) —
  Lightweight Charts and AG Grid version-specific behavior.

---

## 7. API JSON contract (from `PROJECT.md` §4.4)

Enforced by `backend/src/quant/api/schemas.py` (Phase 3.1). Any field nullability there is the ground truth — if `PROJECT.md` §4.4 disagrees, the schema is correct and §4.4 is stale.

Known §4.4 typo fixed in Phase 3.1.1: `KpiBlock` fields are all `number | null`, not `number`.

---

## 8. Debugging escalation

Use the following escalation path when a task fails:

1. **Composer**

   * Provide the full failing output.
   * Do not summarize or omit relevant errors.
   * Allow up to **2 debugging attempts**.

2. **Grok Medium**

   * If Composer fails twice, switch to Grok Medium.
   * Provide the full current failure state and relevant changes.
   * Allow up to **2 debugging attempts**.

3. **Grok High effort**

   * If Grok Medium fails twice, escalate to Grok High effort.
   * Re-evaluate the implementation approach rather than blindly repeating the same fix.

4. **STOP and reassess**

   * If Grok High effort still fails, stop implementation.
   * Do not keep cycling models indefinitely.
   * Determine whether the problem is caused by:

     * an incorrect implementation approach;
     * an incorrect assumption;
     * an architectural conflict;
     * an incomplete or contradictory specification;
     * a dependency/tooling issue;
     * a repository-state issue; or
     * a genuine unresolved defect.

5. **Optional second opinion**

   * Codex CLI may be used as an independent second opinion if available.
   * The second opinion must review the actual failure and repository state rather than simply attempting another blind fix.
   * A second opinion does not reset the task's failure count.

### Hard execution limit

A task may consume at most **5 implementation/debugging loops** before requiring human intervention.

The intended escalation is therefore:

```text
Composer attempt 1
        ↓
Composer attempt 2
        ↓
Grok Medium attempt 1
        ↓
Grok Medium attempt 2
        ↓
Grok High effort attempt 1
        ↓
STOP / reassess
```

The sixth attempt must not begin automatically.

If the task remains unresolved after the allowed attempts:

* do not modify additional implementation code;
* do not advance to the next task;
* do not mark the task complete;
* preserve the complete failure evidence;
* mark the task `BLOCKED`, unless the issue is an actual specification/state contradiction;
* require human review before continuing.

A debugging loop means one meaningful cycle of:

```text
diagnose → hypothesize → modify → test → evaluate
```

Multiple failing tests produced by the same diagnostic cycle count as one loop, not one loop per individual test failure.

### Human intervention report

When the limit is reached, produce:

```text
BLOCKED

Phase:
Task:

Attempts:
1. Composer:
2. Composer:
3. Grok Medium:
4. Grok Medium:
5. Grok High:

Failure:
Tests/commands:
Files modified:
Approaches attempted:
Evidence gathered:

Likely cause:
Unresolved issue:

Human decision/action required:
```

If the issue is a contradiction between authoritative project information and repository evidence, use the existing `STATE CONFLICT` format instead.

**Never continue debugging solely to avoid reporting a failure.**
 
---

## 9. Anti-patterns to watch for

Things agents have actually tried, that need to be caught:

- **Blanket `# type: ignore` comments on imports.** Configure mypy overrides in `pyproject.toml` instead. Rule 14: every remaining ignore needs a trailing reason comment.
- **Global DB connection singletons.** §5 forbids it. Every request opens and closes its own connection.
- **Scratch files at the repo root.** Rule 11. Use `tmp_path` in tests or a REPL.
- **`pyproject.toml` edits bundled into unrelated commits.** Note them explicitly in the report; if it's a new library, it needs approval.
- **Smoke tests that only check subset of files.** Rule 10. Whole tree, exactly as written.
- **Writing to `data/` in tests.** Every test uses `tmp_path`. Never the real data dir.
- **"Improving" a spec while transcribing.** Composer's failure mode. Verify field names match §4.4 exactly.
- **Adding `/api/health` alias or proxy rewrites to "fix" Phase 0.3.** No — Phase 3.6 mounts the router under `/api`.
- **Scaffolding ahead.** §7. Only build the current task.
- **Screenshot-based browser verification.** Cursor's CDP browser tooling (screenshot, zoom, image-read) consumes context fast and is unreliable on Windows. Instruct agents to verify UI via plain DOM assertions in tests, or by opening the browser manually and describing what they see in text. Never allow screenshot-then-read-image loops in a session.
- All page-level error states use `ErrorDisplay` from
  `components/ui/ErrorDisplay.tsx`. Do not hand-roll error UIs in individual
  pages. The top-level `ErrorBoundary` in main.tsx catches render crashes
  and shows a friendly fallback.

---

## 10. Environment

- **Python:** 3.14 in the venv (spec says 3.12+; if a package misbehaves, drop to 3.12 in a fresh venv)
- **OS:** Windows (PowerShell 5.x — `&&` is not supported, use `;`)
- **Path issue:** `pip`/`pytest`/`ruff`/`mypy` are not on PATH — use `python -m pip`, `python -m pytest`, etc.
- **Repo root:** `E:\Documents\Projects\colossal_quant`
- All env vars are documented in `.env.example`. Read env vars via
  `quant.config`, not `os.environ`, in new code. The config module loads
  `.env` at import; real env vars always take precedence.
- **`git status --short` shows `M .cursor/rules/project.mdc`** whenever rules are edited — commit as a mini-phase (`Phase X.Y.1: add rule N`).
- Start the API with `--reload` during development: `python -m uvicorn quant.api.main:app --port 8000 --reload`
- `scripts/cleanup.py` archives parquet artifacts older than 30 days
  (default). It flips `meta_runs.status` to 'archived' and nulls the
  `artifacts` JSON. Run `--dry-run` first to preview.
- Fees: `params['maker_fee']` / `params['taker_fee']` are decimal
  strings, default '0.001' (0.1%). Set per run via CLI flags
  `--maker-fee` / `--taker-fee` or the StrategyForm's "Fee %" input.
- Benchmark: `params['benchmark_symbol']` (string, default '') enables a
  benchmark overlay on the equity chart. The symbol must have bars in the
  same venue/timeframe as the run. Empty string or missing bars → no
  benchmark. Never fails the run.

---

## 11. State and phase transitions

`STATE.md` is the only authoritative source for the current phase/task. Update it only after acceptance and reviewer approval. Conflicts require STOP and explicit resolution.

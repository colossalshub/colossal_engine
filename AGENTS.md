# AGENTS.md

This repo uses a strict AI-collaboration workflow. Read these before doing
anything:

1. `STATE.md` — current phase and task. Authoritative for state.
2. `PROJECT.md` — permanent spec, data contracts, roadmap. Authoritative
   for what the project is.
3. `WORKFLOW.md` — execution procedure, acceptance discipline, gotchas.
4. `REVIEWER.md` — review checklist.
5. `INCIDENTS.md` — observed failure patterns. Read before reviewing any
   report; flag any report that matches a pattern.

## Startup protocol

Before planning or writing code:

1. Read the five files above.
2. Verify the repository matches `STATE.md`. Run `git log --oneline -3`
   and `git status --short`.
3. If `STATE.md` and the repository disagree, STOP and report the
   conflict. Do not proceed.

## Rules

- Never modify `PROJECT.md`, `WORKFLOW.md`, `REVIEWER.md`, or `.cursor/`.
- Never modify `STATE.md` while implementing a task. The implementing
  agent does not mark its own work complete.
- After the reviewer accepts a task, the reviewer updates `STATE.md`
  before writing the next task prompt. That update is its own docs
  commit. Record the evidence block from `STATE.md` §7, mark the task
  complete, and set `current_task` to the next task. If the next phase
  has no task split yet, write the split in that same commit and set
  only the first task to `READY`.
- One task = one commit. Commit via terminal only. The state-advance
  commit is separate from the task commit.
- Every deliverable includes its test.
- Do not add dependencies without approval.
- Run acceptance commands from the repo root on the whole tree.
- Do not infer current phase from memory or commit messages.
- If docs contradict each other or the code, STOP and report.
- When reviewing a report: re-run every acceptance command yourself. Do
  not trust pasted output.
- "Future authorized work" below is a design contract. It does not change
  `STATE.md` and does not authorize a task.

## Environment

- Windows, PowerShell 5.x. `&&` doesn't work; use `;` or separate commands.
- Activate the venv before running Python: `.venv\Scripts\Activate.ps1`
- Repo root: `E:\Documents\Projects\colossal_quant`

## Future authorized work

Not current execution state. `STATE.md` remains authoritative for what
may be implemented. Do not modify `STATE.md` because this section exists.
Do not start this work, open a phase, or commit it until the recorded
Phase 16.5 sequence is complete and a later human message explicitly
authorizes the task.

### U.6 — Tear Sheet Research Workspace Redesign

**Status: not authorized.**

When U.6 is explicitly authorized, evolve the Tear Sheet from KPI cards
and charts into a layered research review. Presentation only. Do not
change backtest calculations, Nautilus execution, portfolio accounting,
ingestion, artifacts, schemas, API contracts, or strategy execution.
Do not fabricate metrics. If the API does not supply a value, leave it
unavailable.

The researcher should be able to answer:

1. What happened? — Overview
2. How did performance evolve? — Performance
3. How did the strategy trade? — Trades
4. What risk produced those results? — Risk
5. When did it work? — Regimes
6. Under what execution assumptions? — Execution
7. Does supporting validation exist? — Robustness
8. Can the experiment be understood and reproduced? — Data

Navigation order, when authorized:

1. Overview
2. Performance
3. Trades
4. Risk
5. Regimes
6. Execution
7. Robustness
8. Data

Keep the application shell, navigation rail, nested `/runs/:id` route,
and one active tab. `/runs/:id` still redirects to `overview`. Run
identity stays in the page header, outside the tabs. Do not reintroduce
`react-grid-layout`.

**Overview.** Headline: CAGR, Sharpe, maximum drawdown. Secondary:
Sortino, volatility, Calmar, profit factor, turnover. Then the existing
equity curve and monthly heatmap. No cumulative-return card. Null KPIs
stay an em dash. Do not calculate replacements in React.

**Performance.** Existing price chart with fill markers, then the
existing equity chart with benchmark when the series supplies it.
Equity is the primary performance chart. No rolling Sharpe or rolling
volatility unless the API supplies those series.

**Trades.** Existing closed-trade KPIs: total trades, win rate, profit
factor, and average duration when it is non-null. Then the existing
server-paginated ledger. Preserve server pagination, sorting, null
handling, and trade fields. Do not aggregate paginated rows into
distributions. Do not invent R-multiple, MAE, MFE, expectancy, or a
holding-time distribution.

**Risk.** A Risk tab using supplied Sharpe, Sortino, volatility,
maximum drawdown, and Calmar, plus the existing underwater chart.
That chart's home is Risk. Do not calculate drawdown duration,
recovery factor, Ulcer Index, or a current-drawdown statistic unless
the backend supplies it.

**Regimes.** No regime payload exists. Unavailable copy: "Not available
for this run. No regime classification is attached to this result."
Do not add a classifier.

**Execution.** Render the execution-assumption strings already on the
run, including fees, fill model, latency, spread, queue, and partial
fills. A missing assumptions object stays an explicit unavailable
state. Do not build a cost model. Do not sum trade-row fees into a
new total. Do not invent gross P&L, funding, slippage, or net P&L.

**Robustness.** Unavailable copy: "No robustness analysis is attached
to this run." Do not add sensitivity, walk-forward, out-of-sample,
bootstrap, Monte Carlo, or a robustness score.

**Data.** Group only fields the tear sheet already has. Run identity:
strategy, git SHA, experiment id when non-null, timeframe, benchmark,
date range. Do not invent venue, strategy version, or dataset identity.
Verification: the existing badge. Clock: the API strings `equity_ts`,
`fill_ts`, `marker_ts`, and `fill_included_in_equity`, shown verbatim.
Missing assumptions keep the current explicit missing behavior.

Do not add subjective strategy judgments, health scores, or an
observations block. Those require a separate authorization and a
research-layer source.

Reuse `EquityCurve`, `DrawdownChart`, `PriceChart`, `MonthlyHeatmap`,
`TradeLedger`, and `BaseChart`. Do not rewrite them for layout, and do
not retokenize the theme. If the Tear Sheet needs a different KPI
layout than U.5, add a Tear Sheet-specific `KpiCards` variant. Compare
must keep the U.5 one-group behavior, and its tests must still pass.

OpenStatz is hierarchy and density inspiration only. Do not copy its
branding, logo, layout, typography, colors, or implementation. Keep
Colossal Quant's tokens, light and dark themes, semantic colors, and
tabular numerals.

Expected file scope, to be re-checked against the repo at planning
time, not blanket permission:

- `frontend/src/App.tsx`
- `frontend/src/pages/TearSheet/TearSheetNav.tsx`
- `frontend/src/pages/TearSheet/index.tsx`
- `frontend/src/pages/TearSheet/tearSheet.css`
- `frontend/src/pages/TearSheet/KpiCards.tsx`
- `frontend/src/pages/TearSheet/kpiCards.css`
- `frontend/src/pages/TearSheet/tabs/OverviewTab.tsx`
- `frontend/src/pages/TearSheet/tabs/PerformanceTab.tsx`
- `frontend/src/pages/TearSheet/tabs/TradesTab.tsx`
- `frontend/src/pages/TearSheet/tabs/DataTab.tsx`
- `frontend/src/pages/TearSheet/tabs/PlaceholderTab.tsx`
- `frontend/src/pages/TearSheet/tabs/RiskTab.tsx`
- `frontend/src/pages/TearSheet/tabs/ExecutionTab.tsx`

No backend files unless a separate task says so.

Acceptance, when the task exists: all eight sections render for a done
run; the active nav item matches the route; the header stays visible;
KPI text comes from `kpis`; nulls stay em dashes; equity, benchmark,
drawdown, monthly cells, and trades are the supplied values; open
trades stay open; missing assumptions do not break the page; Regimes
and Robustness show no fabricated results; Execution shows only
supplied assumptions; both themes work; Compare still passes. Commands:
`cd frontend` then `npx tsc -b`, `npx vitest run`, and `npm run build`.

**Planning gate.** The first pass after explicit authorization is
planning only. Report current architecture, reusable components, data
actually on the API, proposed information architecture, layout, exact
files, exact tests, API impact, acceptance criteria, and scope risks.
Then stop. No code, no new files, no commit, until the human accepts
that plan.
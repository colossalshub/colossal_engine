# AGENTS.md

This repo uses a strict AI-collaboration workflow. Read these before doing
anything:

1. `STATE.md` — current phase and task. Authoritative for state.
2. `PROJECT.md` — permanent spec, data contracts, roadmap. Authoritative
   for what the project is.
3. `WORKFLOW.md` — execution procedure, acceptance discipline, gotchas.
4. `REVIEWER.md` — review checklist. Read only when reviewing a report.
5. `INCIDENTS.md` — observed failure patterns. Read only when reviewing
   a report; flag any report that matches a pattern.

## Startup protocol

Before planning or writing code:

1. Read `STATE.md` in full.
2. Read only the `PROJECT.md` sections the task prompt lists.
3. Read `WORKFLOW.md` in full.
4. Verify the repository matches `STATE.md`. Run `git log --oneline -3`
   and `git status --short`.
5. Do not infer state from memory. If `STATE.md`, `PROJECT.md`,
   `WORKFLOW.md`, the code, or the tests disagree, STOP and report the
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
- Acceptance commands run from the repo root, on the whole tree, exactly
  as written in the task prompt (subject to the path-scoped rule in
  `WORKFLOW.md` §5).
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
Do not start this work, open a phase, or commit it until a later human
message explicitly authorizes the task.

### U.6 — Tear Sheet Research Workspace Redesign

**Status: not authorized.** Full design contract is in `docs/specs/U6.md`.
The planning gate still applies: the first pass after explicit
authorization is planning only — report architecture, data, layout,
files, tests, impact, acceptance, and scope risks, then stop. No code,
no new files, no commit, until the human accepts that plan.

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

## Environment

- Windows, PowerShell 5.x. `&&` doesn't work; use `;` or separate commands.
- Activate the venv before running Python: `.venv\Scripts\Activate.ps1`
- Repo root: `E:\Documents\Projects\colossal_quant`
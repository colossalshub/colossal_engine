# AGENTS.md

This repo uses a strict AI-collaboration workflow. Read these before doing
anything:

1. `STATE.md` — current phase and task. Authoritative for state.
2. `PROJECT.md` — permanent spec, data contracts, roadmap. Authoritative
   for what the project is.
3. `docs/ai/WORKFLOW.md` — execution procedure and acceptance discipline.
4. `docs/ai/REVIEWER.md` — review checklist. Read only when reviewing a report.
5. `docs/ai/INCIDENTS.md` — observed failure patterns. Read only when reviewing
   a report; flag any report that matches a pattern.

## Startup protocol

Before planning or writing code:

1. Read `STATE.md` in full.
2. Read only the `PROJECT.md` sections the task prompt lists.
3. Read `docs/ai/WORKFLOW.md` in full. Load a guide from
   `docs/ai/guides/` only when the task touches that subsystem.
4. Verify the repository matches `STATE.md`. Run `git log --oneline -3`
   and `git status --short`.
5. Do not infer state from memory. If `STATE.md`, `PROJECT.md`,
   `docs/ai/WORKFLOW.md`, the code, or the tests disagree, STOP and report the
   conflict. Do not proceed.

## Rules

- Never modify `PROJECT.md`, `docs/ai/WORKFLOW.md`,
  `docs/ai/REVIEWER.md`, or `.cursor/`.
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
  `docs/ai/WORKFLOW.md` §5).
- When reviewing a report: re-run every acceptance command yourself. Do
  not trust pasted output.
## Environment

- Windows, PowerShell 5.x. `&&` doesn't work; use `;` or separate commands.
- Activate the venv before running Python: `.venv\Scripts\Activate.ps1`
- Repo root: `E:\Documents\Projects\colossal_quant`

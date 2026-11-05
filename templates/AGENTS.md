# AGENTS.md — State-Driven Workflow (copy into your project root)

LLM sessions have no durable memory: the context window is not storage, and text generated in a past session is not recalled knowledge. Project truth lives in files on disk. Every session reads that state before acting and updates it after acting — for new and existing projects alike.

1. **Read state before acting.** At the start of work, read the project's source of truth: `PROJECT_PLAN.md`, `TODO.md`, `CHANGELOG.md`, `WORKLOG.md` (if present), and `.ai/` specs. Continue from the recorded point, not from chat history; verify stale-looking claims against the repository.
2. **Write state after acting.** Immediately after every meaningful step (accepted decision, completed phase, discovered constraint, session-interruption risk), persist the result. An unrecorded step is a step that never happened for the next session.
3. **Spec before code.** Non-trivial features get a short spec first — `.ai/specs/<topic>.md` covering purpose, contracts (API/DB/UI), and acceptance criteria. The spec is the contract the implementation and review are measured against; update it when behavior changes.
4. **Tests are the executable spec.** An implemented feature has a test that proves it. When reconstructing what exists, a passing test outranks chat claims.
5. **Never assert absence without evidence.** Before saying a feature "does not exist", check the specs, the tests, and the code. Spec + no code = backlog; spec + code = implemented; code + no spec = undocumented — write or refresh the spec before changing it. Concluding "it's absent" from an empty context window is forbidden.
6. **Machine-readable task state (optional).** Default tracker is `TODO.md`. For automated multi-agent orchestration maintain `.ai/tasks.json` (id, title, status: todo|in_progress|done|blocked, spec_ref, context_files, acceptance_criteria, blockers); `done` only after verification. If both trackers exist, `PROJECT_PLAN.md` must declare which is authoritative; never let them disagree.
7. **Context assembly for delegated work.** When handing a task to a worker agent, pass the task, its `spec_ref` content, and the listed `context_files` — not raw unfiltered chat history.
8. **Adopting an existing project.** At first touch, create missing SSOT files from verified repository evidence; do not invent history.

Vision, architecture, constraints, and major decisions live in `PROJECT_PLAN.md`; dated material changes in `CHANGELOG.md`; the operational queue in `TODO.md`; the session journal in `WORKLOG.md`. Do not create parallel duplicates (e.g. `.ai/vision.md`) — `.ai/` holds only specs and optional `tasks.json`.

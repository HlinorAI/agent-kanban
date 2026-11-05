# WORKLOG: agent-kanban

## 2026-11-05 (session ZCode/GLM)
- Read working prototype (~43KB, local dashboard): manual block STAGES/CATS/MODES/P/GROUP/G + generated KB-DATA block (markers) + generic render/drag/drop/notes logic. Decision: sanitize by surgical script, not rewrite → logic preserved byte-for-byte.
- Built kit per spec .ai/specs/opensource-kit.md; tests on synthetic git repos in /tmp — init found all repos, updater filled ACT/START/EXTRA, auto-register added 3 cards, repeat run reported "no changes" (idempotent), manual block untouched.
- Personal-string scan of all shipped files: clean (the only hit was this journal quoting the scan patterns themselves; reworded).
- Git initialized; first commit local. NOT published — public push requires owner approval of account+name.
Resume point: publish step in TODO.md "Now".

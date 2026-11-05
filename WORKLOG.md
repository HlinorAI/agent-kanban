# WORKLOG: agent-kanban

## 2026-11-05 (session ZCode/GLM)
- Read working prototype (~43KB, local dashboard): manual block STAGES/CATS/MODES/P/GROUP/G + generated KB-DATA block (markers) + generic render/drag/drop/notes logic. Decision: sanitize by surgical script, not rewrite → logic preserved byte-for-byte.
- Built kit per spec .ai/specs/opensource-kit.md; tests on synthetic git repos in /tmp — init found all repos, updater filled ACT/START/EXTRA, auto-register added 3 cards, repeat run reported "no changes" (idempotent), manual block untouched.
- Personal-string scan of all shipped files: clean (the only hit was this journal quoting the scan patterns themselves; reworded).
- Git initialized; first commit local. NOT published — public push requires owner approval of account+name.
Resume point: publish step in TODO.md "Now".

## 2026-11-05 (публикация)
- Owner approved: private repo `HlinorAI/agent-kanban`. Created via gh (account hlinor-systems), pushed main (60fe513), verified visibility=PRIVATE.
- Commit author set to owner's global identity; .gitignore added (kanban.html, config, .bak/tmp, pycache).
- Next: public flip only by explicit owner approval; then final polish (done same day: ProjectKanban.app rename to avoid collision with personal installs, repo description+topics, pre-public audit).

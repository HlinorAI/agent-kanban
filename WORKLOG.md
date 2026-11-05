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

## 2026-11-05 (pre-public audit)
- Found and fixed: install/uninstall scripts committed without exec bit → every user's ./install-macos.sh would fail; fixed via update-index --chmod=+x (d02c53d). Push initially failed silently (transient SSL) — caught by comparing local HEAD vs GitHub API.
- Live-tested full public flow from a fresh GitHub clone into /tmp: quickstart (init+update on 2 synthetic repos, auto-register=2, KB_UPDATED=today), install ProjectKanban.app (renamed from Kanban.app to avoid collision with personal installs), launch → updater rc=0, uninstall clean (app+LaunchAgent gone).
- Scans: secrets (token/key patterns) across all git history — clean; personal strings (emails, /Users/, project names) — clean; artifacts in index — none.
- Known leftovers for public flip: UI strings Russian (i18n TODO), Linux install notes TODO, commit author identity = owner's global git config (owner's call).

## 2026-11-05 (решение по авторству)
- Owner decision: commit authorship stays as-is (owner's global git identity, email visible) — "contacts belong inside git"; no noreply rewrite, no CONTACTS file. Last pre-public leftover resolved; public flip awaits owner's explicit word.

## 2026-11-05 (first-run wizard v0.2)
- Owner approved full wizard scenario. Spec .ai/specs/first-run-wizard.md; kanban-setup.py implemented; installer: default board ~/kanban/kanban.html, first launch without board → Terminal wizard (macos-first-run.command).
- Tests (synthetic /tmp tree): depth-1/2 discovery, junk+hidden excluded, --yes/--seed/--seed-full, sentinel AGENTS.md not overwritten, refuse-to-replace existing board, interactive defaults with EOF-safe cancel. All green.
- READMEs EN/RU: wizard = method 1; init = method 2; app = method 3; cron unchanged.

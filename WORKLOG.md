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

## 2026-11-05 (ПУБЛИКАЦИЯ)
- Owner said "делаем публичным" → visibility flipped to PUBLIC via gh, verified via API: PUBLIC https://github.com/HlinorAI/agent-kanban.
- Description + 7 topics were set earlier; README EN/RU final; all pre-public audits green (secrets history scan, live clone→wizard→app cycle).
- Kit is now live for external users. Post-public backlog stays in TODO.md (i18n, Linux docs, perf).

## 2026-11-05 (v0.3: i18n + Linux docs + scanner perf; comma bug)
- Backlog closed per owner: i18n (UI dict EN/RU, var LANG default 'en'), zero-Cyrillic invariant for template+3 py scripts; Linux docs (cron + systemd user timer); scanner fast path git ls-files -c -o --exclude-standard + single-pass stats, os.walk fallback.
- Tests: updater on git repo with ignored junk = 1.0s wall, f == git ls-files count, marks via path segments, idempotent, non-git fallback OK.
- REAL BUG caught by new headless-Chrome render test: auto_register appended entries without a comma after the last manual P entry → `[a]\n[b]` parses as index access → undefined hole in P → BLANK BOARD for every auto-register user since v0.1. Text-level tests never executed the page. Fixed: comma normalization in auto_register (verify: rendered columns data-col=idea..archive, cards visible, EN+RU).
- Lesson recorded: render the page (executed DOM), not just grep the source; --dump-dom with --headless=new DOES execute JS (probe-verified), and window.onerror→document.title is a cheap error trap.

## 2026-11-05 (TCC: silent denials for unsigned bundles)
- On the owner's machine, Kanban.app (personal install, unsigned at the time) never showed the Documents access prompt: instant Errno 1, absent from Files & Folders; tccutil reset of the bundle id did not help; ad-hoc codesign (after xattr -cr cleanup — codesign refuses bundles with FinderInfo detritus from cp -R) still denied instantly in the app-launched context. Root fix applied to the KIT installer: xattr cleanup + ad-hoc codesign + warning; README EN/RU gained a TCC troubleshooting section (manual Full Disk Access path with Cmd+Shift+G).
- Owner-side completion for the personal app: manual Full Disk Access grant (System Settings) — pending owner click.

## 2026-11-05 (native launcher)
- Owner chose the compiled-launcher path (not python3 FDA) — "не каждый готов давать полный доступ". launcher.c: posix_spawn (chrome --app / open fallback; updater synced, output→log), --update-only, paths baked via -D at install time.
- Verified on owner machine: personal Kanban.app rebuilt with universal binary → TCC PROMPT FIRED for the first time (python blocks pending decision instead of instant Errno 1). Owner granted. Kit installer compiles the binary (clang/cc), falls back to bash script when no compiler; live-tested from /tmp copy: Launcher: native, universal+adhoc, hidden run ok, uninstall clean (remote commit follows).
- Residual: a git subprocess under the app stalled on a repo file with com.apple.macl (per-file TCC locks created by agent sessions, 201+ found across ~/Documents/Projects) — being stripped via sandboxed copy-in-place (separate worklog line in personal kanban).

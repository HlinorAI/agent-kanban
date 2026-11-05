# TODO: agent-kanban

## Now
- [x] 2026-11-05 TCC hardening: ad-hoc codesign in installer + README troubleshooting (silent denials without signature).
- [x] 2026-11-05 First-run wizard (kanban-setup.py): discovery, board in ~/kanban, agent-memory seeding with confirmation; macOS app runs wizard on first launch when no board exists.
- [x] SSOT files + spec (this dir).
- [x] Sanitize dashboard template from working prototype (zero personal strings).
- [x] Config-driven `kanban-update.py` (kanban-projects.json, ~HOME, auto_register).
- [x] `kanban-init.py` scanner + template instantiation.
- [x] `install-macos.sh` / `uninstall-macos.sh` (Kanban.app + optional LaunchAgent).
- [x] `templates/` — agent SSOT skeletons.
- [x] Tests on synthetic repos in /tmp (init → update → data block verified).
- [x] README + LICENSE + local git commit.
- [x] Published as **private** `HlinorAI/agent-kanban` (owner-approved 2026-11-05).

## Next
- [x] 2026-11-05 Flipped to public by explicit owner approval (description + topics set earlier).
- [ ] Set GitHub repo description + topics when making public.
- [x] 2026-11-05 i18n: UI dictionary EN/RU in template (var LANG, default 'en'), zero Cyrillic in code/CLI; board rendered via headless Chrome EN+RU.
- [ ] Auto-refresh: updater pings a tiny HTTP endpoint OR dashboard polls file mtime.
- [x] 2026-11-05 Linux: cron + systemd user timer documented in README EN/RU (Windows — backlog).
- [x] 2026-11-05 Performance: git ls-files fast path (respects .gitignore), single-pass stats; os.walk fallback for non-git dirs.
- [ ] Optional GitHub Actions badge/stats columns.

## Blocked
- [ ] (nothing)

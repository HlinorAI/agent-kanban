# TODO: agent-kanban

## Now
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
- [ ] Flip to public — ONLY after explicit owner approval.
- [ ] Set GitHub repo description + topics when making public.
- [ ] i18n: English UI strings behind a small dictionary.
- [ ] Auto-refresh: updater pings a tiny HTTP endpoint OR dashboard polls file mtime.
- [ ] Linux/Windows install notes (+ optional cron/systemd timer example).
- [ ] Performance: `git ls-files` fast path for large repos.
- [ ] Optional GitHub Actions badge/stats columns.

## Blocked
- [ ] (nothing)

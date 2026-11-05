# CHANGELOG: agent-kanban

## 2026-11-05 — v0.1.0

### Added
- Initial kit: dashboard template (sanitized from a working prototype), config-driven updater with auto-registration of new repos, project scanner (`kanban-init.py`), macOS app installer/uninstaller, agent SSOT templates, README/LICENSE.
- State-driven workflow spec `.ai/specs/opensource-kit.md`.
- Synthetic-repo tests covering init → update → data-block regeneration.

### 2026-11-05
- Published as private repo HlinorAI/agent-kanban (main, 60fe513); .gitignore added.
- Bilingual docs: README.md (EN) + README.ru.md (RU) with three install methods (CLI / macOS app / cron); lean-down of README, removed duplicated roadmap section.
### Added (same day)
- First-run wizard `kanban-setup.py`: scans common folders, builds the board in `~/kanban`, seeds AGENTS.md / SSOT skeletons into repos with explicit confirmation (never overwrites). macOS app launches the wizard automatically when no board exists. READMEs updated (wizard = install method 1).

# PROJECT_PLAN: agent-kanban

## Objective
Open-source starter kit combining two working practices:
1. **State-driven agent workflow** — file-based SSOT (PROJECT_PLAN/TODO/CHANGELOG/WORKLOG + .ai/specs) so AI agents never depend on chat memory; templates users drop into their own repos.
2. **Repo kanban dashboard** — single-file HTML board over the user's local git repositories, refreshed by a config-driven Python updater; optional macOS app launcher + scheduled refresh.

## Problem being solved
LLM agents "forget" — chat history is not memory, and nobody sees the state of 20+ local projects at a glance. Fix: project truth lives in files agents must read/write, and a dashboard shows repo facts (commits, activity, stack, dirt) as a kanban.

## Intended users
Solo developers working with multiple AI agents (Claude Code, Codex, ZCode, etc.) across many local repositories.

## Architecture
- `kanban/kanban.html` — user's dashboard, generated from `kanban.html.template`. Manual data block (STAGES/CATS/MODES/P/GROUP/G) + generated block between `KB-DATA-BEGIN/END` markers.
- `kanban/kanban-update.py` — reads `kanban-projects.json`, collects git facts per repo, regenerates only the marker block; `.bak` backup; guards protect manual data.
- `kanban/kanban-init.py` — scans a root dir for git repos → writes `kanban-projects.json` + instantiates `kanban.html`.
- `kanban/install-macos.sh` / `uninstall-macos.sh` — build `Kanban.app` (Chrome `--app` window + background refresh) and optional LaunchAgent (login + daily 09:00). Linux: plain `python3 kanban-update.py` via cron works; docs only.
- `templates/` — SSOT skeletons (AGENTS.md, PROJECT_PLAN.md, TODO.md, CHANGELOG.md, WORKLOG.md) to copy into any project.
- No runtime dependencies beyond Python 3.8+ stdlib and git. Local-only: no network calls, no telemetry.

## Constraints / decisions
- UI strings are Russian in v0.1 (origin); i18n is backlog.
- `auto_register: true` in config: updater may append minimal card entries for repos missing in the manual `P` list; user enriches descriptions later.
- Privacy: example data only in the repo; installer/updater never phone home.
- License: MIT.

## Status
2026-11-05: scaffolding, sanitizer from working prototype, tests on synthetic repos. Not yet published to GitHub (needs owner approval of account/name).

## Risks / open questions
- macOS TCC: launchd-based refresh requires a one-time Documents permission grant (documented).
- Updater walk time grows with repo size (skip-dirs cover node_modules etc.).
- Single-file HTML approach caps at ~100 cards before it gets heavy.

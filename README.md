# agent-kanban

A local, single-file **kanban board over your git repositories** plus a
**state-driven workflow kit for AI agents** — so agents stop "forgetting" and
you finally see all your projects at a glance.

Two things in one kit:

1. **Project kanban** — `kanban.html` is one HTML file showing every local repo
   as a draggable card (stage, category, mode, last activity, commits, stack,
   remote, dirty files). `kanban-update.py` refreshes the facts from git; you
   keep full control of descriptions, stages and notes (stored in your browser).
2. **State-driven agent rules** — `templates/AGENTS.md` and SSOT skeletons
   (`PROJECT_PLAN / TODO / CHANGELOG / WORKLOG`, specs in `.ai/specs/`) to drop
   into any project, so every agent session reads state before acting and
   writes it back after.

**Local-only by design**: no network calls, no telemetry, no accounts.
Dependencies: Python 3.8+, git, any modern browser.

## Quickstart

```bash
git clone <this-repo> agent-kanban && cd agent-kanban

# point it at a folder of git repos (one level deep):
python3 kanban/kanban-init.py ~/code

# open the dashboard
open ~/code/kanban.html          # macOS
# xdg-open ~/code/kanban.html    # Linux
```

`kanban-init.py` writes `kanban-projects.json` (the repo list) and
`kanban.html` (your board). Edit descriptions/categories by hand in the
`var P = [...]` block of `kanban.html`; everything between the
`KB-DATA-BEGIN/END` markers belongs to the updater — don't edit that.

Refresh facts any time:

```bash
python3 kanban/kanban-update.py ~/code/kanban.html
```

Add or remove repos by editing `kanban-projects.json` (see
`kanban/kanban-projects.example.json`). New repos are auto-registered as
minimal cards on the next update (`auto_register: true`).

## macOS: launch it like an app

```bash
cd kanban
./install-macos.sh               # installs ProjectKanban.app
./install-macos.sh --with-schedule   # + hidden refresh at login and daily 09:00
./uninstall-macos.sh
```

The app (ProjectKanban.app) opens the board in a standalone Chrome window (`--app`, no address
bar) and refreshes repo facts in the background on every launch. First launch:
macOS will ask for access to your files (one time) — this is required for
reading your repos, including from the scheduled background refresh.
Logs: `~/Library/Logs/kanban-app.log`. Linux/Windows: run the updater from
cron/Task Scheduler — same effect, no app wrapper (docs: TODO).

## Agent workflow kit

Copy `templates/AGENTS.md`, `templates/PROJECT_PLAN.md`, `templates/TODO.md`,
`templates/CHANGELOG.md`, `templates/WORKLOG.md` into your project root (this
repo itself uses them — look around). Point your coding agent (Claude Code,
Codex, ZCode, Cursor, …) at `AGENTS.md`; most tools pick it up automatically.
For non-trivial features, keep short specs in `.ai/specs/<topic>.md` before
writing code.

## How the dashboard stays safe to edit

- Everything outside `/* KB-DATA-BEGIN … KB-DATA-END */` is yours: cards,
  descriptions, families, stages, notes (notes and manual stage moves live in
  browser localStorage).
- The updater regenerates only the marker block, writes a `.bak` first, and
  refuses to save if its guards detect the markers swallowed manual data.

## Privacy & security

- The board reads only local files via `git` and the filesystem; it never
  opens network connections.
- Remotes are shown URL-sanitized (credentials stripped).
- Nothing leaves your machine.

## Status & roadmap

v0.1.0 — see [TODO.md](TODO.md) and [PROJECT_PLAN.md](PROJECT_PLAN.md).
Known limits: UI strings are currently in Russian (i18n planned); very large
folders scan slowly (fast `git ls-files` path planned).

## License

MIT — see [LICENSE](LICENSE).

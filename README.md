# agent-kanban

**A local kanban board over your git repositories + state-driven workflow templates for AI agents.**

English | [Русский](README.ru.md)

One HTML file shows every local repo as a draggable card: stage, category, last activity, commits, stack, dirty files, remote. A Python script refreshes the facts from git; you own the descriptions, stages and notes. No network, no telemetry, no accounts.

**Requires:** Python 3.8+, git, any modern browser. macOS optional (for the app launcher).

## What's inside

- `kanban/` — the dashboard (single HTML file), updater, installer
- `templates/` — agent SSOT skeletons: `AGENTS.md`, `PROJECT_PLAN.md`, `TODO.md`, `CHANGELOG.md`, `WORKLOG.md`

## Install — method 1: first-run wizard (any OS)

```bash
git clone https://github.com/HlinorAI/agent-kanban.git
cd agent-kanban
python3 kanban/kanban-setup.py
```

The wizard scans common code folders (`~/Documents`, `~/code`, `~/Developer`, …), shows the git repositories it found, builds your personal board in `~/kanban` and offers to turn on **agent memory**: it drops `AGENTS.md` (optionally the full SSOT skeletons) into your repos — showing exactly which files will be created; existing files are never overwritten. Nothing is written without your confirmation.

Non-interactive flags for scripting: `--roots DIR[,DIR]`, `--target DIR`, `--yes`, `--seed`, `--seed-full`.

## Install — method 2: one explicit command (any OS)

```bash
python3 kanban/kanban-init.py ~/code        # a folder with your git repos (one level deep)
open ~/code/kanban.html                     # xdg-open on Linux
```

`kanban-init.py` writes `kanban-projects.json` and `kanban.html` for the folder you point it at, then fills in repo facts.

Refresh facts any time:

```bash
python3 kanban/kanban-update.py ~/kanban/kanban.html
```

## Install — method 3: macOS app

```bash
cd agent-kanban/kanban
./install-macos.sh --html ~/code/kanban.html                    # installs ProjectKanban.app
./install-macos.sh --html ~/code/kanban.html --with-schedule    # + refresh at login and daily 09:00
./uninstall-macos.sh                                            # full removal
```

The app opens the board in a standalone Chrome window (no address bar) and refreshes repo facts in the background on every launch — the board opens instantly, fresh data is visible on next open or ⌘R. If no board exists yet, first launch runs the setup wizard (method 1) in a Terminal window. First launch also: macOS asks for file access once — required to read your repos, including scheduled background runs. Logs: `~/Library/Logs/kanban-app.log`.

## Scheduled refresh without the app (Linux/macOS)

cron:

```cron
0 9 * * * cd /path/to/agent-kanban && python3 kanban/kanban-update.py /path/to/kanban.html >> /tmp/kanban-update.log 2>&1
```

or a systemd user timer:

```ini
# ~/.config/systemd/user/kanban-update.service
[Unit]
Description=agent-kanban facts refresh

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /path/to/agent-kanban/kanban/kanban-update.py /path/to/kanban.html
```

```ini
# ~/.config/systemd/user/kanban-update.timer
[Unit]
Description=Refresh agent-kanban daily

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl --user daemon-reload && systemctl --user enable --now kanban-update.timer
```

## Editing your board

- UI language: `var LANG = 'en';` near the top of the script in `kanban.html` — change to `'ru'` for Russian (stage names, filters, detail panel are fully translated).
- Cards, categories, descriptions: edit the `var P = [...]` block in `kanban.html`.
- Everything between `/* KB-DATA-BEGIN … KB-DATA-END */` belongs to the updater — it makes a `.bak` first and refuses to save if its guards detect manual data in the zone.
- Repos listed in `kanban-projects.json` but missing from `P` get minimal auto-generated cards (`auto_register: true`) — enrich them later.
- Stage moves and notes are stored in your browser (localStorage), nothing is written back to the file.
- Related repos can be grouped into families (`GROUP`/`G` blocks) and shown as one product.

## Agent workflow kit

Copy `templates/*.md` into your project root and point your coding agent (Claude Code, Codex, ZCode, Cursor, …) at `AGENTS.md` — most tools pick it up automatically. The loop it enforces: read project state before acting (files, not chat memory), write state back after every meaningful step, short spec in `.ai/specs/` before non-trivial code, tests as the executable spec, and never claim a feature is missing without checking specs, tests and code.

## Privacy

Local-only by design: reads your repos via `git` and the filesystem, never opens network connections, and sanitizes remote URLs before showing them.

## Known limitations

- Very large repo folders scan slowly (the updater uses `git ls-files` and respects `.gitignore`, but huge repos still take a moment).
- The single-file board stays comfortable up to ~100 cards.

## License

[MIT](LICENSE)

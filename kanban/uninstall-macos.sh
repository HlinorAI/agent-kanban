#!/bin/bash
# Remove Kanban.app and the optional scheduled refresh (agent-kanban).
set -euo pipefail
UID_N=$(id -u)
launchctl bootout "gui/$UID_N/io.github.agent-kanban.update" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/io.github.agent-kanban.update.plist"
rm -rf "/Applications/Kanban.app" "$HOME/Applications/Kanban.app"
echo "Removed: Kanban.app, LaunchAgent (if present). Dashboard and logs left untouched."

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bootstrap the kanban kit over a directory of git repositories.

Scans ROOT (default: current directory) one level deep for git repositories,
writes kanban-projects.json next to them, instantiates kanban.html from
kanban.html.template, and runs kanban-update.py to fill repo facts.

Usage:
  python3 kanban-init.py [ROOT] [--template PATH] [--config PATH] [--html PATH]

Everything is local: no network, no telemetry.
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "project"


def find_repos(root):
    repos = {}
    used = set()
    for entry in sorted(os.listdir(root)):
        full = os.path.join(root, entry)
        if entry.startswith(".") or not os.path.isdir(full):
            continue
        if not os.path.exists(os.path.join(full, ".git")):
            continue
        sid = slugify(entry)
        n = 2
        while sid in used:
            sid = f"{slugify(entry)}-{n}"
            n += 1
        used.add(sid)
        repos[sid] = full
    return repos


def display_path(path):
    home = os.path.expanduser("~")
    if path == home or path.startswith(home + os.sep):
        return "~" + path[len(home):]
    return path


def main():
    ap = argparse.ArgumentParser(description="Bootstrap project kanban over a folder of git repos")
    ap.add_argument("root", nargs="?", default=os.getcwd(), help="directory to scan for git repos")
    ap.add_argument("--template", default=os.path.join(HERE, "kanban.html.template"))
    ap.add_argument("--config", default=None, help="output config path (default ROOT/kanban-projects.json)")
    ap.add_argument("--html", default=None, help="output dashboard path (default ROOT/kanban.html)")
    ap.add_argument("--no-run", action="store_true", help="do not run updater afterwards")
    args = ap.parse_args()

    root = os.path.abspath(os.path.expanduser(args.root))
    if not os.path.isdir(root):
        print(f"ERROR: directory not found: {root}")
        sys.exit(1)
    if not os.path.isfile(args.template):
        print(f"ERROR: template not found: {args.template}")
        sys.exit(1)

    repos = find_repos(root)
    if not repos:
        print(f"No git repositories found (depth 1) in {root}.")
        sys.exit(1)

    config_path = args.config or os.path.join(root, "kanban-projects.json")
    html_path = args.html or os.path.join(root, "kanban.html")
    cfg = {
        "kanban_html": html_path,
        "auto_register": True,
        "projects": {k: display_path(v) for k, v in repos.items()},
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    with open(args.template, encoding="utf-8") as f:
        html = f.read()
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Repositories found: {len(repos)}")
    print(f"Config: {config_path}")
    print(f"Board: {html_path}")
    print("Next: open kanban.html in a browser; edit card categories/descriptions in the var P block of the file.")

    if not args.no_run:
        updater = os.path.join(HERE, "kanban-update.py")
        r = subprocess.run([sys.executable, updater, html_path])
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""agent-kanban first-run wizard.

Discovers git repositories in common locations, builds a personal kanban board
in ~/kanban (by default) and optionally seeds agent-memory templates
(AGENTS.md + SSOT skeletons) into the selected repositories.

Never writes anything without confirmation: repos and files to create are
shown and confirmed interactively. For scripting/tests use the non-interactive
flags: --roots, --target, --yes, --seed, --seed-full.

Existing files are never overwritten — candidates missing them only.
Local-only: no network access.
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "kanban.html.template")
UPDATER = os.path.join(HERE, "kanban-update.py")
TEMPLATES = os.path.normpath(os.path.join(HERE, "..", "templates"))

DEFAULT_ROOTS = ["~/Documents", "~/Documents/Projects", "~/Projects",
                 "~/code", "~/src", "~/dev", "~/Developer", "~/work"]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist",
             "build", ".next", "vendor", "Pods", "results", ".obsidian",
             "Library", "Applications"}
MAX_DEPTH = 2
SEED_FULL = ["AGENTS.md", "PROJECT_PLAN.md", "TODO.md", "CHANGELOG.md", "WORKLOG.md"]
SEED_MIN = ["AGENTS.md"]


def is_repo(path):
    return os.path.exists(os.path.join(path, ".git"))


def display_path(path):
    home = os.path.expanduser("~")
    if path == home or path.startswith(home + os.sep):
        return "~" + path[len(home):]
    return path


def discover(roots, exclude_prefixes):
    found, seen = [], set()
    for root in roots:
        base = os.path.realpath(os.path.expanduser(root))
        if not os.path.isdir(base):
            continue
        stack = [(base, 0)]
        while stack:
            cur, depth = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            try:
                entries = sorted(os.listdir(cur))
            except OSError:
                continue
            for name in entries:
                if name.startswith(".") or name in SKIP_DIRS:
                    continue
                p = os.path.join(cur, name)
                if not os.path.isdir(p):
                    continue
                real = os.path.realpath(p)
                if any(real == e or real.startswith(e + os.sep) for e in exclude_prefixes):
                    continue
                if is_repo(p):
                    if real not in {os.path.realpath(f) for f, _ in found}:
                        found.append((p, root))
                elif depth + 1 < MAX_DEPTH:
                    stack.append((p, depth + 1))
    return found


def parse_selection(answer, total):
    """'1,3-5' → sorted list of 0-based indices; empty → all."""
    if not answer.strip():
        return list(range(total))
    idx = set()
    for part in answer.replace(" ", "").split(","):
        if "-" in part:
            a, _, b = part.partition("-")
            if a.isdigit() and b.isdigit():
                idx.update(range(int(a) - 1, int(b)))
        elif part.isdigit():
            idx.add(int(part) - 1)
    return sorted(i for i in idx if 0 <= i < total)


def ask(prompt, default_yes=False):
    try:
        answer = input(prompt).strip().lower()
    except EOFError:
        return False
    if not answer:
        return default_yes
    return answer in ("y", "yes", "д", "да")


def create_board(target, repos):
    os.makedirs(target, exist_ok=True)
    html_path = os.path.join(target, "kanban.html")
    config_path = os.path.join(target, "kanban-projects.json")
    for path, what in ((html_path, "доска"), (config_path, "конфиг")):
        if os.path.exists(path) and not ask(f"{what} уже существует: {display_path(path)} — заменить? [y/N]: "):
            print("Отмена: существующие файлы не тронуты.")
            sys.exit(1)
    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    cfg = {
        "kanban_html": html_path,
        "auto_register": True,
        "projects": {slug(os.path.basename(p)): display_path(p) for p, _ in repos},
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    return html_path


def slug(name):
    import re
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "project"


def unique_slugs(repos):
    out, used = {}, set()
    for p, _ in repos:
        s = slug(os.path.basename(p))
        n = 2
        while s in used:
            s = f"{slug(os.path.basename(p))}-{n}"
            n += 1
        used.add(s)
        out[p] = s
    return out


def seed(repos, files, assume_yes):
    plan = []
    for p, _ in repos:
        missing = [f for f in files if not os.path.exists(os.path.join(p, f))]
        if missing:
            plan.append((p, missing))
    if not plan:
        print("Посев не нужен: шаблоны уже есть во всех выбранных репозиториях.")
        return 0, 0
    print("\nБудут СОЗДАНЫ следующие файлы (существующие не перезаписываются):")
    for p, missing in plan:
        print(f"  {display_path(p)}")
        for f in missing:
            print(f"    + {f}")
    if not assume_yes and not ask("\nЗаписать? [Y/n]: ", default_yes=True):
        print("Посев отменён — ничего не записано.")
        return 0, 0
    seeded = skipped = 0
    for p, missing in plan:
        for f in missing:
            dst = os.path.join(p, f)
            if os.path.exists(dst):
                skipped += 1
                continue
            with open(os.path.join(TEMPLATES, f), encoding="utf-8") as src:
                content = src.read()
            with open(dst, "w", encoding="utf-8") as out:
                out.write(content)
            seeded += 1
    return seeded, skipped


def main():
    ap = argparse.ArgumentParser(description="agent-kanban first-run wizard")
    ap.add_argument("--roots", default=None, help="comma-separated dirs to scan (default: common code dirs)")
    ap.add_argument("--target", default=None, help="board directory (default: ~/kanban)")
    ap.add_argument("--yes", action="store_true", help="accept all found repos, no prompts")
    ap.add_argument("--seed", action="store_true", help="seed AGENTS.md into selected repos without prompting")
    ap.add_argument("--seed-full", action="store_true", help="seed AGENTS.md + all SSOT skeletons without prompting")
    ap.add_argument("--no-run", action="store_true", help="do not run the updater afterwards")
    args = ap.parse_args()

    if not os.path.isfile(TEMPLATE):
        print(f"ОШИБКА: шаблон не найден: {TEMPLATE}")
        sys.exit(1)

    target = os.path.realpath(os.path.expanduser(args.target or os.path.join("~", "kanban")))
    roots = [r.strip() for r in args.roots.split(",")] if args.roots else DEFAULT_ROOTS
    exclude = {os.path.realpath(HERE), target, os.path.realpath(TEMPLATES)}

    print("agent-kanban — мастер первого запуска")
    print(f"Ищу git-репозитории (глубина ≤ {MAX_DEPTH}) в: {', '.join(display_path(os.path.expanduser(r)) for r in roots)}")
    found = discover(roots, exclude)
    if not found:
        print("Репозиториев не найдено. Укажите корни вручную: --roots '/path/to/repos'")
        sys.exit(1)

    print(f"\nНайдено репозиториев: {len(found)}")
    current_root = None
    for i, (p, root) in enumerate(found, 1):
        if root != current_root:
            current_root = root
            print(f"  [{display_path(os.path.expanduser(root))}]")
        print(f"   {i:3d}. {display_path(p)}")

    if args.yes:
        chosen = found
        print("Выбраны все (--yes).")
    else:
        try:
            answer = input(f"\nКакие включить? Enter — все, номера/диапазоны через запятую, q — выход: ")
        except EOFError:
            print("\nОтмена.")
            sys.exit(1)
        if answer.strip().lower() in ("q", "quit", "exit", "й"):
            print("Отмена — ничего не сделано.")
            sys.exit(0)
        idx = parse_selection(answer, len(found))
        if not idx:
            print("Ничего не выбрано.")
            sys.exit(1)
        chosen = [found[i] for i in idx]

    slugs = unique_slugs(chosen)
    print(f"\nДоска будет создана в: {display_path(target)} ({len(chosen)} репо)")
    html_path = create_board(target, [(p, r) for p, r in chosen])

    seed_files = SEED_FULL if args.seed_full else SEED_MIN
    if args.seed or args.seed_full:
        seeded, skipped = seed(chosen, seed_files, assume_yes=True)
    elif not args.yes and ask(f"\nВключить «память агентов»? (положить {seed_files[0]}" +
                              (" + SSOT-скелеты" if args.seed_full else "") +
                              " в выбранные репо) [Y/n]: ", default_yes=True):
        seeded, skipped = seed(chosen, seed_files, assume_yes=False)
    else:
        seeded, skipped = 0, 0
        print("Шаблоны агентов не посеяны — можно позже: python3 kanban/kanban-setup.py --seed --roots ...")

    if not args.no_run:
        print("\nОбновляю факты по репозиториям…")
        subprocess.run([sys.executable, UPDATER, html_path], check=False)

    print("\nГотово.")
    print(f"  Доска:    {display_path(html_path)}  — откройте в браузере")
    print(f"  Репо:     {len(chosen)}, шаблонов посеяно: {seeded}" + (f", пропущено существующих: {skipped}" if skipped else ""))
    print("  Приложение (macOS): cd " + display_path(HERE) + " && ./install-macos.sh --html " + display_path(html_path))


if __name__ == "__main__":
    main()

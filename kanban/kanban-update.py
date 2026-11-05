#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refreshes volatile repository facts in the project kanban (kanban.html).

Reads kanban-projects.json (projects: {id: path}) and regenerates only the
block between the KB-DATA-BEGIN / KB-DATA-END markers:
KB_UPDATED, ACT (last activity), START (first git commit),
EXTRA (repo facts: commits/authors/branches/worktrees/dirty files,
files, stack, infrastructure, remote, commits in last 7 days).

Manual data (P, descriptions, GROUP, G, STAGES, CATS, MODES) is never touched
inside the marker block; with auto_register enabled, configured repos missing
from P get a minimal card appended so they appear on the board.

Usage: python3 kanban-update.py [path-to-kanban.html]
Config lookup: kanban-projects.json next to the html file (or next to this
script). Run kanban-init.py first to generate both.
No network access; requires python3.8+ and git.
"""

import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta

LANGS = {".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript", ".ts": "TypeScript",
         ".tsx": "TypeScript", ".jsx": "TypeScript", ".go": "Go", ".rs": "Rust",
         ".swift": "Swift", ".php": "PHP", ".html": "HTML", ".css": "CSS", ".scss": "CSS",
         ".sql": "SQL", ".sh": "Shell", ".zsh": "Shell", ".tf": "Terraform", ".hcl": "Terraform",
         ".java": "Java", ".kt": "Kotlin"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
             ".next", "vendor", "Pods", "results", ".obsidian"}
SKIP_FILES = {".DS_Store"}
GUARDS = ("var GROUP", "var G = {", "var P = [", "var STAGES", "var CATS")
AUTO_COMMENT = "/* auto-registered from kanban-projects.json; edit category/description */"


def load_config(kanban_html):
    """Find kanban-projects.json: next to the html file, then next to this script."""
    for base in (os.path.dirname(os.path.abspath(kanban_html)),
                 os.path.dirname(os.path.abspath(__file__))):
        cfg = os.path.join(base, "kanban-projects.json")
        if os.path.isfile(cfg):
            with open(cfg, encoding="utf-8") as f:
                data = json.load(f)
            return data, cfg
    return {}, None


def resolve_kanban_path(argv):
    if len(argv) > 1:
        return argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    local = os.path.join(here, "kanban.html")
    if os.path.isfile(local):
        return local
    for base in (os.getcwd(), os.path.expanduser("~")):
        cand = os.path.join(base, "kanban.html")
        if os.path.isfile(cand):
            return cand
    print("ERROR: kanban.html not found; pass the path as an argument")
    sys.exit(1)


def git(path, args):
    try:
        r = subprocess.run(["git", "-C", path] + args, capture_output=True, text=True, timeout=60)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def sanitize_remote(url):
    if not url:
        return None
    url = re.sub(r"^https?://[^/@]+@", "https://", url)
    m = re.match(r"^git@([^:]+):(.+?)(?:\.git)?$", url)
    if m:
        url = f"https://{m.group(1)}/{m.group(2)}"
    url = re.sub(r"\.git$", "", url)
    return url if url.startswith("https://") else None


def git_file_list(path):
    """Tracked + untracked-not-ignored files (respects .gitignore); None on failure."""
    try:
        r = subprocess.run(["git", "-C", path, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                           capture_output=True, timeout=300)
        if r.returncode != 0:
            return None
        return [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]
    except Exception:
        return None


def walk_file_list(path):
    """Fallback listing for non-git directories (uses SKIP_DIRS)."""
    files = []
    for root, dirs, fnames in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.endswith(".xcodeproj")]
        for f in fnames:
            if f in SKIP_FILES:
                continue
            files.append(os.path.relpath(os.path.join(root, f), path))
    return files


def scan_files(path, git_ok):
    """Single pass over the file list: newest mtime, count, extensions, markers."""
    rel_files = git_file_list(path) if git_ok else None
    if rel_files is None:
        rel_files = walk_file_list(path)
    newest = 0.0
    files_total = 0
    ext_count = {}
    marks = set()
    for rel in rel_files:
        base = os.path.basename(rel)
        if base in SKIP_FILES:
            continue
        segs = rel.split("/")
        if "tests" in segs or "test" in segs:
            marks.add("tests")
        if ".agent-gates" in segs:
            marks.add(".agent-gates")
        if len(segs) >= 2 and segs[0] == ".github" and segs[1] == "workflows":
            marks.add("CI")
        files_total += 1
        try:
            mt = os.path.getmtime(os.path.join(path, rel))
            if mt > newest:
                newest = mt
        except OSError:
            pass
        if len(segs) == 1:
            if base == "README.md":
                marks.add("README")
            elif base == "PROJECT_PLAN.md":
                marks.add("PROJECT_PLAN")
            elif base == "TODO.md":
                marks.add("TODO")
            elif base == "CHANGELOG.md":
                marks.add("CHANGELOG")
            elif base == "WORKLOG.md":
                marks.add("WORKLOG")
            elif base == "Dockerfile":
                marks.add("Docker")
            elif base.startswith("docker-compose") and base.endswith((".yml", ".yaml")):
                marks.add("docker-compose")
            elif base == "package.json":
                marks.add("Node")
            elif base in ("pyproject.toml", "requirements.txt", "setup.py"):
                marks.add("Python pkg")
            elif base == "go.mod":
                marks.add("Go module")
            elif base == "Cargo.toml":
                marks.add("Rust")
            elif base.startswith("wrangler") and base.endswith((".toml", ".jsonc", ".json")):
                marks.add("Cloudflare Workers")
            elif base == "Makefile":
                marks.add("Makefile")
        ext = os.path.splitext(base)[1].lower()
        if ext in LANGS:
            ext_count[LANGS[ext]] = ext_count.get(LANGS[ext], 0) + 1
    mt_date = datetime.fromtimestamp(newest).strftime("%Y-%m-%d") if newest else ""
    return mt_date, files_total, ext_count, marks


def max_date(a, b):
    if not a:
        return b or ""
    if not b:
        return a
    return a if a >= b else b


def collect(projects):
    today = date.today()
    since7 = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    act, start, extra = {}, {}, {}
    for pid, raw in projects.items():
        path = os.path.expanduser(str(raw))
        if not os.path.isdir(path):
            continue
        x = {}
        git_ok = git(path, ["rev-parse", "--git-dir"]) is not None
        last_git = ""
        if git_ok:
            first = git(path, ["log", "--reverse", "--date=format:%Y-%m-%d", "--format=%ad"])
            if first:
                first = first.splitlines()[0]
                start[pid] = first
            last_git = git(path, ["log", "-1", "--date=format:%Y-%m-%d", "--format=%ad"]) or ""
            c = git(path, ["rev-list", "--count", "HEAD"])
            if c:
                x["c"] = int(c)
            r7 = git(path, ["rev-list", "--count", f"--since={since7}", "HEAD"])
            if r7:
                x["r7"] = int(r7)
            au = git(path, ["log", "--format=%ae"])
            if au is not None:
                x["a"] = len(set(au.split()))
            st = git(path, ["status", "--porcelain"])
            if st is not None:
                d = len(st.splitlines())
                if d:
                    x["d"] = d
            br = git(path, ["for-each-ref", "refs/heads", "--format=%(refname:short)"])
            if br is not None:
                b = len(br.splitlines())
                if b > 1:
                    x["b"] = b
            wt = git(path, ["worktree", "list"])
            if wt is not None:
                w = len(wt.splitlines())
                if w > 1:
                    x["w"] = w
            rr = sanitize_remote(git(path, ["config", "--get", "remote.origin.url"]))
            if rr:
                x["r"] = rr
        mt_date, files_total, ext_count, marks = scan_files(path, git_ok)
        act[pid] = max_date(last_git, mt_date)
        if files_total:
            x["f"] = files_total
        top = sorted(ext_count.items(), key=lambda kv: -kv[1])
        langs = [f"{k} ×{v}" for k, v in top[:4] if v >= 3]
        if langs:
            x["l"] = langs
        if marks:
            x["m"] = sorted(marks)
        if x:
            extra[pid] = x
    return act, start, extra


def js_str(s):
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"


def js_map_str(m):
    if not m:
        return "{}"
    return "{" + ",".join(f"{k}:{js_str(v)}" for k, v in sorted(m.items()) if v) + "}"


def js_map_extra(m):
    parts = []
    for k in sorted(m):
        x = m[k]
        bits = []
        for key in ("c", "a", "b", "w", "d", "f", "r7"):
            if key in x:
                bits.append(f"{key}:{x[key]}")
        if "r" in x:
            bits.append(f"r:{js_str(x['r'])}")
        if "l" in x:
            bits.append("l:[" + ",".join(js_str(v) for v in x["l"]) + "]")
        if "m" in x:
            bits.append("m:[" + ",".join(js_str(v) for v in x["m"]) + "]")
        parts.append(f"{k}:{{{','.join(bits)}}}")
    return "{" + ",".join(parts) + "}"


def build_block(act, start, extra):
    today = date.today().strftime("%Y-%m-%d")
    return (
        "/* KB-DATA-BEGIN — generated by kanban-update.py; manual edits inside will be overwritten */\n"
        f"  var KB_UPDATED = {js_str(today)};\n"
        f"  var ACT = {js_map_str(act)};\n"
        "  /* start date: first git commit; '' — no git history */\n"
        f"  var START = {js_map_str(start)};\n"
        "  /* repo facts: c=commits, a=authors, b=branches, w=worktrees, d=uncommitted, f=files, l=stack, m=infra/markers, r=remote, r7=commits in last 7 days */\n"
        f"  var EXTRA = {js_map_extra(extra)};\n"
        "  /* KB-DATA-END */"
    )


def p_headline(raw_path):
    base = os.path.basename(os.path.normpath(os.path.expanduser(str(raw_path))))
    return base or "untitled"


def auto_register(text, projects):
    """Append minimal P entries for configured repos missing from the manual list."""
    m = re.search(r"var P = \[(.*?)\n  \];", text, re.S)
    if not m:
        return text, 0
    body = m.group(1)
    added = 0
    inserts = []
    for pid, raw in projects.items():
        if f"['{pid}'," in body or f"['{pid}', " in body:
            continue
        path_disp = "~/" + os.path.relpath(os.path.expanduser(str(raw)), os.path.expanduser("~")) \
            if str(raw).startswith("~") or os.path.expanduser(str(raw)).startswith(os.path.expanduser("~")) \
            else str(raw)
        inserts.append(
            f"    ['{pid}',{js_str(p_headline(raw))},'product','solo','idea',{js_str(path_disp)},'',''] {AUTO_COMMENT}"
        )
        added += 1
    if not inserts:
        return text, 0
    # normalize: exactly one comma between array elements regardless of how the
    # manual block ended (a missing comma would parse "next[entry]" as an index
    # access and leave an undefined hole in P, blanking the board)
    body_norm = body.rstrip()
    if body_norm.endswith(","):
        body_norm = body_norm[:-1].rstrip()
    new_body = body_norm + ",\n" + ",\n".join(inserts) + "\n"
    return text[:m.start(1)] + new_body + text[m.end(1):], added


def main():
    kanban = resolve_kanban_path(sys.argv)
    config, cfg_path = load_config(kanban)
    projects = config.get("projects", {})
    if not projects:
        print(f"ERROR: kanban-projects.json not found or empty (looked next to {kanban} and the script)")
        sys.exit(1)
    act, start, extra = collect(projects)
    with open(kanban, encoding="utf-8") as f:
        text = f.read()
    if config.get("auto_register", True):
        text, n_added = auto_register(text, projects)
    else:
        n_added = 0
    block = build_block(act, start, extra)
    new_text, n = re.subn(r"/\* KB-DATA-BEGIN.*?/\* KB-DATA-END \*/", block, text, flags=re.S)
    if n != 1:
        print(f"ERROR: KB-DATA markers not found or ambiguous ({n})")
        sys.exit(1)
    for guard in GUARDS:
        if guard not in new_text:
            print(f"ERROR: {guard} missing after replacement — markers would swallow manual data, write cancelled")
            sys.exit(1)
    if new_text == text:
        print("No changes.")
        return
    backup = kanban + ".bak"
    with open(backup, "w", encoding="utf-8") as f:
        f.write(text)
    tmp = kanban + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new_text)
    os.replace(tmp, kanban)
    n_act = sum(1 for v in act.values() if v)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} updated: ACT={n_act}, START={len(start)}, EXTRA={len(extra)}, auto-register={n_added}; backup: {backup}")


if __name__ == "__main__":
    main()

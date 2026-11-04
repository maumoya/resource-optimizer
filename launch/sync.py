#!/usr/bin/env python3
"""Keep every published surface of a skill repo in step with its measured numbers.

One source of truth: launch/facts.json  {"key": {"value": "25%", "source": "...", "date": "YYYY-MM-DD"}}
What shows them:     launch/assets.json [{"path": "assets/card.svg", "template": "launch/templates/card.svg", "uses": [...]},
                                         {"path": "assets/demo.gif", "run": "vhs launch/demo.tape", "uses": [...]},
                                         {"name": "Social preview", "outward": "upload assets/social.png in Settings", "uses": [...]}]
Inline in any text file: <!--fact:key-->25%<!--/fact-->

Usage: sync.py check [REPO_DIR]          read-only; exit 1 when anything is stale
       sync.py apply [REPO_DIR] [--run]  render templates and markers; --run also runs generator commands
       sync.py done  [REPO_DIR] NAME     mark an outward item as done by the owner
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

MARKER = re.compile(r"<!--fact:([\w.-]+)-->(.*?)<!--/fact-->", re.S)
PLACEHOLDER = re.compile(r"\{\{([\w.-]+)\}\}")
SKIP_DIRS = {".git", "node_modules", "launch"}


def load(repo):
    launch = repo / "launch"
    facts = {k: str(v["value"]) for k, v in json.loads((launch / "facts.json").read_text()).items()}
    assets = json.loads((launch / "assets.json").read_text()) if (launch / "assets.json").exists() else []
    stamp_file = launch / ".stamp.json"
    stamp = json.loads(stamp_file.read_text()) if stamp_file.exists() else {"facts": {}, "assets": {}}
    return facts, assets, stamp, stamp_file


def asset_id(a):
    return a.get("path") or a["name"]


def facts_hash(facts, keys):
    return hashlib.sha256(json.dumps({k: facts.get(k) for k in sorted(keys)}).encode()).hexdigest()[:12]


def text_files(repo):
    for p in repo.rglob("*"):
        if p.is_file() and not SKIP_DIRS & set(p.relative_to(repo).parts):
            try:
                yield p, p.read_text()
            except (UnicodeDecodeError, OSError):
                continue


def render(text, facts):
    return PLACEHOLDER.sub(lambda m: facts.get(m.group(1), m.group(0)), text)


def check(repo):
    facts, assets, stamp, _ = load(repo)
    rows = []
    for a in assets:
        missing = [k for k in a.get("uses", []) if k not in facts]
        if missing:
            rows.append(("UNKNOWN FACT", asset_id(a), ", ".join(missing)))
            continue
        h = facts_hash(facts, a.get("uses", []))
        if "template" in a:
            want = render((repo / a["template"]).read_text(), facts)
            target = repo / a["path"]
            if not target.exists() or target.read_text() != want:
                rows.append(("STALE", a["path"], "re-render: sync.py apply"))
        elif stamp["assets"].get(asset_id(a)) != h:
            how = f"run: {a['run']}" if "run" in a else f"owner: {a['outward']}"
            rows.append(("STALE", asset_id(a), how))
    for p, text in text_files(repo):
        for m in MARKER.finditer(text):
            key, shown = m.group(1), m.group(2)
            if key not in facts:
                rows.append(("UNKNOWN FACT", str(p.relative_to(repo)), key))
            elif shown != facts[key]:
                rows.append(("DRIFT", str(p.relative_to(repo)), f"{key}: shows {shown!r}, fact is {facts[key]!r}"))
    old = {stamp["facts"][k] for k in stamp["facts"] if k in facts and stamp["facts"][k] != facts[k]}
    old -= set(facts.values())  # a value another fact still uses is not a leftover
    generated = {a["path"] for a in assets if "path" in a}  # already reported as STALE
    for p, text in text_files(repo):
        if str(p.relative_to(repo)) in generated:
            continue
        plain = MARKER.sub("", text)
        for value in sorted(old):
            for n, line in enumerate(plain.splitlines(), 1):
                if re.search(r"(?<![\w.])" + re.escape(value) + r"(?![\w])", line):
                    rows.append(("LEFTOVER", f"{p.relative_to(repo)}:{n}", f"old value {value!r} still shown"))
    return rows


def apply(repo, run):
    facts, assets, stamp, stamp_file = load(repo)
    for p, text in text_files(repo):
        new = MARKER.sub(lambda m: f"<!--fact:{m.group(1)}-->{facts.get(m.group(1), m.group(2))}<!--/fact-->", text)
        if new != text:
            p.write_text(new)
            print(f"updated  {p.relative_to(repo)}")
    for a in assets:
        h = facts_hash(facts, a.get("uses", []))
        if "template" in a:
            target = repo / a["path"]
            want = render((repo / a["template"]).read_text(), facts)
            if not target.exists() or target.read_text() != want:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(want)
                print(f"rendered {a['path']}")
            stamp["assets"][asset_id(a)] = h
        elif "run" in a and stamp["assets"].get(asset_id(a)) != h:
            if not run:
                print(f"needs    {asset_id(a)}: {a['run']}  (rerun with --run)")
                continue
            print(f"running  {a['run']}")
            subprocess.run(a["run"], shell=True, cwd=repo, check=True)
            stamp["assets"][asset_id(a)] = h
        elif "outward" in a and stamp["assets"].get(asset_id(a)) != h:
            print(f"owner    {asset_id(a)}: {a['outward']}  (then: sync.py done . {json.dumps(asset_id(a))})")
    # old values stay in the stamp until no file shows them, so LEFTOVER keeps flagging them
    if not any(r[0] == "LEFTOVER" for r in check(repo)):
        stamp["facts"] = facts
    stamp_file.write_text(json.dumps(stamp, indent=1, sort_keys=True) + "\n")


def done(repo, name):
    facts, assets, stamp, stamp_file = load(repo)
    a = next((a for a in assets if asset_id(a) == name), None)
    if a is None:
        sys.exit(f"no asset named {name!r}")
    stamp["assets"][name] = facts_hash(facts, a.get("uses", []))
    stamp_file.write_text(json.dumps(stamp, indent=1, sort_keys=True) + "\n")


def main(argv):
    if not argv or argv[0] not in {"check", "apply", "done"}:
        sys.exit(__doc__)
    cmd, rest = argv[0], [a for a in argv[1:] if a != "--run"]
    if cmd == "done":
        if not rest:
            sys.exit("usage: sync.py done [REPO_DIR] NAME")
        return done(pathlib.Path(rest[0] if len(rest) > 1 else ".").resolve(), rest[-1])
    repo = pathlib.Path(rest[0] if rest else ".").resolve()
    if cmd == "apply":
        apply(repo, "--run" in argv)
    rows = check(repo)
    for kind, where, what in rows:
        print(f"{kind:12} {where}  {what}")
    if not rows:
        print("in sync: every surface shows the current facts")
    return 1 if rows and cmd == "check" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

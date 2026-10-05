#!/usr/bin/env python3
"""Repository checks that complement `agentskills validate`.

Run from the repository root: python scripts/validate_repo.py
Exits non-zero and lists every problem found.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MAX_DESCRIPTION = 1024
MAX_SKILL_LINES = 500
TRIGGER_CASES = 20

errors = []


def fail(msg):
    errors.append(msg)


def skill_dirs():
    return sorted(p.parent for p in ROOT.glob("*/SKILL.md"))


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, text
    _, fm, body = text.split("---", 2)
    return yaml.safe_load(fm), body


def check_skill(d):
    name = d.name
    fm, body = frontmatter(d / "SKILL.md")
    if fm is None:
        fail(f"{name}: SKILL.md has no frontmatter")
        return
    if fm.get("name") != name:
        fail(f"{name}: frontmatter name {fm.get('name')!r} does not match folder")
    desc = fm.get("description") or ""
    if not desc.strip():
        fail(f"{name}: empty description")
    if len(desc) > MAX_DESCRIPTION:
        fail(f"{name}: description is {len(desc)} chars (max {MAX_DESCRIPTION})")
    version = (fm.get("metadata") or {}).get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(version)):
        fail(f"{name}: metadata.version {version!r} is not semver")
    lines = (d / "SKILL.md").read_text(encoding="utf-8").count("\n") + 1
    if lines > MAX_SKILL_LINES:
        fail(f"{name}: SKILL.md has {lines} lines (max {MAX_SKILL_LINES})")
    for link in re.findall(r"\]\(([^)#\s]+)\)", body):
        if not link.startswith(("http://", "https://")) and not (d / link).exists():
            fail(f"{name}: SKILL.md links to missing file {link}")


def check_evals(d, all_queries):
    name = d.name
    evals_path = d / "evals" / "evals.json"
    trig_path = d / "evals" / "trigger-evals.json"
    for p in (evals_path, trig_path):
        if not p.exists():
            fail(f"{name}: missing {p.relative_to(ROOT)}")
            return 0
    try:
        ev = json.loads(evals_path.read_text(encoding="utf-8"))
        trig = json.loads(trig_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{name}: invalid JSON: {e}")
        return 0
    if ev.get("skill_name") != name:
        fail(f"{name}: evals.json skill_name {ev.get('skill_name')!r} does not match folder")
    ids = [c.get("id") for c in ev.get("evals", [])]
    if len(ids) != len(set(ids)):
        fail(f"{name}: duplicate eval ids {ids}")
    for c in ev.get("evals", []):
        if not str(c.get("prompt", "")).strip():
            fail(f"{name}: eval {c.get('id')} has an empty prompt")
        exp = c.get("expectations")
        if not exp or not all(isinstance(x, str) and x.strip() for x in exp):
            fail(f"{name}: eval {c.get('id')} needs non-empty string expectations")
        for f in c.get("files", []):
            if not ((d / f).exists() or (d / "evals" / f).exists()):
                fail(f"{name}: eval {c.get('id')} references missing file {f}")
    if len(trig) != TRIGGER_CASES:
        fail(f"{name}: {len(trig)} trigger cases (expected {TRIGGER_CASES})")
    pos = sum(1 for q in trig if q.get("should_trigger") is True)
    neg = sum(1 for q in trig if q.get("should_trigger") is False)
    if (pos, neg) != (TRIGGER_CASES // 2, TRIGGER_CASES // 2):
        fail(f"{name}: trigger balance {pos} positive / {neg} negative (expected 10/10)")
    for q in trig:
        key = str(q.get("query", "")).strip().lower()
        if not key:
            fail(f"{name}: empty trigger query")
        elif key in all_queries:
            fail(f"{name}: trigger query duplicated from {all_queries[key]}")
        else:
            all_queries[key] = name
    return len(ev.get("evals", []))


def check_doc_links():
    docs = [p for p in ROOT.rglob("*.md") if ".git" not in p.parts and not p.name == "SKILL.md"]
    for p in docs:
        text = p.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)#\s]+)\)", text):
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            if not (p.parent / link).exists():
                fail(f"{p.relative_to(ROOT)}: link to missing file {link}")


LOCAL_PATH = re.compile(r"[A-Za-z]:\\\\?Users\\\\?[A-Za-z0-9._-]+|/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/")
SECRETS = re.compile(
    r"sk-ant-[A-Za-z0-9_-]{10,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|gho_[A-Za-z0-9]{30,}"
    r"|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
)
TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".html", ".toml", ".cfg", ".sh", ".ps1"}


def check_hygiene():
    for p in ROOT.rglob("*"):
        if ".git" in p.parts or not p.is_file():
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES and p.name != "LICENSE":
            continue
        if p.resolve() == Path(__file__).resolve():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        rel = p.relative_to(ROOT)
        m = LOCAL_PATH.search(text)
        if m:
            fail(f"{rel}: absolute local path {m.group()!r}")
        m = SECRETS.search(text)
        if m:
            fail(f"{rel}: possible secret {m.group()[:12]}...")
    for p in ROOT.rglob("*.zip"):
        if ".git" not in p.parts:
            fail(f"{p.relative_to(ROOT)}: binary archives belong in a GitHub Release, not the repository")


def check_doc_numbers(skills, total_cases, total_triggers):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    m = re.search(r"collection of (\d+) agent skills", readme)
    if not m or int(m.group(1)) != len(skills):
        fail(f"README.md: skill count {m.group(1) if m else 'missing'} != {len(skills)}")
    for name in skills:
        if f"[{name}]({name}/SKILL.md)" not in readme:
            fail(f"README.md: skill table is missing {name}")
    catalog = (ROOT / "AGENT-ENGINEERING-SKILLS.md").read_text(encoding="utf-8")
    for name in skills:
        if f"[{name}]({name}/SKILL.md)" not in catalog:
            fail(f"AGENT-ENGINEERING-SKILLS.md: catalogue is missing {name}")
    report = (ROOT / "VALIDATION-REPORT.md").read_text(encoding="utf-8")
    m = re.search(r"collection total (\d+)", report)
    if not m or int(m.group(1)) != total_cases:
        fail(f"VALIDATION-REPORT.md: 'collection total' {m.group(1) if m else 'missing'} != {total_cases} behavioral cases")
    for doc, text in (("README.md", readme), ("VALIDATION-REPORT.md", report)):
        for n in re.findall(r"/(\d+) (?:queries|balanced queries)|(\d+) balanced queries", text):
            val = int(n[0] or n[1])
            if val != total_triggers:
                fail(f"{doc}: trigger query count {val} != {total_triggers}")


def main():
    skills = skill_dirs()
    if not skills:
        fail("no skills found")
    all_queries = {}
    total_cases = 0
    for d in skills:
        check_skill(d)
        total_cases += check_evals(d, all_queries)
    check_doc_links()
    check_hygiene()
    check_doc_numbers([d.name for d in skills], total_cases, len(all_queries))
    if errors:
        print(f"{len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {len(skills)} skills, {total_cases} behavioral cases, {len(all_queries)} trigger queries")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Turn a structured brief into a PRD, and lint it for the things reviewers always catch."""

from __future__ import annotations

import json
import re
from pathlib import Path

REQUIRED = ["title", "problem", "users", "goals", "metrics", "scope", "out_of_scope", "risks"]
VAGUE = ["fast", "easy", "intuitive", "seamless", "simple", "user-friendly", "robust", "better", "improve", "optimize", "scalable", "etc"]
NUMBER = re.compile(r"\d")


def lint(brief: dict) -> list[str]:
    issues: list[str] = []
    for k in REQUIRED:
        if not brief.get(k):
            issues.append(f"missing: {k}")
    for m in brief.get("metrics", []):
        text = m if isinstance(m, str) else m.get("name", "")
        if not NUMBER.search(json.dumps(m)):
            issues.append(f"metric has no target number: '{text}'")
    for field in ("problem", "goals"):
        blob = json.dumps(brief.get(field, "")).lower()
        for w in VAGUE:
            if re.search(rf"\b{re.escape(w)}\b", blob):
                issues.append(f"vague word in {field}: '{w}' (say how much, for whom, by when)")
    if brief.get("scope") and not brief.get("out_of_scope"):
        issues.append("scope without out-of-scope invites creep: name what you will not do")
    if len(brief.get("goals", [])) > 3:
        issues.append(f"{len(brief['goals'])} goals: pick at most 3, or none of them are goals")
    return issues


def render(brief: dict) -> str:
    li = lambda xs: "\n".join(f"- {x}" for x in xs) or "- (none)"
    metrics = "\n".join(
        f"| {m['name']} | {m.get('baseline', 'n/a')} | {m.get('target', 'n/a')} | {m.get('by', 'n/a')} |" if isinstance(m, dict) else f"| {m} | | | |"
        for m in brief.get("metrics", [])
    )
    issues = lint(brief)
    review = "\n".join(f"- [ ] {i}" for i in issues) if issues else "- [x] Brief passes the lint checks"
    return f"""# {brief.get('title', 'Untitled')}

**Owner:** {brief.get('owner', 'TBD')} · **Status:** {brief.get('status', 'Draft')}

## Problem
{brief.get('problem', '')}

## Who it's for
{li(brief.get('users', []))}

## Goals
{li(brief.get('goals', []))}

## Success metrics
| Metric | Baseline | Target | By |
|---|---|---|---|
{metrics}

## Scope
{li(brief.get('scope', []))}

## Out of scope
{li(brief.get('out_of_scope', []))}

## Risks and open questions
{li(brief.get('risks', []))}

## Review checklist
{review}
"""


def from_file(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

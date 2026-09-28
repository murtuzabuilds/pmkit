"""RICE prioritization, plus the question most RICE sheets never answer: how fragile is this ranking?"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

IMPACT = {"massive": 3, "high": 2, "medium": 1, "low": 0.5, "minimal": 0.25}


@dataclass
class Item:
    name: str
    reach: float        # people or events per quarter
    impact: float       # 0.25 .. 3
    confidence: float   # 0 .. 1
    effort: float       # person-months

    @property
    def score(self) -> float:
        return round(self.reach * self.impact * self.confidence / self.effort, 1) if self.effort > 0 else 0.0


def parse_impact(v: str) -> float:
    v = str(v).strip().lower()
    return IMPACT[v] if v in IMPACT else float(v)


def parse_conf(v: str) -> float:
    v = str(v).strip().rstrip("%")
    x = float(v)
    return x / 100 if x > 1 else x


def load(path: str | Path) -> list[Item]:
    with open(path, newline="", encoding="utf-8") as f:
        return [Item(r["name"], float(r["reach"]), parse_impact(r["impact"]), parse_conf(r["confidence"]), float(r["effort"])) for r in csv.DictReader(f)]


def rank(items: list[Item]) -> list[Item]:
    return sorted(items, key=lambda i: i.score, reverse=True)


def flip_confidence(items: list[Item]) -> dict[str, float | None]:
    """For each item, the confidence it would need to move up one place. None for the leader.

    If an item only needs a few points of confidence to overtake the one above it, the
    ranking is a coin flip and worth a cheap experiment before committing a roadmap slot.
    """
    ranked = rank(items)
    out: dict[str, float | None] = {ranked[0].name: None} if ranked else {}
    for above, it in zip(ranked, ranked[1:]):
        need = above.score * it.effort / (it.reach * it.impact) if it.reach * it.impact else float("inf")
        out[it.name] = round(need, 3)
    return out


def table(items: list[Item]) -> str:
    flips = flip_confidence(items)
    rows = ["| # | Item | Reach | Impact | Conf. | Effort | RICE | Conf. to move up |", "|---|---|---:|---:|---:|---:|---:|---|"]
    for n, it in enumerate(rank(items), 1):
        f = flips[it.name]
        note = "leader" if f is None else ("not on confidence alone" if f > 1 else f"{f:.0%} (+{f - it.confidence:.0%})" + (" ⚠ close call" if f - it.confidence <= 0.1 else ""))
        rows.append(f"| {n} | {it.name} | {it.reach:,.0f} | {it.impact:g} | {it.confidence:.0%} | {it.effort:g} | {it.score:,.1f} | {note} |")
    return "\n".join(rows)

"""pmkit rice | prd | winloss"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import prd, rice, winloss


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pmkit", description="Small, honest tools for product managers.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("rice", help="rank a backlog CSV and flag close calls"); a.add_argument("csv")
    b = sub.add_parser("prd", help="render and lint a PRD from a JSON brief"); b.add_argument("brief"); b.add_argument("-o", "--out")
    b.add_argument("--lint-only", action="store_true")
    c = sub.add_parser("winloss", help="build a win/loss dashboard from a deals CSV"); c.add_argument("csv"); c.add_argument("-o", "--out", default="winloss.html")
    c.add_argument("--title", default="Win/loss")
    args = ap.parse_args(argv)

    if args.cmd == "rice":
        print(rice.table(rice.load(args.csv)))
    elif args.cmd == "prd":
        brief = prd.from_file(args.brief)
        issues = prd.lint(brief)
        if args.lint_only:
            print("\n".join(issues) or "no issues")
            return 1 if issues else 0
        text = prd.render(brief)
        Path(args.out).write_text(text) if args.out else print(text)
        if issues:
            print(f"\n{len(issues)} lint issue(s), see the review checklist.")
    else:
        rows = winloss.load(args.csv)
        Path(args.out).write_text(winloss.dashboard(rows, args.title))
        print(f"wrote {args.out}\n" + "\n".join(f"· {i}" for i in winloss.insights(rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

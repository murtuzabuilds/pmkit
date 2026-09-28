from pathlib import Path

from pmkit import prd, rice, winloss

EX = Path(__file__).resolve().parents[1] / "examples"


def test_rice_score_and_rank():
    items = rice.load(EX / "backlog.csv")
    top = rice.rank(items)[0]
    assert top.name == "Smart onboarding checklist" and top.score == 3200.0


def test_flip_confidence_flags_close_calls():
    a = rice.Item("a", 100, 1, 1.0, 1)      # 100
    b = rice.Item("b", 100, 1, 0.95, 1)     # 95, needs 100% to tie
    flips = rice.flip_confidence([a, b])
    assert flips["a"] is None and flips["b"] == 1.0
    assert "close call" in rice.table([a, b])


def test_impact_words_and_percent_confidence():
    assert rice.parse_impact("massive") == 3 and rice.parse_conf("80%") == 0.8 and rice.parse_conf("0.5") == 0.5


def test_prd_lint_catches_vague_and_unmeasurable():
    issues = prd.lint({"title": "x", "problem": "Onboarding should be seamless and fast", "goals": ["a", "b", "c", "d"],
                       "metrics": ["happier users"], "scope": ["y"]})
    joined = " ".join(issues)
    for expect in ("seamless", "fast", "no target number", "4 goals", "out-of-scope", "missing: users"):
        assert expect in joined


def test_example_brief_is_clean_and_renders():
    brief = prd.from_file(EX / "brief.json")
    assert prd.lint(brief) == []
    assert "| Week-one data source connected | 62% | 75% | end of Q1 |" in prd.render(brief)


def test_winloss_dashboard_and_insights():
    rows = winloss.load(EX / "deals.csv")
    assert len(rows) == 240 and 0 < winloss.rate(rows) < 1
    html = winloss.dashboard(rows, "Sample")
    assert html.startswith("<!doctype html>") and "Why we lose" in html
    assert any("Top loss reason" in i for i in winloss.insights(rows))

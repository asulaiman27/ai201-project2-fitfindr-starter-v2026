"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs each scenario five times and writes the run log — five
because your criteria are written out of five. Criterion 5 supplies a `queries`
list so each try checks a different price ceiling. Criterion 4 supplies a
`fixed_outfit` so all five fit-card calls receive the same item and outfit.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Check the session state against the item received by tool 2.
        "name": "selected item reaches outfit tool",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Five uncached cards for the same selected item and outfit.
        "name": "fit card details for the same item",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "fixed_outfit": "Baggy dark denim, black combat boots, and a brown leather belt.",
        "criterion": 4,
    },
    {
        # A distinct matching, price-capped query on each of five tries.
        "name": "price ceilings filter five queries",
        "queries": [
            "vintage graphic tee under $30",
            "90s track jacket under $50",
            "leather belt under $20",
            "denim jacket under $45",
            "silk button-down under $30",
        ],
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        queries = scenario.get("queries", [scenario.get("query", "")])
        if not isinstance(queries, list) or not queries or any(
            not isinstance(query, str) or not query.strip() for query in queries
        ):
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems

VAGUE_TERMS = {
    "top": "metric undefined: could mean revenue, count, or recency",
    "best": "metric undefined: no clear ranking criterion",
    "recent": "scope undefined: relative to today or latest data date?",
    "high": "threshold undefined: no clear cutoff value",
    "popular": "metric undefined: could mean sales count or rating",
    "most": "metric undefined: 'most' by what measure?",
}

def heuristic_check(question: str) -> list[str]:
    reasons = []
    question_lower = question.lower()
    for term, reason in VAGUE_TERMS.items():
        if term in question_lower.split() or f" {term} " in f" {question_lower} ":
            reasons.append(f"'{term}': {reason}")
    return reasons
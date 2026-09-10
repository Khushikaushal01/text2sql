import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.models.schemas import ClassificationResult
from app.classifier.heuristics import heuristic_check

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a query classifier for a text-to-SQL system.
Given a user's natural language question and a list of heuristic-flagged
ambiguity signals, classify the query and score your confidence.
Do NOT flag a query as ambiguous just because it involves grouping, filtering,
or joining — only flag it if a term's meaning is genuinely unclear (e.g. "top",
"best" without a defined metric). A query with an explicit, specific criterion
is NOT ambiguous even if it requires a complex query.

Return ONLY valid JSON matching this schema, no other text:
{
  "intent": "aggregation" | "filter" | "join" | "lookup" | "unsupported",
  "is_ambiguous": true | false,
  "ambiguity_reasons": ["string", ...],
  "confidence": float between 0.0 and 1.0
}
"""

def classify(question: str) -> ClassificationResult:
    heuristic_reasons = heuristic_check(question)

    user_prompt = f"""
Question: "{question}"
Heuristic-flagged signals: {heuristic_reasons}

Classify this query.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)
    return ClassificationResult(**data)
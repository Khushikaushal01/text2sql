import os
import json
from groq import Groq
from dotenv import load_dotenv
from app.models.schemas import SQLGenerationResult

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a PostgreSQL expert. Given a natural language question
and the relevant database schema, generate a single, correct, read-only SQL query.

Rules:
- ONLY use tables/columns present in the given schema — never invent names.
- ONLY generate SELECT statements. Never DROP, DELETE, UPDATE, INSERT, ALTER.
- If a table or column name has mixed case, wrap it in double quotes exactly as given.
- Keep the query as simple as possible while still answering the question correctly.

Return ONLY valid JSON matching this schema, no other text:
{
  "sql": "the SQL query as a string",
  "tables_used": ["table1", "table2"],
  "explanation": "one sentence explaining what the query does",
  "confidence": float between 0.0 and 1.0
}
"""

def generate_sql(question: str, schema_context: dict) -> SQLGenerationResult:
    user_prompt = f"""
Question: "{question}"

Relevant schema:
{json.dumps(schema_context, indent=2)}
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
    return SQLGenerationResult(**data)
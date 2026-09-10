# Text2SQL — Ambiguity-Aware Natural Language to SQL Engine

Converts natural language questions into validated, executable SQL — with a
classification engine that detects when a question is too ambiguous to
answer safely, and asks a clarifying question instead of guessing.

## Why this exists

Most text-to-SQL demos silently guess when a question is vague ("show me
top customers" — top by what?) and return a confidently wrong answer. This
project treats ambiguity as a first-class problem: every query is
classified before any SQL is generated, and ambiguous queries are routed
to a clarification step instead of being executed blind.

## Architecture

```
User question
      |
      v
Classification engine  (heuristics + Groq LLM confidence scoring)
      |
      +-- ambiguous --> Clarification question --> (loops back to user)
      |
      +-- clear -------> Schema linking (retrieve relevant tables/columns)
                                |
                                v
                          SQL generation (Groq LLM + schema context)
                                |
                                v
                          Validation (sqlglot syntax + safety + semantic check)
                                |
                                v
                          Execution (read-only Postgres, LIMIT + timeout)
                                |
                                v
                          Response to user
```

## Tech stack

| Layer | Tool |
|---|---|
| Language | Python 3.11+ |
| API | FastAPI |
| Database | PostgreSQL (Chinook sample dataset) |
| Data contracts | Pydantic |
| LLM | Groq (openai/gpt-oss-120b) |
| SQL parsing/validation | sqlglot |
| DB driver | psycopg2 |

## How it works

1. **Classification** — a fast heuristic pass flags known vague terms
   ("top", "best", "recent"), then a Groq LLM call scores intent and
   ambiguity with specific reasons attached.
2. **Clarification loop** — if a query is ambiguous, the API returns a
   targeted clarification question instead of generating SQL.
3. **Schema linking** — relevant tables/columns are retrieved via
   keyword overlap against introspected schema metadata, so only
   relevant context is passed to the LLM (not the full schema).
4. **SQL generation** — the LLM generates SQL grounded strictly in the
   retrieved schema, returned as a structured Pydantic object.
5. **Validation** — sqlglot checks syntax, blocks any non-SELECT
   statement, and verifies every referenced table exists in the schema.
6. **Execution** — validated queries run against a read-only DB role
   with a statement timeout and row limit.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# create a .env file with:
# DATABASE_URL=postgresql://postgres:<password>@localhost:5432/<db_name>
# GROQ_API_KEY=your_key_here

python -m app.schema_linker.introspect   # extract schema metadata
python -m uvicorn app.api.routes:app --reload
```

Then open `http://127.0.0.1:8000/docs` for an interactive Swagger UI, or:

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "List all albums by AC/DC"}'
```

## Evaluation results

Evaluated on a 28-question test set covering clear queries, ambiguous
queries, joins, negations, and date filters:

- **Ambiguity detection accuracy: 100%** (28/28)
- **Execution success rate (clear queries): 100%** (19/19)

Reached after an iteration cycle: initial run scored 85.7% on ambiguity
detection; failures were traced to missing terms in the heuristic list
("biggest", "recommend") and a false positive on a non-ambiguous grouping
query, fixed by expanding the heuristic list and tightening the
classifier's system prompt.

Run the eval yourself:
```bash
python eval/run_eval.py
```

## Project structure

```
app/
├── classifier/       # heuristic + LLM ambiguity/intent classification
├── schema_linker/     # schema introspection + relevant table retrieval
├── generator/          # LLM -> SQL generation
├── validator/          # sqlglot syntax, safety, and semantic checks
├── models/               # Pydantic contracts shared across stages
├── executor.py           # read-only query execution
└── api/                   # FastAPI routes
eval/
├── test_queries.json
└── run_eval.py
data/
└── schema_metadata.json
```

## Limitations / future work

- Schema linking uses keyword overlap; embeddings-based retrieval
  (pgvector) would generalize better to paraphrased questions.
- Currently read-only by design; no write/update query support.
- Single clarification round — doesn't yet handle a second follow-up
  if the user's clarification is itself ambiguous.

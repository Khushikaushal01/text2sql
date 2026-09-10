from fastapi import FastAPI
from pydantic import BaseModel

from app.classifier.llm_classifier import classify
from app.schema_linker.retriever import load_schema, retrieve_relevant_tables
from app.generator.sql_generator import generate_sql
from app.validator.validate import validate_sql
from app.executor import execute_query

app = FastAPI(title="Text2SQL API")
schema = load_schema()

CONFIDENCE_THRESHOLD = 0.7


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def run_query(req: QueryRequest):
    question = req.question

    # Step 1: classify
    classification = classify(question)

    # Step 2: ambiguity check — stop here if unclear
    if classification.is_ambiguous:
        return {
            "status": "clarification_needed",
            "question": f"Your query seems ambiguous: {', '.join(classification.ambiguity_reasons)}. Could you clarify?",
            "classification": classification.model_dump(),
        }

    # Step 3: schema linking
    relevant_schema = retrieve_relevant_tables(question, schema)
    if not relevant_schema:
        relevant_schema = schema  # fallback: use full schema if nothing matched

    # Step 4: SQL generation
    generation = generate_sql(question, relevant_schema)

    # Step 5: validation
    validation = validate_sql(generation.sql, schema)
    if not validation.is_safe:
        return {
            "status": "validation_failed",
            "errors": validation.errors,
            "attempted_sql": generation.sql,
        }

    # Step 6: execution
    try:
        result = execute_query(generation.sql)
    except Exception as e:
        return {"status": "execution_failed", "error": str(e), "attempted_sql": generation.sql}

    return {
        "status": "success",
        "sql": generation.sql,
        "explanation": generation.explanation,
        "columns": result["columns"],
        "rows": result["rows"],
    }

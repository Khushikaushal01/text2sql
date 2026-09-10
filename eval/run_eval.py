import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.classifier.llm_classifier import classify
from app.schema_linker.retriever import load_schema, retrieve_relevant_tables
from app.generator.sql_generator import generate_sql
from app.validator.validate import validate_sql
from app.executor import execute_query

schema = load_schema()

with open("eval/test_queries.json") as f:
    test_cases = json.load(f)

results = []
correct_ambiguity = 0
correct_execution = 0
total_clear = 0

for case in test_cases:
    question = case["question"]
    expected_ambiguous = case["expected_ambiguous"]

    classification = classify(question)
    ambiguity_match = classification.is_ambiguous == expected_ambiguous
    if ambiguity_match:
        correct_ambiguity += 1

    row = {
        "question": question,
        "expected_ambiguous": expected_ambiguous,
        "predicted_ambiguous": classification.is_ambiguous,
        "ambiguity_correct": ambiguity_match,
    }

    if not expected_ambiguous:
        total_clear += 1
        try:
            relevant_schema = retrieve_relevant_tables(question, schema) or schema
            generation = generate_sql(question, relevant_schema)
            validation = validate_sql(generation.sql, schema)
            if validation.is_safe:
                execute_query(generation.sql)
                row["execution_success"] = True
                correct_execution += 1
            else:
                row["execution_success"] = False
                row["error"] = validation.errors
        except Exception as e:
            row["execution_success"] = False
            row["error"] = str(e)

    results.append(row)

print(json.dumps(results, indent=2))
print(f"\n--- Summary ---")
print(f"Ambiguity detection accuracy: {correct_ambiguity}/{len(test_cases)} ({100*correct_ambiguity/len(test_cases):.1f}%)")
print(f"Execution success rate (clear queries): {correct_execution}/{total_clear} ({100*correct_execution/total_clear:.1f}%)")

from app.schema_linker.retriever import load_schema, retrieve_relevant_tables

schema = load_schema()

questions = [
    "Show me the top customers by total spend",
    "List all albums by AC/DC",
]

for q in questions:
    relevant = retrieve_relevant_tables(q, schema)
    print(f"\nQ: {q}")
    print("Relevant tables:", list(relevant.keys()))
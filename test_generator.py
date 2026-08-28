from app.schema_linker.retriever import load_schema, retrieve_relevant_tables
from app.generator.sql_generator import generate_sql

schema = load_schema()

question = "List all albums by AC/DC"
relevant_schema = retrieve_relevant_tables(question, schema)

result = generate_sql(question, relevant_schema)
print(result.model_dump_json(indent=2))
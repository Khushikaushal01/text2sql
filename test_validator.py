from app.validator.validate import validate_sql
from app.schema_linker.retriever import load_schema

schema = load_schema()

good_sql = "SELECT album.title FROM album JOIN artist ON album.artist_id = artist.artist_id WHERE artist.name = 'AC/DC'"
bad_sql_1 = "DROP TABLE album;"
bad_sql_2 = "SELECT * FROM nonexistent_table;"

for label, sql in [("good", good_sql), ("drop", bad_sql_1), ("bad_table", bad_sql_2)]:
    result = validate_sql(sql, schema)
    print(f"\n[{label}]")
    print(result.model_dump_json(indent=2))
import json
import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

def introspect_schema():
    engine = create_engine(os.getenv("DATABASE_URL"))
    inspector = inspect(engine)

    schema_data = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        pk = inspector.get_pk_constraint(table_name)
        fks = inspector.get_foreign_keys(table_name)

        schema_data[table_name] = {
            "columns": [
                {"name": col["name"], "type": str(col["type"])}
                for col in columns
            ],
            "primary_key": pk.get("constrained_columns", []),
            "foreign_keys": [
                {
                    "column": fk["constrained_columns"],
                    "references_table": fk["referred_table"],
                    "references_column": fk["referred_columns"],
                }
                for fk in fks
            ],
        }

    return schema_data


if __name__ == "__main__":
    schema = introspect_schema()
    with open("data/schema_metadata.json", "w") as f:
        json.dump(schema, f, indent=2)
    print(f"Extracted {len(schema)} tables → data/schema_metadata.json")
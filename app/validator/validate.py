import sqlglot
from sqlglot import exp
from app.models.schemas import ValidationResult

FORBIDDEN_STATEMENTS = {"drop", "delete", "update", "insert", "alter", "truncate", "create"}


def validate_sql(sql: str, schema: dict) -> ValidationResult:
    errors = []

    # 1. Syntax check
    try:
        parsed = sqlglot.parse_one(sql, read="postgres")
    except Exception as e:
        return ValidationResult(is_safe=False, is_syntactically_valid=False, errors=[f"Syntax error: {e}"])

    # 2. Safety check — only SELECT allowed
    statement_type = type(parsed).__name__.lower()
    if statement_type != "select":
        errors.append(f"Unsafe statement type: {statement_type}. Only SELECT is allowed.")

    sql_lower = sql.lower()
    for forbidden in FORBIDDEN_STATEMENTS:
        if forbidden in sql_lower.split():
            errors.append(f"Forbidden keyword detected: {forbidden}")

    # 3. Semantic check — tables/columns must exist in schema
    schema_tables_lower = {t.lower(): t for t in schema.keys()}
    used_tables = {t.name.lower() for t in parsed.find_all(exp.Table)}

    for table in used_tables:
        if table not in schema_tables_lower:
            errors.append(f"Unknown table referenced: {table}")

    is_safe = len(errors) == 0
    return ValidationResult(
        is_safe=is_safe,
        is_syntactically_valid=True,
        errors=errors,
    )
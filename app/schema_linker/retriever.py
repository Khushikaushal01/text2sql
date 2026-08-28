import json
import re

def load_schema(path: str = "data/schema_metadata.json") -> dict:
    with open(path) as f:
        return json.load(f)

def _stem(word: str) -> str:
    # naive plural stripping: albums -> album, customers -> customer
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return {_stem(w) for w in words}



def retrieve_relevant_tables(question: str, schema: dict, top_k: int = 3) -> dict:
    question_tokens = _tokenize(question)
    scores = {}

    for table_name, table_info in schema.items():
        # build a searchable text blob: table name + all column names
        table_tokens = _tokenize(table_name)
        for col in table_info["columns"]:
            table_tokens |= _tokenize(col["name"])

        overlap = len(question_tokens & table_tokens)
        if overlap > 0:
            scores[table_name] = overlap

    # sort by overlap score, take top_k
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_tables = [name for name, _ in ranked[:top_k]]

    # always include tables directly linked via foreign keys to the top picks
    # so joins remain possible
    linked = set(top_tables)
    for name in top_tables:
        for fk in schema[name]["foreign_keys"]:
            linked.add(fk["references_table"])

    return {name: schema[name] for name in linked if name in schema}
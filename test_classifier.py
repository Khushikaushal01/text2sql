from app.classifier.llm_classifier import classify

questions = [
    "Show me the top customers",
    "List all albums by AC/DC",
    "What is the total revenue last month?",
]

for q in questions:
    result = classify(q)
    print(f"\nQ: {q}")
    print(result.model_dump_json(indent=2))
from app.models.schemas import ClassificationResult, ClarificationRequest

result = ClassificationResult(
    intent="aggregation",
    is_ambiguous=True,
    ambiguity_reasons=["metric undefined: 'top' could mean revenue or order count"],
    confidence=0.62,
)
print(result.model_dump_json(indent=2))

clarification = ClarificationRequest(
    question="By 'top customers', do you mean by total spend or number of orders?",
    options=["total spend", "number of orders"],
)
print(clarification.model_dump_json(indent=2))
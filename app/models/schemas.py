from pydantic import BaseModel, Field
from typing import Literal


class ClassificationResult(BaseModel):
    intent: Literal["aggregation", "filter", "join", "lookup", "unsupported"]
    is_ambiguous: bool
    ambiguity_reasons: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class ClarificationRequest(BaseModel):
    question: str
    options: list[str] = Field(default_factory=list)


class SQLGenerationResult(BaseModel):
    sql: str
    tables_used: list[str]
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)


class ValidationResult(BaseModel):
    is_safe: bool
    is_syntactically_valid: bool
    errors: list[str] = Field(default_factory=list)
from pydantic import BaseModel, Field
from typing import Literal

class ClassificationOutput(BaseModel):
    category: Literal["Billing", "Technical Issue", "Account/Access", "Feature Request", "Complaint", "Other"]
    summary: str


class JudgeOutput(BaseModel):
    score: int = Field(ge=1, le=10)
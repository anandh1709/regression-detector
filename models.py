from pydantic import BaseModel, Field
from typing import Literal

# Expected structure of the classifier's response
class ClassificationOutput(BaseModel):
    category: Literal["Billing", "Technical Issue", "Account/Access", "Feature Request", "Complaint", "Other"]
    summary: str


# Expected structure of the judge's response
class JudgeOutput(BaseModel):
    score: int = Field(ge=1, le=10)
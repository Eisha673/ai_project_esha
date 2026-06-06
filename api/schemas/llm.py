from pydantic import BaseModel, Field


class ResumeScoreOutput(BaseModel):
    score: int = Field(ge=0, le=100)
    strengths: list[str]
    gaps: list[str]
    recommendation: str
    reasoning: str


class AssessmentSection(BaseModel):
    type: str
    question: str
    evaluation_criteria: str


class AssessmentOutput(BaseModel):
    title: str
    duration_minutes: int = Field(gt=0)
    sections: list[AssessmentSection]


class BiasCheckOutput(BaseModel):
    is_safe: bool
    raw: str


class JDValidationOutput(BaseModel):
    is_valid: bool
    suggestions: list[str]


class InterviewQuestionsOutput(BaseModel):
    questions: list[str]

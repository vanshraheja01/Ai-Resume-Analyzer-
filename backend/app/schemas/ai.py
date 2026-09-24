from pydantic import BaseModel, Field

SCORE_FIELD = Field(ge=0, le=100)


class ResumeAnalysisResult(BaseModel):
    """The contract every AIProvider must return — validated before it ever
    reaches the database or the frontend. An AI response that doesn't fit
    this shape is treated as a failure, never passed through as-is."""

    overall_score: int = SCORE_FIELD
    skills_score: int = SCORE_FIELD
    experience_score: int = SCORE_FIELD
    projects_score: int = SCORE_FIELD
    education_score: int = SCORE_FIELD
    structure_score: int = SCORE_FIELD
    job_relevance_score: int = SCORE_FIELD
    achievements_score: int = SCORE_FIELD
    keywords_score: int = SCORE_FIELD
    strengths: list[str] = Field(default_factory=list, max_length=10)
    weaknesses: list[str] = Field(default_factory=list, max_length=10)
    recommendations: list[str] = Field(default_factory=list, max_length=10)

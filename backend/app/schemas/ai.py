from pydantic import BaseModel, Field

SCORE_FIELD = Field(ge=0, le=100)


class ResumeAnalysisResult(BaseModel):

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


class JobAnalysisResult(BaseModel):
    required_skills: list[str] = Field(default_factory=list, max_length=30)
    preferred_skills: list[str] = Field(default_factory=list, max_length=30)
    min_experience_years: int | None = Field(default=None, ge=0, le=50)
    education_requirements: list[str] = Field(default_factory=list, max_length=10)
    tools_technologies: list[str] = Field(default_factory=list, max_length=30)
    keywords: list[str] = Field(default_factory=list, max_length=30)


class MatchResult(BaseModel):
    match_score: int = SCORE_FIELD
    matched_skills: list[str] = Field(default_factory=list, max_length=30)
    missing_skills: list[str] = Field(default_factory=list, max_length=30)
    partial_skills: list[str] = Field(default_factory=list, max_length=30)
    recommendations: list[str] = Field(default_factory=list, max_length=10)

from app.schemas.ai import ResumeAnalysisResult
from app.services.ai_service import MockAIProvider


def test_mock_provider_returns_valid_schema():
    provider = MockAIProvider()
    result = provider.analyze_resume(
        parsed_data={"skills": ["Python", "React"], "experience": ["Intern"], "projects": []},
        raw_text="some resume text",
    )
    assert isinstance(result, ResumeAnalysisResult)
    for score in [
        result.overall_score,
        result.skills_score,
        result.experience_score,
        result.projects_score,
    ]:
        assert 0 <= score <= 100


def test_mock_provider_rewards_more_content():
    provider = MockAIProvider()

    sparse = provider.analyze_resume(parsed_data={}, raw_text="")
    rich = provider.analyze_resume(
        parsed_data={
            "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
            "experience": ["Intern at Acme"],
            "projects": ["AI Resume Analyzer"],
            "education": ["B.Tech"],
            "achievements": ["Hackathon winner"],
        },
        raw_text="a full resume",
    )

    assert rich.overall_score > sparse.overall_score
    assert rich.skills_score > sparse.skills_score


def test_mock_provider_flags_missing_sections_as_weaknesses():
    provider = MockAIProvider()
    result = provider.analyze_resume(parsed_data={}, raw_text="x")
    assert any("skills" in w.lower() for w in result.weaknesses)


def test_resume_analysis_result_rejects_out_of_range_scores():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ResumeAnalysisResult(
            overall_score=150,  # out of range
            skills_score=50,
            experience_score=50,
            projects_score=50,
            education_score=50,
            structure_score=50,
            job_relevance_score=50,
            achievements_score=50,
            keywords_score=50,
        )

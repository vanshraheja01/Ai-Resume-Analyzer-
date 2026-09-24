from app.services.ai_service import MockAIProvider, _contains_keyword

SAMPLE_JD = """We are looking for a Full Stack Developer with experience in React, Node.js,
Python, REST APIs, PostgreSQL and Docker. 3+ years of experience required.
Bachelor degree in Computer Science or related field.

Preferred: AWS, Redis, Kubernetes experience is a plus.
"""


def test_contains_keyword_avoids_substring_false_positives():
    # "SQL" must not match inside "PostgreSQL"; "Java" must not match inside "JavaScript".
    assert not _contains_keyword("experience with postgresql database", "sql")
    assert not _contains_keyword("javascript developer", "java")
    assert not _contains_keyword("good communication skills", "go")


def test_contains_keyword_matches_symbol_heavy_keywords():
    assert _contains_keyword("experience in c++ and python", "c++")
    assert _contains_keyword("familiar with ci/cd pipelines", "ci/cd")
    assert _contains_keyword("worked with node.js backend", "node.js")


def test_analyze_job_splits_required_and_preferred_skills():
    result = MockAIProvider().analyze_job(SAMPLE_JD)
    assert "React" in result.required_skills
    assert "Docker" in result.required_skills
    assert "AWS" in result.preferred_skills
    assert "Redis" in result.preferred_skills
    assert "AWS" not in result.required_skills


def test_analyze_job_does_not_false_positive_sql_inside_postgresql():
    result = MockAIProvider().analyze_job(SAMPLE_JD)
    assert "SQL" not in result.required_skills
    assert "SQL" not in result.keywords


def test_analyze_job_extracts_experience_years():
    result = MockAIProvider().analyze_job(SAMPLE_JD)
    assert result.min_experience_years == 3


def test_match_resume_job_identifies_matched_missing_and_partial():
    job_data = MockAIProvider().analyze_job(SAMPLE_JD).model_dump()
    resume_data = {"skills": ["React", "JavaScript", "REST APIs", "Python", "PostgreSQL", "Node", "TypeScript"]}

    result = MockAIProvider().match_resume_job(resume_data, job_data)

    assert "React" in result.matched_skills
    assert "Python" in result.matched_skills
    assert "Node.js" in result.partial_skills  # resume has "Node", job wants "Node.js"
    assert "Docker" in result.missing_skills
    assert 0 <= result.match_score <= 100


def test_match_resume_job_handles_empty_job_skills():
    result = MockAIProvider().match_resume_job({"skills": ["Python"]}, {})
    assert result.match_score == 50  # neutral default when there's nothing to compare against
    assert result.matched_skills == []

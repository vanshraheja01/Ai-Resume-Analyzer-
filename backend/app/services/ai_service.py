import json
import re
from abc import ABC, abstractmethod
from functools import lru_cache

from app.config import get_settings
from app.schemas.ai import JobAnalysisResult, MatchResult, ResumeAnalysisResult


class AIProviderError(Exception):
    pass


class AIProvider(ABC):
    @abstractmethod
    def analyze_resume(self, parsed_data: dict, raw_text: str) -> ResumeAnalysisResult: ...

    @abstractmethod
    def analyze_job(self, job_description: str) -> JobAnalysisResult: ...

    @abstractmethod
    def match_resume_job(self, resume_data: dict, job_data: dict) -> MatchResult: ...


TECH_KEYWORDS = [
    "React", "Angular", "Vue", "Next.js", "JavaScript", "TypeScript", "HTML", "CSS",
    "Node.js", "Python", "Java", "C++", "C#", "Go", "Rust", "Ruby", "PHP",
    "FastAPI", "Django", "Flask", "Spring", "Express",
    "REST APIs", "GraphQL", "gRPC",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQL", "SQLite",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Git", "Linux",
    "Machine Learning", "NLP", "TensorFlow", "PyTorch", "Pandas", "NumPy",
    "Agile", "Scrum",
]

_PREFERRED_SECTION_MARKERS = ["preferred", "nice to have", "nice-to-have", "bonus", "a plus"]
_EDUCATION_MARKERS = ["bachelor", "master", "b.tech", "m.tech", "phd", "degree"]
_EXPERIENCE_YEARS_RE = re.compile(r"(\d+)\+?\s*(?:years?|yrs?)", re.IGNORECASE)


def _contains_keyword(text: str, keyword: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(keyword.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


class MockAIProvider(AIProvider):

    def analyze_job(self, job_description: str) -> JobAnalysisResult:
        text_lower = job_description.lower()
        found_skills = [kw for kw in TECH_KEYWORDS if _contains_keyword(text_lower, kw)]

        split_idx = min(
            (idx for marker in _PREFERRED_SECTION_MARKERS if (idx := text_lower.find(marker)) != -1),
            default=None,
        )
        if split_idx is not None:
            required_text, preferred_text = text_lower[:split_idx], text_lower[split_idx:]
            required_skills = [kw for kw in found_skills if _contains_keyword(required_text, kw)]
            preferred_skills = [
                kw for kw in found_skills if kw not in required_skills and _contains_keyword(preferred_text, kw)
            ]
        else:
            required_skills, preferred_skills = found_skills, []

        years_match = _EXPERIENCE_YEARS_RE.search(text_lower)
        education_requirements = [kw.title() for kw in _EDUCATION_MARKERS if _contains_keyword(text_lower, kw)]

        return JobAnalysisResult(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            min_experience_years=int(years_match.group(1)) if years_match else None,
            education_requirements=education_requirements,
            tools_technologies=found_skills,
            keywords=found_skills,
        )

    def match_resume_job(self, resume_data: dict, job_data: dict) -> MatchResult:
        resume_skills = {s.lower() for s in (resume_data.get("skills") or [])}
        required = job_data.get("required_skills") or []
        preferred = job_data.get("preferred_skills") or []
        all_job_skills = list(dict.fromkeys(required + preferred))

        matched = [s for s in all_job_skills if s.lower() in resume_skills]
        unmatched = [s for s in all_job_skills if s.lower() not in resume_skills]

        partial, missing = [], []
        for skill in unmatched:
            root = re.split(r"[.\s]", skill.lower())[0]
            (partial if any(_contains_keyword(rs, root) for rs in resume_skills) else missing).append(skill)

        match_score = round(100 * len(matched) / len(all_job_skills)) if all_job_skills else 50

        recommendations = [f"Consider adding experience or a project using {s}." for s in missing[:5]]
        if not recommendations:
            recommendations.append("Strong skill overlap — tailor your summary to this role's exact keywords.")

        return MatchResult(
            match_score=match_score,
            matched_skills=matched,
            missing_skills=missing,
            partial_skills=partial,
            recommendations=recommendations,
        )

    def analyze_resume(self, parsed_data: dict, raw_text: str) -> ResumeAnalysisResult:
        skills = parsed_data.get("skills") or []
        experience = parsed_data.get("experience") or []
        projects = parsed_data.get("projects") or []
        education = parsed_data.get("education") or []
        certifications = parsed_data.get("certifications") or []
        achievements = parsed_data.get("achievements") or []

        skills_score = min(95, 45 + len(skills) * 6)
        experience_score = 85 if experience else 40
        projects_score = 85 if projects else 40
        education_score = 90 if education else 50
        structure_score = 78 if raw_text.strip() else 30
        job_relevance_score = 70
        achievements_score = 82 if achievements else 45
        keywords_score = min(90, 40 + len(skills) * 5)
        overall_score = round(
            (
                skills_score
                + experience_score
                + projects_score
                + education_score
                + structure_score
                + job_relevance_score
                + achievements_score
                + keywords_score
            )
            / 8
        )

        strengths = []
        weaknesses = []
        recommendations = []

        if skills:
            strengths.append(f"Lists {len(skills)} relevant technical skills.")
        else:
            weaknesses.append("No clearly listed technical skills section.")
            recommendations.append("Add a dedicated Skills section with your core technologies.")

        if experience:
            strengths.append("Includes concrete work experience entries.")
        else:
            weaknesses.append("No work experience section detected.")
            recommendations.append("Add internships or part-time roles, even short ones, with outcomes.")

        if projects:
            strengths.append("Showcases hands-on projects.")
        else:
            weaknesses.append("No projects section detected.")
            recommendations.append("Add 2-3 projects that demonstrate applied skills.")

        if not certifications:
            recommendations.append("Consider adding relevant certifications to strengthen credibility.")

        if not achievements:
            weaknesses.append("No achievements/awards section detected.")

        return ResumeAnalysisResult(
            overall_score=overall_score,
            skills_score=skills_score,
            experience_score=experience_score,
            projects_score=projects_score,
            education_score=education_score,
            structure_score=structure_score,
            job_relevance_score=job_relevance_score,
            achievements_score=achievements_score,
            keywords_score=keywords_score,
            strengths=strengths or ["Resume was readable and structured enough to parse."],
            weaknesses=weaknesses or ["No major structural issues detected."],
            recommendations=recommendations or ["Keep sections consistent and quantify achievements."],
        )


_RESUME_ANALYSIS_PROMPT = """You are an expert technical resume reviewer. Analyze the following resume \
and respond with ONLY a JSON object matching exactly this schema (no markdown, no commentary):

{{
  "overall_score": <0-100 int>,
  "skills_score": <0-100 int>,
  "experience_score": <0-100 int>,
  "projects_score": <0-100 int>,
  "education_score": <0-100 int>,
  "structure_score": <0-100 int>,
  "job_relevance_score": <0-100 int>,
  "achievements_score": <0-100 int>,
  "keywords_score": <0-100 int>,
  "strengths": [<string>, ...],
  "weaknesses": [<string>, ...],
  "recommendations": [<string>, ...]
}}

Parsed resume fields:
{parsed_data}

Full resume text:
{raw_text}
"""

_JOB_ANALYSIS_PROMPT = """You are an expert technical recruiter. Analyze the following job description \
and respond with ONLY a JSON object matching exactly this schema (no markdown, no commentary):

{{
  "required_skills": [<string>, ...],
  "preferred_skills": [<string>, ...],
  "min_experience_years": <int or null>,
  "education_requirements": [<string>, ...],
  "tools_technologies": [<string>, ...],
  "keywords": [<string>, ...]
}}

Job description:
{job_description}
"""

_MATCH_PROMPT = """You are an expert technical recruiter comparing a candidate's resume against a job's \
requirements. Respond with ONLY a JSON object matching exactly this schema (no markdown, no commentary). \
Do not claim the candidate is definitely qualified — this is an analysis, not a hiring guarantee.

{{
  "match_score": <0-100 int>,
  "matched_skills": [<string>, ...],
  "missing_skills": [<string>, ...],
  "partial_skills": [<string>, ...],
  "recommendations": [<string>, ...]
}}

Candidate resume data:
{resume_data}

Job requirements:
{job_data}
"""


class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def _generate_validated[T: (ResumeAnalysisResult, JobAnalysisResult, MatchResult)](
        self, prompt: str, schema_cls: type[T]
    ) -> T:
        from google.genai import types

        last_error: Exception | None = None
        for _attempt in range(2):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                data = json.loads(response.text)
                return schema_cls.model_validate(data)
            except Exception as exc:
                last_error = exc
                continue

        raise AIProviderError(f"Gemini did not return valid {schema_cls.__name__} data after retrying: {last_error}")

    def analyze_resume(self, parsed_data: dict, raw_text: str) -> ResumeAnalysisResult:
        prompt = _RESUME_ANALYSIS_PROMPT.format(
            parsed_data=json.dumps(parsed_data, indent=2),
            raw_text=raw_text[:6000],
        )
        return self._generate_validated(prompt, ResumeAnalysisResult)

    def analyze_job(self, job_description: str) -> JobAnalysisResult:
        prompt = _JOB_ANALYSIS_PROMPT.format(job_description=job_description[:6000])
        return self._generate_validated(prompt, JobAnalysisResult)

    def match_resume_job(self, resume_data: dict, job_data: dict) -> MatchResult:
        prompt = _MATCH_PROMPT.format(
            resume_data=json.dumps(resume_data, indent=2),
            job_data=json.dumps(job_data, indent=2),
        )
        return self._generate_validated(prompt, MatchResult)


@lru_cache
def get_ai_provider() -> AIProvider:
    settings = get_settings()

    if settings.ai_mode == "mock":
        return MockAIProvider()

    if settings.ai_mode == "live":
        if settings.ai_provider == "gemini":
            if not settings.gemini_api_key:
                raise AIProviderError("GEMINI_API_KEY is required when AI_MODE=live and AI_PROVIDER=gemini")
            return GeminiAIProvider(settings.gemini_api_key, settings.gemini_model)
        raise AIProviderError(f"Unsupported AI_PROVIDER: {settings.ai_provider}")

    raise AIProviderError(f"Unsupported AI_MODE: {settings.ai_mode}")

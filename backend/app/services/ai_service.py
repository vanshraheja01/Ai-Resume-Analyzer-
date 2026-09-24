"""AI provider abstraction.

Every caller depends only on `AIProvider` and `get_ai_provider()` — never on
Gemini (or any other vendor) directly. Swapping providers, or running with
no API key at all via `MockAIProvider`, means changing `AI_MODE`/`AI_PROVIDER`
in `.env`; no route or service code changes.
"""

import json
from abc import ABC, abstractmethod
from functools import lru_cache

from app.config import get_settings
from app.schemas.ai import ResumeAnalysisResult


class AIProviderError(Exception):
    """Raised when the AI provider fails or returns something we can't validate."""


class AIProvider(ABC):
    @abstractmethod
    def analyze_resume(self, parsed_data: dict, raw_text: str) -> ResumeAnalysisResult: ...


class MockAIProvider(AIProvider):
    """Deterministic, content-aware scoring with zero external calls or API key.
    Lets the whole app run and be demoed without any AI credentials."""

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
        job_relevance_score = 70  # neutral — no job description until Phase 5's matching engine
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


_ANALYSIS_PROMPT_TEMPLATE = """You are an expert technical resume reviewer. Analyze the following resume \
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


class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str):
        from google import genai  # imported lazily so `google-genai` is only required in live mode

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def analyze_resume(self, parsed_data: dict, raw_text: str) -> ResumeAnalysisResult:
        from google.genai import types

        prompt = _ANALYSIS_PROMPT_TEMPLATE.format(
            parsed_data=json.dumps(parsed_data, indent=2),
            raw_text=raw_text[:6000],  # keep prompts bounded
        )

        last_error: Exception | None = None
        for attempt in range(2):  # one retry if the model returns malformed JSON
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                data = json.loads(response.text)
                return ResumeAnalysisResult.model_validate(data)
            except Exception as exc:  # broad on purpose: API errors, bad JSON, and schema mismatches all just retry-then-fail
                last_error = exc
                continue

        raise AIProviderError(f"Gemini did not return a valid analysis after retrying: {last_error}")


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

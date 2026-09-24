from pathlib import Path

import pytest

from app.services.resume_parser import ResumeParsingError, extract_text, parse_resume

SAMPLE_RESUME = """John Doe
Bengaluru, Karnataka
john.doe@example.com | +91 98765 43210
linkedin.com/in/johndoe | github.com/johndoe

Education
B.Tech in Computer Science, XYZ University, 2022-2026

Skills
Python, FastAPI, React, PostgreSQL, Docker

Experience
Software Engineering Intern at Acme Corp
Built REST APIs used by 10k+ users

Projects
AI Resume Analyzer - a full stack resume matching platform

Certifications
AWS Certified Cloud Practitioner

Achievements
Winner, National Hackathon 2025

Languages
English, Hindi, Kannada
"""


def test_parse_resume_extracts_contact_info():
    result = parse_resume(SAMPLE_RESUME)
    assert result["name"] == "John Doe"
    assert result["email"] == "john.doe@example.com"
    assert result["phone"] == "+91 98765 43210"
    assert result["location"] == "Bengaluru, Karnataka"


def test_parse_resume_extracts_links():
    result = parse_resume(SAMPLE_RESUME)
    assert "linkedin.com/in/johndoe" in result["links"]
    assert "github.com/johndoe" in result["links"]


def test_parse_resume_extracts_sections():
    result = parse_resume(SAMPLE_RESUME)
    assert "Python" in result["skills"]
    assert "Docker" in result["skills"]
    assert any("XYZ University" in line for line in result["education"])
    assert any("Acme Corp" in line for line in result["experience"])
    assert any("AI Resume Analyzer" in line for line in result["projects"])
    assert any("AWS Certified" in line for line in result["certifications"])
    assert any("Hackathon" in line for line in result["achievements"])
    assert set(result["languages"]) == {"English", "Hindi", "Kannada"}


def test_parse_resume_handles_missing_sections_gracefully():
    minimal = "Jane Smith\njane@example.com\n"
    result = parse_resume(minimal)
    assert result["name"] == "Jane Smith"
    assert result["email"] == "jane@example.com"
    assert result["skills"] == []
    assert result["education"] == []


def test_extract_text_rejects_unsupported_type(tmp_path: Path):
    fake_file = tmp_path / "resume.pdf"
    fake_file.write_text("irrelevant")
    with pytest.raises(ResumeParsingError):
        extract_text(fake_file, "txt")


def test_extract_text_rejects_corrupted_pdf(tmp_path: Path):
    corrupt = tmp_path / "corrupt.pdf"
    corrupt.write_text("this is not a real pdf")
    with pytest.raises(ResumeParsingError):
        extract_text(corrupt, "pdf")


def test_extract_text_rejects_corrupted_docx(tmp_path: Path):
    corrupt = tmp_path / "corrupt.docx"
    corrupt.write_text("this is not a real docx")
    with pytest.raises(ResumeParsingError):
        extract_text(corrupt, "docx")

from app import models
from app.database.base import Base


def get_table(name: str):
    return Base.metadata.tables[name]


def test_all_expected_tables_exist():
    expected = {"users", "resumes", "resume_analyses", "jobs", "matches", "applications"}
    assert expected.issubset(Base.metadata.tables.keys())


def test_users_table_shape():
    users = get_table("users")
    assert "email" in users.columns
    assert users.columns["email"].unique
    assert not users.columns["email"].nullable
    assert not users.columns["hashed_password"].nullable


def test_resume_foreign_key_cascades_on_user_delete():
    resumes = get_table("resumes")
    fk = next(iter(resumes.columns["user_id"].foreign_keys))
    assert fk.column.table.name == "users"
    assert fk.ondelete == "CASCADE"


def test_resume_analysis_cascades_on_resume_delete():
    analyses = get_table("resume_analyses")
    fk = next(iter(analyses.columns["resume_id"].foreign_keys))
    assert fk.column.table.name == "resumes"
    assert fk.ondelete == "CASCADE"


def test_match_has_unique_resume_job_pair_constraint():
    matches = get_table("matches")
    unique_constraints = [c for c in matches.constraints if c.__class__.__name__ == "UniqueConstraint"]
    assert any(
        {col.name for col in uc.columns} == {"resume_id", "job_id"} for uc in unique_constraints
    )


def test_application_job_and_resume_fks_are_nullable_with_set_null():
    applications = get_table("applications")

    assert applications.columns["job_id"].nullable
    job_fk = next(iter(applications.columns["job_id"].foreign_keys))
    assert job_fk.ondelete == "SET NULL"

    assert applications.columns["resume_id"].nullable
    resume_fk = next(iter(applications.columns["resume_id"].foreign_keys))
    assert resume_fk.ondelete == "SET NULL"


def test_application_status_enum_has_all_expected_values():
    from app.models.application import ApplicationStatus

    values = {status.value for status in ApplicationStatus}
    assert values == {
        "saved",
        "applied",
        "interview",
        "technical_round",
        "offer",
        "rejected",
        "withdrawn",
    }

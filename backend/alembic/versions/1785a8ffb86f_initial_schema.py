from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '1785a8ffb86f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('location', sa.String(length=255), nullable=True),
    sa.Column('github_url', sa.String(length=500), nullable=True),
    sa.Column('linkedin_url', sa.String(length=500), nullable=True),
    sa.Column('portfolio_url', sa.String(length=500), nullable=True),
    sa.Column('preferred_role', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('jobs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('company', sa.String(length=255), nullable=True),
    sa.Column('description_raw', sa.Text(), nullable=False),
    sa.Column('extracted_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('job_url', sa.String(length=1000), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_user_id'), 'jobs', ['user_id'], unique=False)
    op.create_table('resumes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('file_path', sa.String(length=1000), nullable=False),
    sa.Column('file_type', sa.String(length=10), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=False),
    sa.Column('raw_text', sa.Text(), nullable=True),
    sa.Column('parsed_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resumes_user_id'), 'resumes', ['user_id'], unique=False)
    op.create_table('applications',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('job_id', sa.UUID(), nullable=True),
    sa.Column('resume_id', sa.UUID(), nullable=True),
    sa.Column('company', sa.String(length=255), nullable=False),
    sa.Column('position_title', sa.String(length=255), nullable=False),
    sa.Column('status', sa.Enum('SAVED', 'APPLIED', 'INTERVIEW', 'TECHNICAL_ROUND', 'OFFER', 'REJECTED', 'WITHDRAWN', name='application_status'), nullable=False),
    sa.Column('application_date', sa.Date(), nullable=True),
    sa.Column('interview_date', sa.Date(), nullable=True),
    sa.Column('job_url', sa.String(length=1000), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_job_id'), 'applications', ['job_id'], unique=False)
    op.create_index(op.f('ix_applications_resume_id'), 'applications', ['resume_id'], unique=False)
    op.create_index(op.f('ix_applications_user_id'), 'applications', ['user_id'], unique=False)
    op.create_table('matches',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('resume_id', sa.UUID(), nullable=False),
    sa.Column('job_id', sa.UUID(), nullable=False),
    sa.Column('match_score', sa.Integer(), nullable=False),
    sa.Column('matched_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('missing_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('partial_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('resume_id', 'job_id', name='uq_resume_job_match')
    )
    op.create_index(op.f('ix_matches_job_id'), 'matches', ['job_id'], unique=False)
    op.create_index(op.f('ix_matches_resume_id'), 'matches', ['resume_id'], unique=False)
    op.create_table('resume_analyses',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('resume_id', sa.UUID(), nullable=False),
    sa.Column('overall_score', sa.Integer(), nullable=False),
    sa.Column('skills_score', sa.Integer(), nullable=False),
    sa.Column('experience_score', sa.Integer(), nullable=False),
    sa.Column('projects_score', sa.Integer(), nullable=False),
    sa.Column('education_score', sa.Integer(), nullable=False),
    sa.Column('structure_score', sa.Integer(), nullable=False),
    sa.Column('job_relevance_score', sa.Integer(), nullable=False),
    sa.Column('achievements_score', sa.Integer(), nullable=False),
    sa.Column('keywords_score', sa.Integer(), nullable=False),
    sa.Column('strengths', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('weaknesses', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('ai_provider_used', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_analyses_resume_id'), 'resume_analyses', ['resume_id'], unique=False)


def downgrade() -> None:

    op.drop_index(op.f('ix_resume_analyses_resume_id'), table_name='resume_analyses')
    op.drop_table('resume_analyses')
    op.drop_index(op.f('ix_matches_resume_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_job_id'), table_name='matches')
    op.drop_table('matches')
    op.drop_index(op.f('ix_applications_user_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_resume_id'), table_name='applications')
    op.drop_index(op.f('ix_applications_job_id'), table_name='applications')
    op.drop_table('applications')
    op.drop_index(op.f('ix_resumes_user_id'), table_name='resumes')
    op.drop_table('resumes')
    op.drop_index(op.f('ix_jobs_user_id'), table_name='jobs')
    op.drop_table('jobs')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_applications: int
    by_status: dict[str, int]
    interviews: int
    offers: int
    pending: int
    total_resumes: int
    total_jobs_analyzed: int

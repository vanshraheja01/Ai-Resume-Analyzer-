from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import applications, auth, dashboard, jobs, matching, resumes
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for the AI Resume Analyzer & Job Matching Platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(applications.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"service": settings.app_name, "status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

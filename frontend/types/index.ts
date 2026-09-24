// Mirrors the backend Pydantic schemas (see backend/app/schemas/*.py) so the
// frontend and API stay in lockstep as a single source of truth to update.

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  location: string | null;
  github_url: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
  preferred_role: string | null;
}

export interface ParsedResumeData {
  name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  links: string[];
  education: string[];
  skills: string[];
  experience: string[];
  projects: string[];
  certifications: string[];
  achievements: string[];
  languages: string[];
}

export interface ResumeSummary {
  id: string;
  title: string;
  file_type: "pdf" | "docx";
  file_size: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ResumeDetail extends ResumeSummary {
  parsed_data: ParsedResumeData | null;
  raw_text: string | null;
}

export interface ResumeAnalysis {
  id: string;
  resume_id: string;
  overall_score: number;
  skills_score: number;
  experience_score: number;
  projects_score: number;
  education_score: number;
  structure_score: number;
  job_relevance_score: number;
  achievements_score: number;
  keywords_score: number;
  strengths: string[] | null;
  weaknesses: string[] | null;
  recommendations: string[] | null;
  ai_provider_used: string | null;
  created_at: string;
}

export interface JobExtractedData {
  required_skills: string[];
  preferred_skills: string[];
  min_experience_years: number | null;
  education_requirements: string[];
  tools_technologies: string[];
  keywords: string[];
}

export interface Job {
  id: string;
  title: string;
  company: string | null;
  description_raw: string;
  extracted_data: JobExtractedData | null;
  job_url: string | null;
  created_at: string;
}

export interface Match {
  id: string;
  resume_id: string;
  job_id: string;
  match_score: number;
  matched_skills: string[] | null;
  missing_skills: string[] | null;
  partial_skills: string[] | null;
  recommendations: string[] | null;
  created_at: string;
}

export type ApplicationStatus =
  | "saved"
  | "applied"
  | "interview"
  | "technical_round"
  | "offer"
  | "rejected"
  | "withdrawn";

export interface Application {
  id: string;
  company: string;
  position_title: string;
  status: ApplicationStatus;
  job_id: string | null;
  resume_id: string | null;
  application_date: string | null;
  interview_date: string | null;
  job_url: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_applications: number;
  by_status: Record<ApplicationStatus, number>;
  interviews: number;
  offers: number;
  pending: number;
  total_resumes: number;
  total_jobs_analyzed: number;
}

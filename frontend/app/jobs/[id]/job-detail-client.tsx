"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageSpinner, ErrorState } from "@/components/ui/states";
import { MatchResultPanel } from "@/components/jobs/match-result-panel";
import { useRequireAuth } from "@/lib/auth";
import { jobsApi, resumesApi, matchingApi, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { Job, ResumeSummary, Match } from "@/types";

export function JobDetailClient({ id }: { id: string }) {
  const { user, loading: authLoading } = useRequireAuth();
  const [job, setJob] = useState<Job | null>(null);
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [match, setMatch] = useState<Match | null>(null);
  const [matching, setMatching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    if (!user) return;
    Promise.all([jobsApi.get(id), resumesApi.list()])
      .then(([j, r]) => {
        setJob(j);
        setResumes(r);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load job"));
  }, [user, id]);

  async function handleMatch() {
    if (!selectedResumeId) return;
    setMatching(true);
    try {
      const result = await matchingApi.analyze(selectedResumeId, id);
      setMatch(result);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Matching failed.");
    } finally {
      setMatching(false);
    }
  }

  if (authLoading || !user) return <PageSpinner />;
  if (error) {
    return (
      <AppShell>
        <ErrorState message={error} />
      </AppShell>
    );
  }
  if (!job) return <PageSpinner />;

  const data = job.extracted_data;

  return (
    <AppShell>
      <div className="mx-auto max-w-4xl space-y-6">
        <Link href="/jobs" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back to jobs
        </Link>

        <div>
          <h1 className="text-2xl font-semibold">{job.title}</h1>
          <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
            {job.company && <span>{job.company}</span>}
            {job.job_url && (
              <a href={job.job_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-primary hover:underline">
                Job posting <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>
        </div>

        {data && (
          <Card>
            <CardHeader>
              <CardTitle>Extracted requirements</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <SkillGroup label="Required skills" items={data.required_skills} variant="info" />
              <SkillGroup label="Preferred skills" items={data.preferred_skills} variant="default" />
              {data.min_experience_years !== null && (
                <p className="text-sm">
                  <span className="font-medium">Minimum experience:</span> {data.min_experience_years}+ years
                </p>
              )}
              <SkillGroup label="Education" items={data.education_requirements} variant="default" />
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Job description</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap text-sm text-muted-foreground">{job.description_raw}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Match against a resume</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {resumes.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No resumes uploaded yet.{" "}
                <Link href="/resumes" className="text-primary hover:underline">
                  Upload one
                </Link>{" "}
                to see your match score.
              </p>
            ) : (
              <div className="flex flex-col gap-3 sm:flex-row">
                <select
                  value={selectedResumeId}
                  onChange={(e) => setSelectedResumeId(e.target.value)}
                  className="h-10 flex-1 rounded-lg border border-border bg-card px-3 text-sm"
                >
                  <option value="">Select a resume...</option>
                  {resumes.map((resume) => (
                    <option key={resume.id} value={resume.id}>
                      {resume.title}
                    </option>
                  ))}
                </select>
                <Button onClick={handleMatch} loading={matching} disabled={!selectedResumeId}>
                  Run match
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {match && <MatchResultPanel match={match} />}
      </div>
    </AppShell>
  );
}

function SkillGroup({
  label,
  items,
  variant,
}: {
  label: string;
  items: string[];
  variant: "info" | "default";
}) {
  if (items.length === 0) return null;
  return (
    <div>
      <p className="mb-2 text-sm font-medium">{label}</p>
      <div className="flex flex-wrap gap-1.5">
        {items.map((item) => (
          <Badge key={item} variant={variant}>
            {item}
          </Badge>
        ))}
      </div>
    </div>
  );
}

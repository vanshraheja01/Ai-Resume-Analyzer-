"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PageSpinner, ErrorState, EmptyState } from "@/components/ui/states";
import { ResumeAnalysisPanel } from "@/components/resume/resume-analysis-panel";
import { MatchResultPanel } from "@/components/jobs/match-result-panel";
import { useRequireAuth } from "@/lib/auth";
import { resumesApi, jobsApi, matchingApi, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { ResumeDetail, ResumeAnalysis, Job, Match } from "@/types";

export function ResumeDetailClient({ id }: { id: string }) {
  const { user, loading: authLoading } = useRequireAuth();
  const [resume, setResume] = useState<ResumeDetail | null>(null);
  const [analyses, setAnalyses] = useState<ResumeAnalysis[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [match, setMatch] = useState<Match | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [matching, setMatching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    if (!user) return;
    Promise.all([resumesApi.get(id), resumesApi.analyses(id), jobsApi.list()])
      .then(([r, a, j]) => {
        setResume(r);
        setAnalyses(a);
        setJobs(j);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load resume"));
  }, [user, id]);

  async function handleAnalyze() {
    setAnalyzing(true);
    try {
      const analysis = await resumesApi.analyze(id);
      setAnalyses((prev) => [analysis, ...prev]);
      toast.success("Analysis complete.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Analysis failed.");
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleMatch() {
    if (!selectedJobId) return;
    setMatching(true);
    try {
      const result = await matchingApi.analyze(id, selectedJobId);
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
  if (!resume) return <PageSpinner />;

  const latestAnalysis = analyses[0];
  const parsed = resume.parsed_data;

  return (
    <AppShell>
      <div className="mx-auto max-w-4xl space-y-6">
        <Link href="/resumes" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back to resumes
        </Link>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold">{resume.title}</h1>
            <p className="mt-1 text-sm text-muted-foreground uppercase">{resume.file_type}</p>
          </div>
          <Button onClick={handleAnalyze} loading={analyzing}>
            <Sparkles className="h-4 w-4" />
            {latestAnalysis ? "Re-analyze" : "Analyze with AI"}
          </Button>
        </div>

        {parsed && (
          <Card>
            <CardHeader>
              <CardTitle>Parsed details</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <Field label="Name" value={parsed.name} />
              <Field label="Email" value={parsed.email} />
              <Field label="Phone" value={parsed.phone} />
              <Field label="Location" value={parsed.location} />
              <SkillsField label="Skills" items={parsed.skills} />
              <SkillsField label="Languages" items={parsed.languages} />
            </CardContent>
          </Card>
        )}

        {latestAnalysis ? (
          <ResumeAnalysisPanel analysis={latestAnalysis} />
        ) : (
          <EmptyState
            icon={<Sparkles className="h-8 w-8" />}
            title="No analysis yet"
            description="Click “Analyze with AI” to get a scored breakdown of this resume."
          />
        )}

        <Card>
          <CardHeader>
            <CardTitle>Match against a job</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {jobs.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No analyzed jobs yet.{" "}
                <Link href="/jobs" className="text-primary hover:underline">
                  Add one
                </Link>{" "}
                to see your match score.
              </p>
            ) : (
              <div className="flex flex-col gap-3 sm:flex-row">
                <select
                  value={selectedJobId}
                  onChange={(e) => setSelectedJobId(e.target.value)}
                  className="h-10 flex-1 rounded-lg border border-border bg-card px-3 text-sm"
                >
                  <option value="">Select a job...</option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title} {job.company ? `@ ${job.company}` : ""}
                    </option>
                  ))}
                </select>
                <Button onClick={handleMatch} loading={matching} disabled={!selectedJobId}>
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

function Field({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase text-muted-foreground">{label}</p>
      <p className="mt-0.5 text-sm">{value || "-"}</p>
    </div>
  );
}

function SkillsField({ label, items }: { label: string; items: string[] }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase text-muted-foreground">{label}</p>
      <div className="mt-1.5 flex flex-wrap gap-1.5">
        {items.length > 0 ? (
          items.map((item) => (
            <Badge key={item} variant="info">
              {item}
            </Badge>
          ))
        ) : (
          <span className="text-sm text-muted-foreground">-</span>
        )}
      </div>
    </div>
  );
}

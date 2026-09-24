"use client";

import { useEffect, useState } from "react";
import { Briefcase } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { JobForm } from "@/components/jobs/job-form";
import { JobCard } from "@/components/jobs/job-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState, ErrorState, PageSpinner, Skeleton } from "@/components/ui/states";
import { ConfirmDialog } from "@/components/ui/dialog";
import { useRequireAuth } from "@/lib/auth";
import { jobsApi, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { Job } from "@/types";

export default function JobsPage() {
  const { user, loading: authLoading } = useRequireAuth();
  const [jobs, setJobs] = useState<Job[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Job | null>(null);
  const [deleting, setDeleting] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (!user) return;
    jobsApi
      .list()
      .then(setJobs)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load jobs"));
  }, [user]);

  async function handleDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await jobsApi.remove(deleteTarget.id);
      setJobs((prev) => prev?.filter((j) => j.id !== deleteTarget.id) ?? null);
      toast.success("Job deleted.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to delete job.");
    } finally {
      setDeleting(false);
      setDeleteTarget(null);
    }
  }

  if (authLoading || !user) return <PageSpinner />;

  return (
    <AppShell>
      <div className="mx-auto max-w-4xl space-y-8">
        <div>
          <h1 className="text-2xl font-semibold">Jobs</h1>
          <p className="mt-1 text-muted-foreground">
            Paste a job description to extract required skills and match it against your resumes.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Analyze a job description</CardTitle>
          </CardHeader>
          <CardContent>
            <JobForm onAnalyzed={(job) => setJobs((prev) => [job, ...(prev ?? [])])} />
          </CardContent>
        </Card>

        {error && <ErrorState message={error} />}

        {jobs === null && !error && (
          <div className="grid gap-3 sm:grid-cols-2">
            {[0, 1].map((i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
        )}

        {jobs && jobs.length === 0 && (
          <EmptyState
            icon={<Briefcase className="h-8 w-8" />}
            title="No jobs analyzed yet"
            description="Paste a job description above to see required skills and later match it against a resume."
          />
        )}

        {jobs && jobs.length > 0 && (
          <div className="grid gap-3 sm:grid-cols-2">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} onDelete={() => setDeleteTarget(job)} />
            ))}
          </div>
        )}
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete job?"
        description={`"${deleteTarget?.title}" will be permanently deleted, including any match history.`}
        confirmLabel="Delete"
        danger
        loading={deleting}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </AppShell>
  );
}

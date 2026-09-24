"use client";

import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { ResumeUploadForm } from "@/components/resume/resume-upload-form";
import { ResumeCard } from "@/components/resume/resume-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState, ErrorState, PageSpinner, Skeleton } from "@/components/ui/states";
import { ConfirmDialog } from "@/components/ui/dialog";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { useRequireAuth } from "@/lib/auth";
import { resumesApi, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { ResumeSummary } from "@/types";

export default function ResumesPage() {
  const { user, loading: authLoading } = useRequireAuth();
  const [resumes, setResumes] = useState<ResumeSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<ResumeSummary | null>(null);
  const [deleting, setDeleting] = useState(false);
  const toast = useToast();

  function load() {
    resumesApi
      .list()
      .then(setResumes)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load resumes"));
  }

  useEffect(() => {
    if (user) load();
  }, [user]);

  async function handleDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await resumesApi.remove(deleteTarget.id);
      setResumes((prev) => prev?.filter((r) => r.id !== deleteTarget.id) ?? null);
      toast.success("Resume deleted.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to delete resume.");
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
          <h1 className="text-2xl font-semibold">Resumes</h1>
          <p className="mt-1 text-muted-foreground">Upload multiple versions and pick one to analyze or match.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Upload a new resume</CardTitle>
          </CardHeader>
          <CardContent>
            <ResumeUploadForm onUploaded={(resume) => setResumes((prev) => [resume, ...(prev ?? [])])} />
          </CardContent>
        </Card>

        {error && <ErrorState message={error} />}

        {resumes === null && !error && (
          <div className="grid gap-3 sm:grid-cols-2">
            {[0, 1].map((i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
        )}

        {resumes && resumes.length === 0 && (
          <EmptyState
            icon={<FileText className="h-8 w-8" />}
            title="No resumes yet"
            description="Upload your first resume above to get an AI-generated score and recommendations."
          />
        )}

        {resumes && resumes.length > 0 && (
          <div className="grid gap-3 sm:grid-cols-2">
            {resumes.map((resume, i) => (
              <ScrollReveal key={resume.id} index={i}>
                <ResumeCard resume={resume} onDelete={() => setDeleteTarget(resume)} />
              </ScrollReveal>
            ))}
          </div>
        )}
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete resume?"
        description={`"${deleteTarget?.title}" will be permanently deleted, including its analysis history.`}
        confirmLabel="Delete"
        danger
        loading={deleting}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </AppShell>
  );
}

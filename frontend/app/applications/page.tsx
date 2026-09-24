"use client";

import { useEffect, useState } from "react";
import { ClipboardList, Plus } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { ApplicationCard } from "@/components/applications/application-card";
import { ApplicationForm } from "@/components/applications/application-form";
import { Button } from "@/components/ui/button";
import { EmptyState, ErrorState, PageSpinner, Skeleton } from "@/components/ui/states";
import { Modal, ConfirmDialog } from "@/components/ui/dialog";
import { useRequireAuth } from "@/lib/auth";
import { applicationsApi, ApiError, type ApplicationInput } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import { APPLICATION_STATUS_LABELS, APPLICATION_STATUSES } from "@/lib/utils";
import type { Application, ApplicationStatus } from "@/types";

export default function ApplicationsPage() {
  const { user, loading: authLoading } = useRequireAuth();
  const [applications, setApplications] = useState<Application[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Application | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Application | null>(null);
  const [deleting, setDeleting] = useState(false);
  const toast = useToast();

  function load() {
    applicationsApi
      .list()
      .then(setApplications)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load applications"));
  }

  useEffect(() => {
    if (user) load();
  }, [user]);

  async function handleCreate(data: ApplicationInput) {
    try {
      const app = await applicationsApi.create(data);
      setApplications((prev) => [app, ...(prev ?? [])]);
      toast.success("Application added.");
      setFormOpen(false);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to add application.");
    }
  }

  async function handleUpdate(data: ApplicationInput) {
    if (!editing) return;
    try {
      const updated = await applicationsApi.update(editing.id, data);
      setApplications((prev) => prev?.map((a) => (a.id === updated.id ? updated : a)) ?? null);
      toast.success("Application updated.");
      setEditing(null);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to update application.");
    }
  }

  async function handleStatusChange(app: Application, status: ApplicationStatus) {
    try {
      const updated = await applicationsApi.update(app.id, { status });
      setApplications((prev) => prev?.map((a) => (a.id === updated.id ? updated : a)) ?? null);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to update status.");
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await applicationsApi.remove(deleteTarget.id);
      setApplications((prev) => prev?.filter((a) => a.id !== deleteTarget.id) ?? null);
      toast.success("Application deleted.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to delete application.");
    } finally {
      setDeleting(false);
      setDeleteTarget(null);
    }
  }

  if (authLoading || !user) return <PageSpinner />;

  const grouped = APPLICATION_STATUSES.map((status) => ({
    status,
    items: (applications ?? []).filter((a) => a.status === status),
  })).filter((g) => g.items.length > 0 || applications === null);

  return (
    <AppShell>
      <div className="mx-auto max-w-6xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold">Applications</h1>
            <p className="mt-1 text-muted-foreground">Track every application from saved to offer.</p>
          </div>
          <Button onClick={() => setFormOpen(true)}>
            <Plus className="h-4 w-4" /> Add application
          </Button>
        </div>

        {error && <ErrorState message={error} />}

        {applications === null && !error && (
          <div className="grid gap-3 sm:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        )}

        {applications && applications.length === 0 && (
          <EmptyState
            icon={<ClipboardList className="h-8 w-8" />}
            title="No applications tracked yet"
            description="Add your first application to start tracking its progress."
            action={
              <Button size="sm" onClick={() => setFormOpen(true)}>
                Add application
              </Button>
            }
          />
        )}

        {applications && applications.length > 0 && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {grouped.map((group) => (
              <div key={group.status} className="space-y-3">
                <h2 className="text-sm font-semibold text-muted-foreground">
                  {APPLICATION_STATUS_LABELS[group.status]} ({group.items.length})
                </h2>
                <div className="space-y-3">
                  {group.items.map((app) => (
                    <ApplicationCard
                      key={app.id}
                      application={app}
                      onStatusChange={(status) => handleStatusChange(app, status)}
                      onEdit={() => setEditing(app)}
                      onDelete={() => setDeleteTarget(app)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal open={formOpen} title="Add application" onClose={() => setFormOpen(false)}>
        <ApplicationForm onSubmit={handleCreate} submitLabel="Add application" />
      </Modal>

      <Modal open={!!editing} title="Edit application" onClose={() => setEditing(null)}>
        {editing && <ApplicationForm initial={editing} onSubmit={handleUpdate} submitLabel="Save changes" />}
      </Modal>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete application?"
        description={`The application for "${deleteTarget?.position_title}" at ${deleteTarget?.company} will be permanently deleted.`}
        confirmLabel="Delete"
        danger
        loading={deleting}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </AppShell>
  );
}

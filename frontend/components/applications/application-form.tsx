"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input, Label, Textarea } from "@/components/ui/input";
import { APPLICATION_STATUS_LABELS, APPLICATION_STATUSES } from "@/lib/utils";
import type { Application, ApplicationStatus } from "@/types";
import type { ApplicationInput } from "@/lib/api";

export function ApplicationForm({
  initial,
  onSubmit,
  submitLabel = "Save",
}: {
  initial?: Application;
  onSubmit: (data: ApplicationInput) => Promise<void>;
  submitLabel?: string;
}) {
  const [company, setCompany] = useState(initial?.company ?? "");
  const [positionTitle, setPositionTitle] = useState(initial?.position_title ?? "");
  const [status, setStatus] = useState<ApplicationStatus>(initial?.status ?? "saved");
  const [jobUrl, setJobUrl] = useState(initial?.job_url ?? "");
  const [applicationDate, setApplicationDate] = useState(initial?.application_date ?? "");
  const [interviewDate, setInterviewDate] = useState(initial?.interview_date ?? "");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit({
        company,
        position_title: positionTitle,
        status,
        job_url: jobUrl || null,
        application_date: applicationDate || null,
        interview_date: interviewDate || null,
        notes: notes || null,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <Label htmlFor="app-company">Company</Label>
          <Input id="app-company" required value={company} onChange={(e) => setCompany(e.target.value)} />
        </div>
        <div>
          <Label htmlFor="app-position">Position</Label>
          <Input
            id="app-position"
            required
            value={positionTitle}
            onChange={(e) => setPositionTitle(e.target.value)}
          />
        </div>
      </div>

      <div>
        <Label htmlFor="app-status">Status</Label>
        <select
          id="app-status"
          value={status}
          onChange={(e) => setStatus(e.target.value as ApplicationStatus)}
          className="h-10 w-full rounded-lg border border-border bg-card px-3 text-sm"
        >
          {APPLICATION_STATUSES.map((s) => (
            <option key={s} value={s}>
              {APPLICATION_STATUS_LABELS[s]}
            </option>
          ))}
        </select>
      </div>

      <div>
        <Label htmlFor="app-url">Job URL</Label>
        <Input id="app-url" type="url" value={jobUrl} onChange={(e) => setJobUrl(e.target.value)} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <Label htmlFor="app-date">Application date</Label>
          <Input
            id="app-date"
            type="date"
            value={applicationDate}
            onChange={(e) => setApplicationDate(e.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="interview-date">Interview date</Label>
          <Input
            id="interview-date"
            type="date"
            value={interviewDate}
            onChange={(e) => setInterviewDate(e.target.value)}
          />
        </div>
      </div>

      <div>
        <Label htmlFor="app-notes">Notes</Label>
        <Textarea id="app-notes" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
      </div>

      <Button type="submit" className="w-full" loading={loading}>
        {submitLabel}
      </Button>
    </form>
  );
}

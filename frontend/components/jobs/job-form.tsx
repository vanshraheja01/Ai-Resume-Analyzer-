"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input, Label, Textarea } from "@/components/ui/input";
import { jobsApi, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { Job } from "@/types";

export function JobForm({ onAnalyzed }: { onAnalyzed: (job: Job) => void }) {
  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [jobUrl, setJobUrl] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const job = await jobsApi.analyze({
        title,
        company: company || undefined,
        description_raw: description,
        job_url: jobUrl || undefined,
      });
      toast.success("Job description analyzed.");
      setTitle("");
      setCompany("");
      setJobUrl("");
      setDescription("");
      onAnalyzed(job);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to analyze job description.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <Label htmlFor="job-title">Job title</Label>
          <Input id="job-title" required value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div>
          <Label htmlFor="job-company">Company</Label>
          <Input id="job-company" value={company} onChange={(e) => setCompany(e.target.value)} />
        </div>
      </div>
      <div>
        <Label htmlFor="job-url">Job URL (optional)</Label>
        <Input id="job-url" type="url" value={jobUrl} onChange={(e) => setJobUrl(e.target.value)} />
      </div>
      <div>
        <Label htmlFor="job-description">Job description</Label>
        <Textarea
          id="job-description"
          required
          minLength={20}
          rows={8}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Paste the full job description here..."
        />
      </div>
      <Button type="submit" loading={loading}>
        Analyze with AI
      </Button>
    </form>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FileText, Briefcase, ClipboardList, Award, Clock, Upload, Target } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { StatCard } from "@/components/dashboard/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageSpinner, ErrorState } from "@/components/ui/states";
import { ScrollReveal } from "@/components/ui/scroll-reveal";
import { useRequireAuth } from "@/lib/auth";
import { dashboardApi, ApiError } from "@/lib/api";
import type { DashboardStats } from "@/types";

export default function DashboardPage() {
  const { user, loading: authLoading } = useRequireAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    dashboardApi
      .get()
      .then(setStats)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load dashboard"));
  }, [user]);

  if (authLoading || !user) return <PageSpinner />;

  return (
    <AppShell>
      <div className="mx-auto max-w-6xl space-y-8">
        <div>
          <h1 className="text-2xl font-semibold">Welcome back{user.full_name ? `, ${user.full_name}` : ""}</h1>
          <p className="mt-1 text-muted-foreground">Here&apos;s where your job search stands.</p>
        </div>

        {error && <ErrorState message={error} />}

        {!stats && !error && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[0, 1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="h-20" />
              </Card>
            ))}
          </div>
        )}

        {stats && (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <ScrollReveal index={0}>
              <StatCard label="Applications" value={stats.total_applications} icon={ClipboardList} />
            </ScrollReveal>
            <ScrollReveal index={1}>
              <StatCard label="Interviews" value={stats.interviews} icon={Clock} />
            </ScrollReveal>
            <ScrollReveal index={2}>
              <StatCard label="Offers" value={stats.offers} icon={Award} />
            </ScrollReveal>
            <ScrollReveal index={3}>
              <StatCard label="Pending" value={stats.pending} icon={Briefcase} />
            </ScrollReveal>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-3">
          <ScrollReveal index={0}>
            <Card className="h-full transition-[transform,box-shadow] duration-300 hover:-translate-y-1 hover:shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-4 w-4 text-primary" /> Upload a resume
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Get an AI-generated score and improvement recommendations.
                </p>
                <Link href="/resumes">
                  <Button size="sm" className="mt-4">
                    Go to resumes
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </ScrollReveal>

          <ScrollReveal index={1}>
            <Card className="h-full transition-[transform,box-shadow] duration-300 hover:-translate-y-1 hover:shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-primary" /> Match a job
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Paste a job description to see your match score and skill gaps.
                </p>
                <Link href="/jobs">
                  <Button size="sm" className="mt-4">
                    Analyze a job
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </ScrollReveal>

          <ScrollReveal index={2}>
            <Card className="h-full transition-[transform,box-shadow] duration-300 hover:-translate-y-1 hover:shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-primary" /> Your library
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {stats ? `${stats.total_resumes} resume(s), ${stats.total_jobs_analyzed} job(s) analyzed.` : "-"}
                </p>
                <Link href="/applications">
                  <Button size="sm" variant="outline" className="mt-4">
                    View applications
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </ScrollReveal>
        </div>
      </div>
    </AppShell>
  );
}

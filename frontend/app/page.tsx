import Link from "next/link";
import { ArrowRight, FileSearch, Target, ClipboardCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollReveal } from "@/components/ui/scroll-reveal";

const FEATURES = [
  {
    icon: FileSearch,
    title: "AI Resume Analysis",
    description:
      "Upload a PDF or DOCX resume and get scored on skills, experience, projects, structure, and more.",
  },
  {
    icon: Target,
    title: "Job Match Scoring",
    description: "Paste a job description and see exactly which skills match, which are missing, and why.",
  },
  {
    icon: ClipboardCheck,
    title: "Application Tracking",
    description: "Track every application from saved to offer, with notes, dates, and status at a glance.",
  },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-border">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <div className="flex items-center gap-2 font-semibold">
            <Sparkles className="h-5 w-5 text-primary" />
            AI Resume Analyzer
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">
                Log in
              </Button>
            </Link>
            <Link href="/register">
              <Button size="sm">Sign up</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <section className="relative overflow-hidden">
          <div
            className="hero-glow -left-24 -top-24 h-96 w-96 bg-primary"
            aria-hidden
          />
          <div
            className="hero-glow -right-32 top-10 h-80 w-80 bg-emerald-400"
            style={{ animationDelay: "-6s" }}
            aria-hidden
          />
          <div className="relative mx-auto max-w-4xl px-4 py-24 text-center">
            <ScrollReveal index={0}>
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
                Know exactly what your resume is missing
              </h1>
            </ScrollReveal>
            <ScrollReveal index={1}>
              <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">
                AI-powered resume scoring, job-match analysis, and application tracking in one place — built
                to give you a clear, honest read on where you stand.
              </p>
            </ScrollReveal>
            <ScrollReveal index={2}>
              <div className="mt-8 flex justify-center gap-3">
                <Link href="/register">
                  <Button size="lg">
                    Get started free
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/login">
                  <Button size="lg" variant="outline">
                    Log in
                  </Button>
                </Link>
              </div>
            </ScrollReveal>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-24">
          <div className="grid gap-6 sm:grid-cols-3">
            {FEATURES.map((feature, i) => (
              <ScrollReveal key={feature.title} index={i}>
                <Card className="h-full transition-[transform,box-shadow] duration-300 hover:-translate-y-1 hover:shadow-lg">
                  <CardContent>
                    <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <feature.icon className="h-5 w-5" />
                    </div>
                    <h3 className="font-semibold">{feature.title}</h3>
                    <p className="mt-2 text-sm text-muted-foreground">{feature.description}</p>
                  </CardContent>
                </Card>
              </ScrollReveal>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-border py-6 text-center text-sm text-muted-foreground">
        AI-generated analysis — not a guaranteed hiring outcome.
      </footer>
    </div>
  );
}

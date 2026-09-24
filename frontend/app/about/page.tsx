import Link from "next/link";
import Image from "next/image";
import { ArrowLeft, GraduationCap, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollReveal } from "@/components/ui/scroll-reveal";

const INTERESTS = [
  "Full Stack Development",
  "Frontend",
  "Backend",
  "AI",
  "APIs",
  "DSA",
  "Problem Solving",
  "Creative Technology",
];

const SKILLS = ["React.js", "JavaScript", "Node.js", "Python", "REST APIs", "HTML", "CSS", "Git", "GitHub"];

export default function AboutPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-border">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <Sparkles className="h-5 w-5 text-primary" />
            AI Resume Analyzer
          </Link>
          <Link
            href="/"
            className="press-feedback inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back home
          </Link>
        </div>
      </header>

      <main className="relative flex-1">
        <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
          <div className="hero-glow -left-24 top-0 h-96 w-96 bg-primary" />
          <div
            className="hero-glow -right-32 top-40 h-80 w-80 bg-emerald-400"
            style={{ animationDelay: "-8s" }}
          />
        </div>

        <div className="relative mx-auto grid max-w-6xl gap-12 px-4 py-20 lg:grid-cols-[1.15fr_0.85fr] lg:items-start">
          <div>
            <ScrollReveal index={0}>
              <p className="text-sm font-semibold uppercase tracking-widest text-primary">About Me</p>
            </ScrollReveal>

            <ScrollReveal index={1}>
              <h1 className="mt-3 bg-gradient-to-br from-foreground to-foreground/60 bg-clip-text text-5xl font-extrabold tracking-tight text-transparent sm:text-6xl">
                Vansh Raheja
              </h1>
            </ScrollReveal>

            <ScrollReveal index={2}>
              <p className="mt-6 text-lg leading-relaxed text-muted-foreground">
                I&apos;m a B.Tech Computer Science &amp; Engineering student at GGSIPU, with a strong interest
                in building modern, practical, and user-focused digital experiences.
              </p>
            </ScrollReveal>

            <ScrollReveal index={3}>
              <h2 className="mt-8 text-2xl font-serif italic text-primary">My interests</h2>
              <p className="mt-3 leading-relaxed text-muted-foreground">
                span Full Stack Development, Frontend Development, Backend Development, AI, APIs, Data
                Structures &amp; Algorithms, and creative problem-solving. I enjoy exploring new technologies,
                understanding how systems work, and turning ideas into applications that are useful in the
                real world.
              </p>
            </ScrollReveal>

            <ScrollReveal index={4}>
              <p className="mt-4 leading-relaxed text-muted-foreground">
                I work with technologies including React.js, JavaScript, Node.js, Python, REST APIs, HTML,
                CSS, Git, and GitHub, with a foundation in Object-Oriented Programming, Data Structures &amp;
                Algorithms, and client-server architecture.
              </p>
            </ScrollReveal>

            <ScrollReveal index={5}>
              <p className="mt-4 leading-relaxed text-muted-foreground">
                I believe development is a continuous journey of learning, experimenting, building, and
                improving — and I&apos;m always looking for the next idea to turn into something meaningful.
              </p>
            </ScrollReveal>

            <ScrollReveal index={6}>
              <p className="mt-8 font-serif text-xl italic text-primary">
                Learning. Building. Creating. Evolving.
              </p>
            </ScrollReveal>

            <ScrollReveal index={7}>
              <div className="mt-10 flex items-start gap-3 rounded-xl border border-border bg-card p-4">
                <GraduationCap className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                <div>
                  <p className="font-semibold">B.Tech — Computer Science &amp; Engineering</p>
                  <p className="text-sm text-muted-foreground">GGSIPU (Guru Gobind Singh Indraprastha University)</p>
                </div>
              </div>
            </ScrollReveal>

            <ScrollReveal index={8}>
              <div className="mt-8">
                <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                  Interests
                </p>
                <div className="flex flex-wrap gap-2">
                  {INTERESTS.map((interest) => (
                    <Badge key={interest} variant="info">
                      {interest}
                    </Badge>
                  ))}
                </div>
              </div>
            </ScrollReveal>

            <ScrollReveal index={9}>
              <div className="mt-6">
                <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                  Skills
                </p>
                <div className="flex flex-wrap gap-2">
                  {SKILLS.map((skill) => (
                    <Badge key={skill} variant="default">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            </ScrollReveal>
          </div>

          <ScrollReveal index={2} className="lg:sticky lg:top-20">
            <div className="overflow-hidden rounded-2xl border border-border shadow-lg">
              <div className="relative aspect-[3/4] w-full">
                <Image
                  src="/vansh-raheja.jpg"
                  alt="Vansh Raheja"
                  fill
                  sizes="(min-width: 1024px) 380px, 100vw"
                  className="object-cover"
                  style={{ objectPosition: "50% 18%" }}
                  priority
                />
              </div>
              <div className="bg-foreground px-5 py-4 text-background">
                <p className="font-serif text-lg italic">Vansh Raheja</p>
                <p className="text-sm opacity-70">B.Tech CSE Student, GGSIPU</p>
              </div>
            </div>
            <p className="mt-4 text-center font-serif italic text-primary">
              Learning. Building. Creating. Evolving.
            </p>
          </ScrollReveal>
        </div>
      </main>
    </div>
  );
}

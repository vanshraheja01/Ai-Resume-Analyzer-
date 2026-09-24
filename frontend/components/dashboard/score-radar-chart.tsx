"use client";

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import type { ResumeAnalysis } from "@/types";

export function ScoreRadarChart({ analysis }: { analysis: ResumeAnalysis }) {
  const data = [
    { category: "Skills", score: analysis.skills_score },
    { category: "Experience", score: analysis.experience_score },
    { category: "Projects", score: analysis.projects_score },
    { category: "Education", score: analysis.education_score },
    { category: "Structure", score: analysis.structure_score },
    { category: "Achievements", score: analysis.achievements_score },
    { category: "Keywords", score: analysis.keywords_score },
    { category: "Relevance", score: analysis.job_relevance_score },
  ];

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} outerRadius="75%">
          <PolarGrid stroke="var(--border)" />
          <PolarAngleAxis dataKey="category" tick={{ fill: "var(--muted-foreground)", fontSize: 11 }} />
          <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
          <Radar dataKey="score" stroke="var(--primary)" fill="var(--primary)" fillOpacity={0.25} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

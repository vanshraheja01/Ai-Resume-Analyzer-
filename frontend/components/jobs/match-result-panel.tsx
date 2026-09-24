import { Check, X, CircleDashed } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Match } from "@/types";

export function MatchResultPanel({ match }: { match: Match }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Match score</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold text-primary">{match.match_score}%</span>
          <span className="text-sm text-muted-foreground">estimated fit</span>
        </div>

        <p className="text-xs text-muted-foreground">
          AI-generated analysis, not a guaranteed hiring outcome — use it to guide what to strengthen.
        </p>

        <SkillList
          icon={<Check className="h-3.5 w-3.5" />}
          label="Matched skills"
          skills={match.matched_skills}
          className="text-emerald-700 dark:text-emerald-400"
        />
        <SkillList
          icon={<CircleDashed className="h-3.5 w-3.5" />}
          label="Partial match"
          skills={match.partial_skills}
          className="text-amber-700 dark:text-amber-400"
        />
        <SkillList
          icon={<X className="h-3.5 w-3.5" />}
          label="Missing skills"
          skills={match.missing_skills}
          className="text-red-700 dark:text-red-400"
        />

        {match.recommendations && match.recommendations.length > 0 && (
          <div>
            <p className="mb-2 text-sm font-medium">Recommendations</p>
            <ul className="space-y-1.5 text-sm text-muted-foreground">
              {match.recommendations.map((rec, i) => (
                <li key={i} className="flex gap-2">
                  <span className="text-primary">•</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function SkillList({
  icon,
  label,
  skills,
  className,
}: {
  icon: React.ReactNode;
  label: string;
  skills: string[] | null;
  className: string;
}) {
  if (!skills || skills.length === 0) return null;
  return (
    <div>
      <p className="mb-2 text-sm font-medium">{label}</p>
      <div className="flex flex-wrap gap-2">
        {skills.map((skill) => (
          <span
            key={skill}
            className={`inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-1 text-xs font-medium ${className}`}
          >
            {icon}
            {skill}
          </span>
        ))}
      </div>
    </div>
  );
}

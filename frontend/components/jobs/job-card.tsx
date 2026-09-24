import Link from "next/link";
import { Briefcase, Trash2 } from "lucide-react";
import { InteractiveCard, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import type { Job } from "@/types";

export function JobCard({ job, onDelete }: { job: Job; onDelete: () => void }) {
  const skillCount = job.extracted_data?.required_skills.length ?? 0;
  return (
    <InteractiveCard className="group">
      <CardContent className="flex items-start justify-between gap-3">
        <Link href={`/jobs/${job.id}`} className="flex flex-1 items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary transition-transform duration-300 group-hover:scale-110">
            <Briefcase className="h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate font-medium">{job.title}</p>
            {job.company && <p className="text-sm text-muted-foreground">{job.company}</p>}
            <p className="mt-1 text-xs text-muted-foreground">Added {formatDate(job.created_at)}</p>
            {skillCount > 0 && (
              <Badge variant="info" className="mt-2">
                {skillCount} required skills
              </Badge>
            )}
          </div>
        </Link>
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onDelete();
          }}
          className="press-feedback shrink-0 rounded-lg p-2 text-muted-foreground transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950"
          aria-label="Delete job"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </CardContent>
    </InteractiveCard>
  );
}

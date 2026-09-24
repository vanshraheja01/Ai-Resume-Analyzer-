import Link from "next/link";
import { FileText, Trash2 } from "lucide-react";
import { InteractiveCard, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import type { ResumeSummary } from "@/types";

export function ResumeCard({ resume, onDelete }: { resume: ResumeSummary; onDelete: () => void }) {
  return (
    <InteractiveCard className="group">
      <CardContent className="flex items-start justify-between gap-3">
        <Link href={`/resumes/${resume.id}`} className="flex flex-1 items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary transition-transform duration-300 group-hover:scale-110">
            <FileText className="h-5 w-5" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate font-medium">{resume.title}</p>
            <p className="mt-1 text-xs text-muted-foreground">Updated {formatDate(resume.updated_at)}</p>
            <Badge variant="default" className="mt-2 uppercase">
              {resume.file_type}
            </Badge>
          </div>
        </Link>
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onDelete();
          }}
          className="press-feedback shrink-0 rounded-lg p-2 text-muted-foreground transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950"
          aria-label="Delete resume"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </CardContent>
    </InteractiveCard>
  );
}

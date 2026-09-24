import { Calendar, ExternalLink, Pencil, Trash2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge, APPLICATION_STATUS_VARIANT } from "@/components/ui/badge";
import { APPLICATION_STATUS_LABELS, APPLICATION_STATUSES, formatDate } from "@/lib/utils";
import type { Application, ApplicationStatus } from "@/types";

export function ApplicationCard({
  application,
  onStatusChange,
  onEdit,
  onDelete,
}: {
  application: Application;
  onStatusChange: (status: ApplicationStatus) => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <Card className="hover:shadow-md">
      <CardContent className="space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate font-medium">{application.position_title}</p>
            <p className="truncate text-sm text-muted-foreground">{application.company}</p>
          </div>
          <div className="flex shrink-0 gap-1">
            <button
              onClick={onEdit}
              className="press-feedback rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted"
              aria-label="Edit"
            >
              <Pencil className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={onDelete}
              className="press-feedback rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950"
              aria-label="Delete"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <select
          value={application.status}
          onChange={(e) => onStatusChange(e.target.value as ApplicationStatus)}
          className="h-8 w-full rounded-lg border border-border bg-card px-2 text-xs"
        >
          {APPLICATION_STATUSES.map((s) => (
            <option key={s} value={s}>
              {APPLICATION_STATUS_LABELS[s]}
            </option>
          ))}
        </select>

        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          <Badge variant={APPLICATION_STATUS_VARIANT[application.status]}>
            {APPLICATION_STATUS_LABELS[application.status]}
          </Badge>
          {application.application_date && (
            <span className="flex items-center gap-1">
              <Calendar className="h-3 w-3" /> {formatDate(application.application_date)}
            </span>
          )}
          {application.job_url && (
            <a href={application.job_url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-primary hover:underline">
              <ExternalLink className="h-3 w-3" /> Posting
            </a>
          )}
        </div>

        {application.notes && <p className="line-clamp-2 text-xs text-muted-foreground">{application.notes}</p>}
      </CardContent>
    </Card>
  );
}

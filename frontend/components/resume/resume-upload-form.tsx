"use client";

import { useRef, useState, type DragEvent } from "react";
import { Upload, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { resumesApi, ApiError } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import type { ResumeDetail } from "@/types";

export function ResumeUploadForm({ onUploaded }: { onUploaded: (resume: ResumeDetail) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const toast = useToast();

  function pickFile(f: File | null) {
    if (!f) return;
    const ext = f.name.toLowerCase().split(".").pop();
    if (ext !== "pdf" && ext !== "docx") {
      toast.error("Only PDF and DOCX files are supported.");
      return;
    }
    if (f.size > 5 * 1024 * 1024) {
      toast.error("File exceeds the 5MB upload limit.");
      return;
    }
    setFile(f);
    if (!title) setTitle(f.name.replace(/\.(pdf|docx)$/i, ""));
  }

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    try {
      const resume = await resumesApi.upload(file, title || undefined);
      toast.success("Resume uploaded and parsed successfully.");
      setFile(null);
      setTitle("");
      onUploaded(resume);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragOver(false);
    pickFile(e.dataTransfer.files?.[0] ?? null);
  }

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed p-8 text-center transition-colors",
          dragOver ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
        />
        {file ? (
          <>
            <FileText className="h-8 w-8 text-primary" />
            <p className="font-medium">{file.name}</p>
            <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(0)} KB</p>
          </>
        ) : (
          <>
            <Upload className="h-8 w-8 text-muted-foreground" />
            <p className="font-medium">Drag & drop your resume, or click to browse</p>
            <p className="text-xs text-muted-foreground">PDF or DOCX, up to 5MB</p>
          </>
        )}
      </div>

      {file && (
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <Label htmlFor="resume-title">Resume title</Label>
            <Input
              id="resume-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Software Engineer Resume"
            />
          </div>
          <Button onClick={handleUpload} loading={uploading}>
            Upload &amp; parse
          </Button>
        </div>
      )}
    </div>
  );
}

"use client";

import { useState, useCallback } from "react";
import { uploadTranscript, summarizeTranscript } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const MAX_FILE_SIZE = 15 * 1024 * 1024; // 15MB

export function UploadDropzone({ onJobStarted }: { onJobStarted: (jobId: string, transcript: any) => void }) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFile = async (file: File) => {
    setError(null);
    if (file.size > MAX_FILE_SIZE) {
      setError("File exceeds 15MB limit.");
      return;
    }

    setIsUploading(true);
    try {
      // 1. Upload
      const transcript = await uploadTranscript(file);
      // 2. Start Job
      const jobResp = await summarizeTranscript(transcript.id);
      
      onJobStarted(jobResp.job_id, transcript);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setIsUploading(false);
    }
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  return (
    <Card className="w-full max-w-2xl mx-auto mt-8">
      <CardContent>
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={onDrop}
          className={`mt-6 border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
            isDragging ? "border-primary bg-primary/10" : "border-muted-foreground/25"
          }`}
          onClick={() => document.getElementById("file-upload")?.click()}
        >
          {isUploading ? (
            <div className="animate-pulse font-semibold">Uploading and Processing...</div>
          ) : (
            <div className="text-muted-foreground">
              <p className="font-semibold text-lg text-foreground mb-2">Drag and drop your transcript here</p>
              <p>Supports .txt, .srt, .vtt (Max 15MB)</p>
            </div>
          )}
          <input
            id="file-upload"
            type="file"
            className="hidden"
            accept=".txt,.srt,.vtt"
            onChange={(e) => {
              if (e.target.files?.[0]) handleFile(e.target.files[0]);
            }}
          />
        </div>
        {error && <p className="text-destructive text-center mt-4 font-medium">{error}</p>}
      </CardContent>
    </Card>
  );
}

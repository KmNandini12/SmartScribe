"use client";

import { useState } from "react";
import { UploadDropzone } from "@/components/UploadDropzone";
import { JobStatusBadge } from "@/components/JobStatusBadge";
import { SplitPaneInspector } from "@/components/SplitPaneInspector";

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<any>(null);
  const [isCompleted, setIsCompleted] = useState(false);

  const handleJobStarted = (id: string, transcriptData: any) => {
    setJobId(id);
    setTranscript(transcriptData);
    setIsCompleted(false);
  };

  const handleJobCompleted = (job: any) => {
    setIsCompleted(true);
  };

  return (
    <main className="min-h-screen bg-slate-50 p-8 md:p-24 font-sans text-slate-900">
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none mix-blend-overlay"></div>
      <div className="max-w-6xl mx-auto space-y-8 relative z-10">
        
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
            SmartScribe
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Zero-Hallucination Extractive Auditability.
            Upload your transcript to extract deterministic, verifiable takeaways.
          </p>
        </div>

        {!jobId && (
          <UploadDropzone onJobStarted={handleJobStarted} />
        )}

        {jobId && (
          <div className="flex flex-col items-center mt-12 space-y-4">
            <h2 className="text-2xl font-bold">Processing Document</h2>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground text-sm font-medium">Job ID: {jobId}</span>
              <JobStatusBadge jobId={jobId} onCompleted={handleJobCompleted} />
            </div>
            
            {isCompleted && transcript && (
              <div className="w-full mt-12">
                <SplitPaneInspector transcript={transcript} jobId={jobId} />
              </div>
            )}
          </div>
        )}
        
      </div>
    </main>
  );
}

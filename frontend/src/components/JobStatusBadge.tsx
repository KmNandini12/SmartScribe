"use client";

import { useEffect, useState } from "react";
import { getJobStatus } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

export function JobStatusBadge({ jobId, onCompleted }: { jobId: string, onCompleted: (job: any) => void }) {
  const [status, setStatus] = useState<string>("PENDING");

  useEffect(() => {
    if (!jobId) return;

    let intervalId: NodeJS.Timeout;

    const poll = async () => {
      try {
        const job = await getJobStatus(jobId);
        setStatus(job.status);
        if (job.status === "COMPLETED" || job.status.startsWith("FAILED")) {
          clearInterval(intervalId);
          if (job.status === "COMPLETED") {
            onCompleted(job);
          }
        }
      } catch (err) {
        console.error("Polling error", err);
      }
    };

    poll(); // Initial check
    intervalId = setInterval(poll, 2000); // Poll every 2s

    return () => clearInterval(intervalId);
  }, [jobId, onCompleted]);

  let colorClass = "bg-yellow-500 hover:bg-yellow-600";
  if (status === "PROCESSING") colorClass = "bg-blue-500 hover:bg-blue-600 animate-pulse";
  if (status === "COMPLETED") colorClass = "bg-green-500 hover:bg-green-600";
  if (status.startsWith("FAILED")) colorClass = "bg-red-500 hover:bg-red-600";

  return (
    <Badge className={`${colorClass} text-white px-4 py-1 text-sm rounded-full transition-all`}>
      {status}
    </Badge>
  );
}

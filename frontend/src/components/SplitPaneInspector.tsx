"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { API_BASE_URL } from "@/lib/api";

export function SplitPaneInspector({ transcript, jobId }: { transcript: any, jobId: string }) {
  const [summary, setSummary] = useState<any>(null);
  const [highlightedText, setHighlightedText] = useState<string | null>(null);
  
  // Ref for transcript sentences container to handle scrolling
  const sentenceRefs = useRef<{[key: string]: HTMLDivElement | null}>({});

  useEffect(() => {
    if (!jobId) return;
    
    // Fetch summary via the jobs router.
    fetch(`${API_BASE_URL}/jobs/${jobId}/summary`)
      .then(res => res.json())
      .then(data => setSummary(data))
      .catch(console.error);
  }, [jobId]);

  const handlePointClick = (text: string) => {
    setHighlightedText(text);
    // Scroll to the exact sentence
    const el = sentenceRefs.current[text];
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-6 mt-8 h-[600px]">
      {/* Left Pane: Raw Transcript */}
      <Card className="flex-1 flex flex-col">
        <CardHeader>
          <CardTitle>Source Transcript</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-4">
            <div className="space-y-4">
              {transcript.sentences.map((s: any, idx: number) => {
                const isHighlighted = highlightedText === s.text;
                return (
                  <div 
                    key={idx} 
                    ref={el => { sentenceRefs.current[s.text] = el; }}
                    className={`p-2 rounded transition-colors ${isHighlighted ? "bg-yellow-200 dark:bg-yellow-900/50" : ""}`}
                  >
                    <span className="font-semibold text-sm text-muted-foreground mr-2">
                      {s.speaker || "Unknown"}
                    </span>
                    <span className="text-foreground">{s.text}</span>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Right Pane: Summary */}
      <Card className="flex-1 flex flex-col">
        <CardHeader>
          <CardTitle>Extracted Verbatim Summary</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-4">
            <div className="space-y-4">
              {!summary && <div className="animate-pulse">Loading summary...</div>}
              {summary?.extracted_points?.map((point: any, idx: number) => (
                <div 
                  key={idx} 
                  className="p-4 border rounded-lg cursor-pointer hover:border-primary transition-colors bg-card"
                  onClick={() => handlePointClick(point.text)}
                >
                  <p className="text-sm font-medium">{point.text}</p>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}

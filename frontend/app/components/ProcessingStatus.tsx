"use client";

import { useEffect, useMemo, useState } from "react";

interface ProcessingStatusProps {
  phase: "upload" | "generation";
  progress?: number;
  explicitMessage?: string;
}

const uploadMessages = [
  "Analyzing your document...",
  "Extracting flight details...",
  "Reading hotel confirmations...",
  "Parsing dates and destinations...",
  "Organizing your trip info...",
];

const generationMessages = [
  "Finding top restaurants that match your taste...",
  "Exploring must-see attractions...",
  "Calculating routes and travel times...",
  "Assembling your daily schedule...",
  "Adding booking links and maps...",
  "Finalizing your personalized guide...",
];

export default function ProcessingStatus({ phase, progress, explicitMessage }: ProcessingStatusProps) {
  const [idx, setIdx] = useState(0);
  const messages = useMemo(() => (phase === "upload" ? uploadMessages : generationMessages), [phase]);

  useEffect(() => {
    const id = setInterval(() => {
      setIdx((i) => (i + 1) % messages.length);
    }, 2500);
    return () => clearInterval(id);
  }, [messages.length]);

  const msg = explicitMessage && explicitMessage.trim().length > 0 ? explicitMessage : messages[idx];

  return (
    <div className="text-sm text-gray-700">
      {typeof progress === "number" ? (
        <span>
          {msg} {(progress >= 0 && progress <= 100) ? `(${Math.round(progress)}%)` : ""}
        </span>
      ) : (
        <span>{msg}</span>
      )}
    </div>
  );
}


"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Progress } from "@/components/ui/progress";
import { Card } from "@/components/ui/card";
import { 
  Loader2,
  Sparkles,
  Clock
} from "lucide-react";

export default function GenerateItineraryPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId");
  
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    if (!tripId) {
      router.push("/");
      return;
    }

    generateItinerary();
  }, [tripId]);

  const generateItinerary = async () => {
    try {
      if (isPolling) return;
      setIsPolling(true);

      // Use Server-Sent Events for real-time updates
      const source = new EventSource(`/api/proxy/generation-stream/${tripId}`);
      source.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (typeof data.progress === 'number') setProgress(data.progress);
          if (data.message) setStatusMessage(data.message);
          if (data.status === 'completed') {
            setProgress(100);
            setStatusMessage('Your personalized guide is ready!');
            source.close();
            setTimeout(() => router.push(`/guide?tripId=${tripId}`), 800);
          }
        } catch (e) {
          console.error('SSE parse error', e);
        }
      };
      source.onerror = (e) => {
        // If SSE proxy or backend stream fails, fall back to status polling
        console.warn('SSE unavailable, switching to polling');
        source.close();
        const poll = setInterval(async () => {
          try {
            const res = await fetch(`/api/proxy/generation-status/${tripId}`);
            const data = await res.json();
            if (typeof data.progress === 'number') setProgress(data.progress);
            if (data.message) setStatusMessage(data.message);
            if (data.status === 'completed') {
              clearInterval(poll);
              setProgress(100);
              setTimeout(() => router.push(`/guide?tripId=${tripId}`), 500);
            }
          } catch {}
        }, 1500);
      };

    } catch (error: any) {
      console.error("Generation error:", error);
      setError(error.message || "Failed to generate itinerary");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-3xl"
      >
        <Card className="p-8 shadow-2xl bg-white/95 backdrop-blur">
          <div className="text-center mb-8">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="inline-block mb-4"
            >
              <Sparkles className="h-12 w-12 text-blue-500" />
            </motion.div>
            <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Creating Your Personalized Travel Guide
            </h1>
            <p className="text-gray-600">
              We're using AI to craft the perfect itinerary based on your preferences
            </p>
          </div>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-gray-500 mb-2">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-3" />
          </div>

          {/* Current Status */}
          {statusMessage && (
            <motion.div
              key={statusMessage}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-blue-50 rounded-lg flex items-center gap-3"
            >
              <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
              <span className="text-blue-900 font-medium">{statusMessage}</span>
            </motion.div>
          )}


          {/* Info Box */}
          <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
            <div className="flex items-start gap-3">
              <Clock className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">
                  This usually takes 1-2 minutes
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  We're searching real-time data to find the best restaurants, attractions, and events that match your preferences.
                  Your guide will include personalized recommendations with contact details and booking links.
                </p>
              </div>
            </div>
          </div>

          {/* Error State */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg"
            >
              <p className="text-red-800">{error}</p>
            </motion.div>
          )}
        </Card>
      </motion.div>
    </div>
  );
}
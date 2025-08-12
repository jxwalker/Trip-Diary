"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Progress } from "@/components/ui/progress";
import { Card } from "@/components/ui/card";
import { 
  Loader2,
  MapPin,
  Utensils,
  Calendar,
  Hotel,
  Sparkles,
  CheckCircle,
  Clock,
  Compass
} from "lucide-react";

export default function GenerateItineraryPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId");
  
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const steps = [
    { id: "preferences", label: "Processing preferences", icon: Sparkles, duration: 2000 },
    { id: "restaurants", label: "Finding perfect restaurants", icon: Utensils, duration: 15000 },
    { id: "attractions", label: "Discovering attractions", icon: MapPin, duration: 15000 },
    { id: "events", label: "Searching for events", icon: Calendar, duration: 10000 },
    { id: "hotels", label: "Analyzing hotel area", icon: Hotel, duration: 5000 },
    { id: "itinerary", label: "Creating daily itineraries", icon: Compass, duration: 20000 },
    { id: "finalizing", label: "Finalizing your guide", icon: CheckCircle, duration: 3000 },
  ];

  useEffect(() => {
    if (!tripId) {
      router.push("/");
      return;
    }

    generateItinerary();
  }, [tripId]);

  const generateItinerary = async () => {
    try {
      // Start progress simulation
      let currentProgress = 0;
      let stepIndex = 0;

      const progressInterval = setInterval(() => {
        if (stepIndex < steps.length) {
          const step = steps[stepIndex];
          setCurrentStep(step.label);
          
          // Simulate progress for this step
          const stepProgress = 100 / steps.length;
          currentProgress = Math.min(100, (stepIndex + 1) * stepProgress);
          setProgress(currentProgress);
          
          if (stepIndex > 0) {
            setCompletedSteps(prev => [...prev, steps[stepIndex - 1].id]);
          }
          
          stepIndex++;
        } else {
          clearInterval(progressInterval);
        }
      }, 3000); // Update every 3 seconds

      // Poll for actual completion
      const checkCompletion = setInterval(async () => {
        try {
          const response = await fetch(`/api/proxy/generation-status/${tripId}`);
          const data = await response.json();
          
          if (data.status === "completed") {
            clearInterval(checkCompletion);
            clearInterval(progressInterval);
            setProgress(100);
            setCurrentStep("Your personalized guide is ready!");
            setCompletedSteps(steps.map(s => s.id));
            
            // Redirect to guide page after a short delay
            setTimeout(() => {
              router.push(`/guide?tripId=${tripId}`);
            }, 1500);
          } else if (data.status === "error") {
            clearInterval(checkCompletion);
            clearInterval(progressInterval);
            setError(data.message || "Something went wrong");
          }
        } catch (err) {
          // Continue polling even if there's an error
          console.error("Status check error:", err);
        }
      }, 2000);

      // Timeout after 3 minutes
      setTimeout(() => {
        clearInterval(checkCompletion);
        clearInterval(progressInterval);
        // Even if not fully complete, redirect to guide
        router.push(`/guide?tripId=${tripId}`);
      }, 180000);

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

          {/* Current Step */}
          {currentStep && (
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-blue-50 rounded-lg flex items-center gap-3"
            >
              <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
              <span className="text-blue-900 font-medium">{currentStep}</span>
            </motion.div>
          )}

          {/* Steps Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            {steps.map((step) => {
              const Icon = step.icon;
              const isCompleted = completedSteps.includes(step.id);
              const isCurrent = currentStep === step.label;
              
              return (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className={`
                    p-3 rounded-lg border-2 transition-all
                    ${isCompleted 
                      ? 'border-green-500 bg-green-50' 
                      : isCurrent
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 bg-gray-50'
                    }
                  `}
                >
                  <div className="flex items-center gap-2">
                    {isCompleted ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : isCurrent ? (
                      <Icon className="h-5 w-5 text-blue-600 animate-pulse" />
                    ) : (
                      <Icon className="h-5 w-5 text-gray-400" />
                    )}
                    <span className={`text-sm ${
                      isCompleted 
                        ? 'text-green-900 font-medium' 
                        : isCurrent
                        ? 'text-blue-900 font-medium'
                        : 'text-gray-600'
                    }`}>
                      {step.label}
                    </span>
                  </div>
                </motion.div>
              );
            })}
          </div>

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
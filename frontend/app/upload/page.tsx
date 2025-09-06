"use client";

import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import ProcessingStatus from "@/app/components/ProcessingStatus";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Upload,
  FileText,
  X,
  CheckCircle,
  Loader2,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Info,
  Plane,
  Hotel,
  Calendar,
  MapPin
} from "lucide-react";
import { useRouter } from "next/navigation";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  file: File;
}

const UPLOAD_PERSIST_KEY = "tripcraft.upload.progress";

interface PersistedUpload {
  tripId: string;
  startedAt: number;
  status: 'processing' | 'completed' | 'error';
  progress: number;
  message: string;
  fileName: string;
  fileSize: number;
  fileType: string;
}

export default function SimplifiedUploadPage() {
  const router = useRouter();
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<{
    progress: number;
    message: string;
    extractedData?: any;
  }>({ progress: 0, message: "" });
  const [error, setError] = useState<string | null>(null);
  const [resumeData, setResumeData] = useState<PersistedUpload | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setUploadedFile({
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        type: file.type,
        file: file
      });
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/*": [".png", ".jpg", ".jpeg"],
      "text/*": [".txt"],
    },
    multiple: false,
    maxFiles: 1
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  // Progress persistence and resume logic
  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = localStorage.getItem(UPLOAD_PERSIST_KEY);
      if (raw) {
        const saved: PersistedUpload = JSON.parse(raw);
        if (saved && saved.status === 'processing') {
          setResumeData(saved);
        }
      }
    } catch (e) {
      // ignore
    }
  }, []);

  const startPolling = (tripId: string) => {
    let attempts = 0;
    const maxAttempts = 180; // allow up to ~3 minutes

    const checkStatus = async () => {
      try {
        const statusResponse = await fetch(`/api/proxy/status/${tripId}`);
        const statusData = await statusResponse.json();

        const progress = statusData.progress || 0;
        const message = statusData.message || "Processing...";

        setProcessingStatus({
          progress,
          message,
          extractedData: statusData.extracted_data
        });

        // Persist destination for smart defaults if available
        try {
          const dest = statusData?.extracted_data?.destination;
          if (dest) {
            const key = `tripcraft.trip.${tripId}.destination`;
            sessionStorage.setItem(key, dest);
          }
        } catch (e) {}

        try {
          const raw = localStorage.getItem(UPLOAD_PERSIST_KEY);
          const saved = raw ? JSON.parse(raw) : {};
          localStorage.setItem(UPLOAD_PERSIST_KEY, JSON.stringify({
            ...saved,
            tripId,
            status: "processing",
            progress,
            message
          }));
        } catch (e) {}

        if (statusData.status === "completed") {
          try { localStorage.removeItem(UPLOAD_PERSIST_KEY); } catch (e) {}
          setTimeout(() => {
            router.push(`/preferences-modern?tripId=${tripId}`);
          }, 500);
        } else if (statusData.status === "error") {
          throw new Error(statusData.message || "Processing failed");
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(checkStatus, 1000);
        } else {
          throw new Error("Processing timeout");
        }
      } catch (err) {
        if (attempts < maxAttempts) {
          attempts++;
          setTimeout(checkStatus, 2000);
        } else {
          try {
            const raw = localStorage.getItem(UPLOAD_PERSIST_KEY);
            const saved = raw ? JSON.parse(raw) : {};
            localStorage.setItem(UPLOAD_PERSIST_KEY, JSON.stringify({
              ...saved,
              status: "error",
              message: (err as Error)?.message || "Error"
            }));
          } catch (e) {}
          console.error("Error:", err);
          setError((err as Error)?.message || "Something went wrong");
          setIsProcessing(false);
        }
      }
    };

    setTimeout(checkStatus, 2000);
  };

  const handleResume = () => {
    if (!resumeData) return;
    const dummyFile = new File([""], resumeData.fileName, { type: resumeData.fileType });
    const stubUploaded: UploadedFile = {
      id: "resumed-" + Math.random().toString(36).substr(2, 9),
      name: resumeData.fileName,
      size: resumeData.fileSize,
      type: resumeData.fileType,
      file: dummyFile
    };
    setUploadedFile(stubUploaded);
    setError(null);
    setIsProcessing(true);
    setProcessingStatus({
      progress: resumeData.progress || 0,
      message: resumeData.message || "Processing...",
    });
    startPolling(resumeData.tripId);
    setResumeData(null);
  };

  const discardResume = () => {
    try { localStorage.removeItem(UPLOAD_PERSIST_KEY); } catch (e) {}
    setResumeData(null);
  };

  const handleProcess = async () => {
    if (!uploadedFile) return;
    
    setIsProcessing(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append("file", uploadedFile.file, uploadedFile.name);
      formData.append("use_vision", "true");
      
      const response = await fetch("/api/proxy/upload", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }
      
      const data = await response.json();
      const tripId = data.trip_id;

      try {
        localStorage.setItem(UPLOAD_PERSIST_KEY, JSON.stringify({
          tripId,
          startedAt: Date.now(),
          status: 'processing',
          progress: 0,
          message: 'Uploading...',
          fileName: uploadedFile.name,
          fileSize: uploadedFile.size,
          fileType: uploadedFile.type
        }));
      } catch (e) {}

      startPolling(tripId);
      
    } catch (error: any) {
      console.error("Error:", error);
      try {
        const raw = localStorage.getItem(UPLOAD_PERSIST_KEY);
        if (raw) {
          const saved = JSON.parse(raw);
          localStorage.setItem(UPLOAD_PERSIST_KEY, JSON.stringify({
            ...saved,
            status: 'error',
            message: error?.message || 'Error'
          }));
        }
      } catch (e) {}
      setError(error.message || "Something went wrong");
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        {resumeData && !isProcessing && !uploadedFile && (
          <Alert className="mb-4 border-blue-200 bg-blue-50">
            <Info className="h-4 w-4 text-blue-600" />
            <AlertDescription>
              You have an in-progress upload. Would you like to resume?
              <div className="mt-3 flex gap-2">
                <Button size="sm" onClick={handleResume} className="bg-blue-600 text-white">
                  Resume Upload
                </Button>
                <Button size="sm" variant="outline" onClick={discardResume}>
                  Discard
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        )}
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Upload Your Travel Document
          </h1>
          <p className="text-lg text-gray-600">
            We'll extract all the details and create your perfect itinerary
          </p>
        </motion.div>

        {/* Main Upload Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="p-8 shadow-xl bg-white">
            {!uploadedFile ? (
              <>
                {/* Dropzone */}
                <div
                  {...getRootProps()}
                  className={`
                    border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all
                    ${isDragActive 
                      ? "border-blue-500 bg-blue-50" 
                      : "border-gray-300 hover:border-gray-400 bg-gray-50"
                    }
                  `}
                >
                  <input {...getInputProps()} />
                  <Upload className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                  <p className="text-xl font-medium mb-2">
                    {isDragActive ? "Drop your file here" : "Drop your travel document here"}
                  </p>
                  <p className="text-gray-500 mb-4">or click to browse</p>
                  <p className="text-sm text-gray-400">
                    Supports PDF, images, and text files
                  </p>
                </div>

                {/* Quick Info */}
                <div className="mt-6 grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>Flight confirmations</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>Hotel bookings</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>Travel itineraries</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>Email confirmations</span>
                  </div>
                </div>
              </>
            ) : (
              <>
                {/* File Preview */}
                <div className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileText className="h-10 w-10 text-blue-500" />
                      <div>
                        <p className="font-medium">{uploadedFile.name}</p>
                        <p className="text-sm text-gray-500">
                          {formatFileSize(uploadedFile.size)}
                        </p>
                      </div>
                    </div>
                    {!isProcessing && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setUploadedFile(null);
                          setError(null);
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>

                {/* Processing Status */}
                {isProcessing && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    className="mt-6 space-y-4"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Processing</span>
                      <span className="text-sm text-gray-500">{processingStatus.progress}%</span>
                    </div>
                    <Progress value={processingStatus.progress} className="h-2" />
                    <ProcessingStatus phase="upload" progress={processingStatus.progress} explicitMessage={processingStatus.message} />
                    
                    {processingStatus.extractedData && (
                      <div className="p-3 bg-blue-50 rounded-lg space-y-2">
                        <p className="text-sm font-medium text-blue-900">Found:</p>
                        <div className="grid grid-cols-2 gap-2 text-sm text-blue-700">
                          {processingStatus.extractedData.destination && (
                            <div className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {processingStatus.extractedData.destination}
                            </div>
                          )}
                          {processingStatus.extractedData.dates?.start_date && (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {processingStatus.extractedData.dates.start_date}
                            </div>
                          )}
                          {processingStatus.extractedData.flights?.length > 0 && (
                            <div className="flex items-center gap-1">
                              <Plane className="h-3 w-3" />
                              {processingStatus.extractedData.flights.length} flight(s)
                            </div>
                          )}
                          {processingStatus.extractedData.hotels?.length > 0 && (
                            <div className="flex items-center gap-1">
                              <Hotel className="h-3 w-3" />
                              {processingStatus.extractedData.hotels.length} hotel(s)
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Error Message */}
                {error && (
                  <Alert className="mt-4 border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-800">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Action Button */}
                {!isProcessing && (
                  <Button
                    onClick={handleProcess}
                    size="lg"
                    className="w-full mt-6 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700"
                  >
                    <Sparkles className="h-5 w-5 mr-2" />
                    Create My Itinerary
                    <ArrowRight className="h-5 w-5 ml-2" />
                  </Button>
                )}
              </>
            )}
          </Card>
        </motion.div>

        {/* Info Box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-6"
        >
          <Alert className="border-blue-200 bg-blue-50">
            <Info className="h-4 w-4 text-blue-600" />
            <AlertDescription>
              <strong>What happens next?</strong><br />
              We'll extract your trip details, find the best restaurants and attractions 
              with real-time data, and create a complete day-by-day itinerary with authentic 
              recommendations - not placeholders!
            </AlertDescription>
          </Alert>
        </motion.div>

        {/* Manual Input Option */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-4 text-center"
        >
          <p className="text-gray-600 mb-2">Don't have a document?</p>
          <Button
            variant="outline"
            onClick={() => router.push("/create-trip")}
            className="border-blue-300 text-blue-600 hover:bg-blue-50"
          >
            Enter Trip Details Manually
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </motion.div>
      </div>
    </div>
  );
}
"use client";

import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import {
  Upload,
  FileText,
  X,
  CheckCircle,
  Loader2,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Mail,
  Type,
  FileUp,
  Globe,
  ChevronLeft,
  Calendar,
  Plane,
  Hotel,
  MapPin,
  Users,
  AlertTriangle,
  Info
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  status: "uploading" | "processing" | "completed" | "error";
  progress: number;
  file?: File; // Actual file object for real upload
  extractedData?: any;
}

interface TripDetails {
  startDate: string;
  endDate: string;
  destination: string;
  travelers: number;
  flights: {
    outbound: string;
    return: string;
  };
  hotels: {
    name: string;
    checkIn: string;
    checkOut: string;
  }[];
}

export default function UploadPage() {
  const router = useRouter();
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [freeText, setFreeText] = useState("");
  const [activeTab, setActiveTab] = useState("upload");
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<{
    progress: number;
    message: string;
    extractedData?: any;
  }>({ progress: 0, message: "" });
  const [tripDetails, setTripDetails] = useState<TripDetails>({
    startDate: "",
    endDate: "",
    destination: "",
    travelers: 1,
    flights: {
      outbound: "",
      return: ""
    },
    hotels: []
  });
  // No mocks, no fake warnings - real backend only

  // Progress Persistence - Save and restore upload state
  useEffect(() => {
    // Check for saved upload session on mount
    const savedSession = localStorage.getItem('uploadSession');
    if (savedSession) {
      try {
        const session = JSON.parse(savedSession);
        // Check if session is recent (within 24 hours)
        const sessionAge = Date.now() - session.timestamp;
        if (sessionAge < 24 * 60 * 60 * 1000) {
          // Restore session data
          if (session.freeText) setFreeText(session.freeText);
          if (session.tripDetails) setTripDetails(session.tripDetails);
          if (session.processingStatus) {
            setProcessingStatus(session.processingStatus);
            // If there was an ongoing processing, offer to resume
            if (session.tripId && session.processingStatus.progress < 100) {
              // Show resume option
              const shouldResume = window.confirm(
                'You have an incomplete upload from your previous session. Would you like to resume?'
              );
              if (shouldResume) {
                resumeProcessing(session.tripId);
              } else {
                // Clear the saved session if user doesn't want to resume
                localStorage.removeItem('uploadSession');
              }
            }
          }
        } else {
          // Session too old, clear it
          localStorage.removeItem('uploadSession');
        }
      } catch (error) {
        console.error('Error restoring session:', error);
        localStorage.removeItem('uploadSession');
      }
    }
  }, []);

  // Save session data when it changes
  useEffect(() => {
    if (freeText || tripDetails.destination || processingStatus.progress > 0) {
      const sessionData = {
        timestamp: Date.now(),
        freeText,
        tripDetails,
        processingStatus,
        tripId: sessionStorage.getItem('tripId')
      };
      localStorage.setItem('uploadSession', JSON.stringify(sessionData));
    }
  }, [freeText, tripDetails, processingStatus]);

  // Resume processing function
  const resumeProcessing = async (tripId: string) => {
    setIsProcessing(true);
    let attempts = 0;
    const maxAttempts = 120;
    
    const checkStatus = async () => {
      try {
        const statusResponse = await fetch(`/api/proxy/status/${tripId}`);
        const statusData = await statusResponse.json();
        
        console.log("Resume status update:", statusData);
        
        setProcessingStatus({
          progress: statusData.progress || 0,
          message: statusData.message || "Resuming processing...",
          extractedData: statusData.extracted_data
        });
        
        if (statusData.status === "completed") {
          // Clear saved session on completion
          localStorage.removeItem('uploadSession');
          router.push(`/summary?tripId=${tripId}`);
        } else if (statusData.status === "error" || statusData.status === "failed") {
          throw new Error(statusData.message || "Processing failed");
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(checkStatus, 1000);
        } else {
          throw new Error("Processing timeout. Please try uploading again.");
        }
      } catch (err) {
        console.error("Error checking resume status:", err);
        setIsProcessing(false);
        localStorage.removeItem('uploadSession');
      }
    };
    
    checkStatus();
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Real files - no simulation, no mocks
    const newFiles = acceptedFiles.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      status: "completed" as const, // Files are ready immediately for real upload
      progress: 100,
      file: file // Store actual file object for real upload
    }));

    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/*": [".png", ".jpg", ".jpeg"],
      "text/*": [".txt", ".eml"],
    },
    multiple: true,
  });

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  const getFileIcon = (type: string) => {
    if (type.includes("pdf")) return "📄";
    if (type.includes("image")) return "🖼️";
    if (type.includes("text")) return "📝";
    return "📎";
  };

  const handleProcessWithAI = async () => {
    setIsProcessing(true);
    // Real backend processing
    
    try {
      // Prepare form data
      const formData = new FormData();
      
      // Add manual trip details
      console.log("Sending trip details:", tripDetails);
      formData.append("trip_details", JSON.stringify(tripDetails));
      
      // Add free text if any
      if (freeText) {
        console.log("Sending free text:", freeText);
        formData.append("free_text", freeText);
      }
      
      // Add actual files for real upload
      // If we have exactly one file, use the single-file endpoint
      let apiPath = '/api/proxy/upload';
      
      if (files.length === 1 && files[0].file) {
        console.log("Single file upload:", files[0].name);
        formData.append("file", files[0].file, files[0].name);
        formData.append("use_vision", "true");
        apiPath = '/api/proxy/upload-single';
      } else if (files.length > 1) {
        // Multiple files - use the multi-file endpoint
        files.forEach((uploadedFile) => {
          if (uploadedFile.file) {
            console.log("Adding file:", uploadedFile.name);
            formData.append("files", uploadedFile.file, uploadedFile.name);
          }
        });
        formData.append("use_vision", "true");
      } else if (!freeText && !tripDetails.destination) {
        // No files and no data - can't process
        throw new Error("Please upload a file or enter trip details");
      }
      
      console.log("Sending request via proxy:", apiPath);
      const response = await fetch(apiPath, {
        method: "POST",
        body: formData,
      });
      
      console.log("Response status:", response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Backend error:", errorText);
        throw new Error(`Backend error: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log("Response data:", data);
      const tripId = data.trip_id;
      
      // Store trip ID in sessionStorage for next page
      sessionStorage.setItem("tripId", tripId);
      
      // Poll for completion - REAL progress from backend
      let attempts = 0;
      const maxAttempts = 120; // Increase to 60 seconds (120 * 500ms)
      
      const checkStatus = async () => {
        try {
          const statusResponse = await fetch(`/api/proxy/status/${tripId}`);
          const statusData = await statusResponse.json();
          
          console.log("Status update:", statusData);
          
          // Update with REAL progress from backend
          setProcessingStatus({
            progress: statusData.progress || 0,
            message: statusData.message || "Processing...",
            extractedData: statusData.extracted_data
          });
          
          if (statusData.status === "completed") {
            // Clear saved session on successful completion
            localStorage.removeItem('uploadSession');
            // Navigate to summary page with trip ID
            router.push(`/summary?tripId=${tripId}`);
          } else if (statusData.status === "error" || statusData.status === "failed") {
            throw new Error(statusData.message || "Processing failed");
          } else if (attempts < maxAttempts) {
            attempts++;
            setTimeout(checkStatus, 1000); // Check every 1 second
          } else {
            throw new Error("Processing is taking longer than expected. Please check the backend logs.");
          }
        } catch (err) {
          console.error("Error checking status:", err);
          if (attempts < maxAttempts) {
            attempts++;
            setTimeout(checkStatus, 2000); // Retry after 2 seconds on error
          } else {
            throw err;
          }
        }
      };
      
      // Start polling after 2 seconds to give backend time to start
      setTimeout(checkStatus, 2000);
      
    } catch (error: any) {
      console.error("Error processing with AI:", error);
      // Better error handling
      const errorMessage = error?.message || "Unknown error occurred";
      console.log("Full error:", error);
      
      // Show more specific error message
      if (errorMessage.includes("Load failed") || errorMessage.includes("fetch")) {
        alert("Connection error: Please ensure the backend is running and the proxy is configured.");
      } else {
        alert(`Error: ${errorMessage}`);
      }
      setIsProcessing(false);
    }
  };

  const hasFiles = files.length > 0 || freeText.length > 0;
  const allFilesProcessed = files.every((f) => f.status === "completed");
  const hasManualInput = tripDetails.destination && tripDetails.startDate && tripDetails.endDate;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <div className="flex items-center space-x-2">
              <Globe className="h-6 w-6 text-sky-500" />
              <span className="text-xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
                TripCraft AI
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="px-3 py-1">
              Step 1 of 4
            </Badge>
          </div>
        </div>
      </nav>

      <div className="pt-24 pb-12 px-6">
        <div className="container mx-auto max-w-5xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-sky-600 bg-clip-text text-transparent">
              Add Your Travel Information
            </h1>
            <p className="text-gray-600 text-lg">
              Upload documents or enter details manually - we'll create your perfect itinerary
            </p>
          </motion.div>

          {/* Real backend status - no mocks */}

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Left Column - Manual Input */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Trip Details
                  </CardTitle>
                  <CardDescription>
                    Enter your travel information manually
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="destination">
                      <MapPin className="h-3 w-3 inline mr-1" />
                      Destination
                    </Label>
                    <Input
                      id="destination"
                      placeholder="e.g., Paris, France"
                      value={tripDetails.destination}
                      onChange={(e) => setTripDetails({...tripDetails, destination: e.target.value})}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label htmlFor="startDate">Start Date</Label>
                      <Input
                        id="startDate"
                        type="date"
                        value={tripDetails.startDate}
                        onChange={(e) => setTripDetails({...tripDetails, startDate: e.target.value})}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="endDate">End Date</Label>
                      <Input
                        id="endDate"
                        type="date"
                        value={tripDetails.endDate}
                        onChange={(e) => setTripDetails({...tripDetails, endDate: e.target.value})}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="travelers">
                      <Users className="h-3 w-3 inline mr-1" />
                      Number of Travelers
                    </Label>
                    <Input
                      id="travelers"
                      type="number"
                      min="1"
                      value={tripDetails.travelers}
                      onChange={(e) => setTripDetails({...tripDetails, travelers: parseInt(e.target.value)})}
                    />
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <h4 className="font-medium flex items-center gap-2">
                      <Plane className="h-4 w-4" />
                      Flight Details
                    </h4>
                    <div className="space-y-2">
                      <Label htmlFor="outbound">Outbound Flight</Label>
                      <Input
                        id="outbound"
                        placeholder="AA123 - JFK to CDG"
                        value={tripDetails.flights.outbound}
                        onChange={(e) => setTripDetails({
                          ...tripDetails, 
                          flights: {...tripDetails.flights, outbound: e.target.value}
                        })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="return">Return Flight</Label>
                      <Input
                        id="return"
                        placeholder="AA456 - CDG to JFK"
                        value={tripDetails.flights.return}
                        onChange={(e) => setTripDetails({
                          ...tripDetails, 
                          flights: {...tripDetails.flights, return: e.target.value}
                        })}
                      />
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <h4 className="font-medium flex items-center gap-2">
                      <Hotel className="h-4 w-4" />
                      Hotel Information
                    </h4>
                    <div className="space-y-2">
                      <Label htmlFor="hotel">Hotel Name</Label>
                      <Input
                        id="hotel"
                        placeholder="e.g., Hotel Plaza Athénée"
                      />
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      Add Hotel
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column - File Upload */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                  <TabsList className="grid w-full grid-cols-3 mb-6">
                    <TabsTrigger value="upload" className="flex items-center gap-2">
                      <FileUp className="h-4 w-4" />
                      File Upload
                    </TabsTrigger>
                    <TabsTrigger value="email" className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      Email Forward
                    </TabsTrigger>
                    <TabsTrigger value="text" className="flex items-center gap-2">
                      <Type className="h-4 w-4" />
                      Free Text
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="upload" className="space-y-4">
                    {/* Dropzone */}
                    <Card
                      {...getRootProps()}
                      className={`
                        p-12 border-2 border-dashed cursor-pointer transition-all
                        ${isDragActive 
                          ? "border-sky-500 bg-sky-50" 
                          : "border-gray-300 hover:border-gray-400 bg-white"
                        }
                      `}
                    >
                      <input {...getInputProps()} />
                      <div className="text-center">
                        <motion.div
                          animate={{ 
                            y: isDragActive ? -10 : 0,
                            scale: isDragActive ? 1.1 : 1
                          }}
                          className="mx-auto w-16 h-16 mb-4 rounded-full bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center text-white"
                        >
                          <Upload className="h-8 w-8" />
                        </motion.div>
                        <p className="text-xl font-medium mb-2">
                          {isDragActive
                            ? "Drop your files here"
                            : "Drag & drop your files here"}
                        </p>
                        <p className="text-gray-500 mb-4">
                          or click to browse from your computer
                        </p>
                        <p className="text-sm text-gray-400">
                          Supports PDF, Images, TXT, and EML files
                        </p>
                      </div>
                    </Card>

                    {/* Real Processing Info */}
                    <Alert className="border-blue-200 bg-blue-50">
                      <Info className="h-4 w-4 text-blue-600" />
                      <AlertTitle>Real AI Processing</AlertTitle>
                      <AlertDescription className="space-y-2 mt-2">
                        <div className="flex items-start gap-2">
                          <Badge className="bg-blue-100 text-blue-700">1</Badge>
                          <span className="text-sm">Files uploaded to backend server</span>
                        </div>
                        <div className="flex items-start gap-2">
                          <Badge className="bg-blue-100 text-blue-700">2</Badge>
                          <span className="text-sm">GPT-4o-mini extracts travel information</span>
                        </div>
                        <div className="flex items-start gap-2">
                          <Badge className="bg-blue-100 text-blue-700">3</Badge>
                          <span className="text-sm">Itinerary generated with real data</span>
                        </div>
                        <div className="text-sm font-medium mt-2">
                          Backend running on localhost:8000
                        </div>
                      </AlertDescription>
                    </Alert>

                    {/* File List */}
                    <AnimatePresence>
                      {files.length > 0 && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="space-y-3"
                        >
                          <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                            <FileText className="h-4 w-4" />
                            Uploaded Files ({files.length})
                          </h3>
                          {files.map((file) => (
                            <motion.div
                              key={file.id}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              exit={{ opacity: 0, x: 20 }}
                              layout
                            >
                              <Card className="p-4">
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center space-x-3">
                                    <span className="text-2xl">{getFileIcon(file.type)}</span>
                                    <div>
                                      <p className="font-medium">{file.name}</p>
                                      <p className="text-sm text-gray-500">
                                        {formatFileSize(file.size)}
                                      </p>
                                    </div>
                                  </div>
                                  <div className="flex items-center space-x-3">
                                    {/* Files are ready immediately - no fake progress */}
                                    {file.status === "completed" && (
                                      <div className="flex items-center space-x-2 text-green-600">
                                        <CheckCircle className="h-5 w-5" />
                                        <span className="text-sm">Ready to upload</span>
                                      </div>
                                    )}
                                    {file.status === "error" && (
                                      <div className="flex items-center space-x-2 text-red-600">
                                        <AlertCircle className="h-5 w-5" />
                                        <span className="text-sm">Error</span>
                                      </div>
                                    )}
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => removeFile(file.id)}
                                    >
                                      <X className="h-4 w-4" />
                                    </Button>
                                  </div>
                                </div>
                              </Card>
                            </motion.div>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </TabsContent>

                  <TabsContent value="email" className="space-y-4">
                    <Card className="p-8 bg-gradient-to-br from-blue-50 to-sky-50">
                      <div className="text-center">
                        <Mail className="h-12 w-12 mx-auto mb-4 text-sky-600" />
                        <h3 className="text-xl font-semibold mb-2">Forward Travel Emails</h3>
                        <p className="text-gray-600 mb-4">
                          Forward your travel confirmation emails to:
                        </p>
                        <div className="bg-white rounded-lg px-4 py-2 inline-block">
                          <code className="text-lg font-mono text-sky-600">
                            travel@tripcraft.ai
                          </code>
                        </div>
                        <p className="text-sm text-gray-500 mt-4">
                          We'll automatically extract all travel details from your emails
                        </p>
                      </div>
                    </Card>
                  </TabsContent>

                  <TabsContent value="text" className="space-y-4">
                    <Card className="p-6">
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold">Paste Your Travel Information</h3>
                          <Badge variant="outline">
                            {freeText.length} characters
                          </Badge>
                        </div>
                        <Textarea
                          placeholder="Paste your flight details, hotel bookings, or any travel information here..."
                          className="min-h-[300px] resize-none"
                          value={freeText}
                          onChange={(e) => setFreeText(e.target.value)}
                        />
                        <p className="text-sm text-gray-500">
                          Our AI will extract and organize all relevant travel information
                        </p>
                      </div>
                    </Card>
                  </TabsContent>
                </Tabs>
              </motion.div>
            </div>
          </div>

          {/* Real-time Processing Status */}
          {isProcessing && processingStatus.message && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6"
            >
              <Card className="border-blue-200 bg-gradient-to-r from-blue-50 to-sky-50">
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-blue-900">Processing Your Travel Information</h3>
                      <Badge className="bg-blue-600 text-white">{processingStatus.progress}%</Badge>
                    </div>
                    <Progress value={processingStatus.progress} className="h-2" />
                    <p className="text-sm text-blue-700">{processingStatus.message}</p>
                    
                    {/* Show extracted data as it's processed */}
                    {processingStatus.extractedData && (
                      <div className="mt-4 p-3 bg-white rounded-lg">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Extracted Information:</h4>
                        <div className="space-y-2 text-sm text-gray-600">
                          {processingStatus.extractedData.destination && (
                            <div className="flex items-center gap-2">
                              <MapPin className="h-3 w-3" />
                              <span>Destination: {processingStatus.extractedData.destination}</span>
                            </div>
                          )}
                          {processingStatus.extractedData.dates?.start_date && (
                            <div className="flex items-center gap-2">
                              <Calendar className="h-3 w-3" />
                              <span>Dates: {processingStatus.extractedData.dates.start_date} to {processingStatus.extractedData.dates.end_date}</span>
                            </div>
                          )}
                          {processingStatus.extractedData.flights?.length > 0 && (
                            <div className="flex items-center gap-2">
                              <Plane className="h-3 w-3" />
                              <span>Found {processingStatus.extractedData.flights.length} flight(s)</span>
                            </div>
                          )}
                          {processingStatus.extractedData.hotels?.length > 0 && (
                            <div className="flex items-center gap-2">
                              <Hotel className="h-3 w-3" />
                              <span>Found {processingStatus.extractedData.hotels.length} hotel(s)</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="flex justify-between items-center mt-8"
          >
            <Link href="/">
              <Button variant="outline" size="lg">
                <ChevronLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
            </Link>
            
            <div className="flex items-center gap-4">
              {(hasFiles || hasManualInput) && (
                <p className="text-sm text-gray-500">
                  {hasFiles && `${files.length} file(s) ready`}
                  {hasFiles && hasManualInput && " + "}
                  {hasManualInput && "manual details entered"}
                </p>
              )}
              <Button
                size="lg"
                disabled={(!hasFiles && !hasManualInput) || (hasFiles && !allFilesProcessed)}
                className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700"
                onClick={handleProcessWithAI}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Process with AI
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          </motion.div>

          {/* Tips */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="mt-12 p-6 bg-blue-50 rounded-lg"
          >
            <h4 className="font-semibold text-blue-900 mb-3">Pro Tips:</h4>
            <ul className="space-y-2 text-sm text-blue-800">
              <li className="flex items-start">
                <CheckCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                You can combine manual input with uploaded documents for the most complete itinerary
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                Upload multiple files at once - we'll process them all together
              </li>
              <li className="flex items-start">
                <CheckCircle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                Include hotel confirmations to get location-based recommendations
              </li>
            </ul>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
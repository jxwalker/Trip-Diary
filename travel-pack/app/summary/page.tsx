"use client";

import { Suspense } from "react";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { formatTravelDate, calculateTripDuration } from "@/lib/dateUtils";
import {
  CheckCircle,
  AlertCircle,
  Edit2,
  Save,
  X,
  ArrowRight,
  Calendar,
  Plane,
  Hotel,
  MapPin,
  Users,
  FileText,
  ChevronLeft,
  Globe,
  Sparkles,
  Clock,
  AlertTriangle,
  Loader2
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface ExtractedData {
  destination: string;
  startDate: string;
  endDate: string;
  travelers: number;
  flights: {
    outbound: {
      flightNumber: string;
      airline: string;
      departure: { airport: string; time: string; date: string };
      arrival: { airport: string; time: string };
      confirmation?: string;
    };
    return: {
      flightNumber: string;
      airline: string;
      departure: { airport: string; time: string; date: string };
      arrival: { airport: string; time: string };
      confirmation?: string;
    };
  };
  hotels: {
    name: string;
    address: string;
    checkIn: string;
    checkOut: string;
    confirmation?: string;
  }[];
  extractedFrom: {
    files: string[];
    manualInput: boolean;
    freeText: boolean;
  };
}

function SummaryPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId") || sessionStorage.getItem("tripId");
  
  const [isEditing, setIsEditing] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [hasChanges, setHasChanges] = useState(false);
  
  // Empty data structure - will be filled from backend
  const [extractedData, setExtractedData] = useState<ExtractedData>({
    destination: "",
    startDate: "",
    endDate: "",
    travelers: 1,
    flights: {
      outbound: {
        flightNumber: "",
        airline: "",
        departure: { airport: "", time: "", date: "" },
        arrival: { airport: "", time: "" },
        confirmation: ""
      },
      return: {
        flightNumber: "",
        airline: "",
        departure: { airport: "", time: "", date: "" },
        arrival: { airport: "", time: "" },
        confirmation: ""
      }
    },
    hotels: [],
    extractedFrom: {
      files: [],
      manualInput: false,
      freeText: false
    }
  });

  // Fetch itinerary data when component mounts
  useEffect(() => {
    const fetchItinerary = async () => {
      if (!tripId) {
        setIsLoading(false);
        return;
      }
      
      try {
        // Use Next.js proxy to avoid connection issues
        const response = await fetch(`/api/proxy/itinerary/${tripId}`);
        if (response.ok) {
          const data = await response.json();
          
          // Transform backend data to match our ExtractedData structure
          if (data.itinerary) {
            const itinerary = data.itinerary;
            
            // Extract actual data from backend without mock fallbacks
            const newData: ExtractedData = {
              destination: itinerary.trip_summary?.destination || "",
              startDate: itinerary.trip_summary?.start_date || "",
              endDate: itinerary.trip_summary?.end_date || "",
              travelers: itinerary.trip_summary?.total_travelers || 1,
              flights: {
                outbound: itinerary.flights?.[0] ? {
                  flightNumber: itinerary.flights[0].flight_number || "",
                  airline: itinerary.flights[0].airline || "",
                  departure: itinerary.flights[0].departure || { airport: "", time: "", date: "" },
                  arrival: itinerary.flights[0].arrival || { airport: "", time: "" },
                  confirmation: itinerary.flights[0].confirmation || ""
                } : extractedData.flights.outbound,
                return: itinerary.flights?.[1] ? {
                  flightNumber: itinerary.flights[1].flight_number || "",
                  airline: itinerary.flights[1].airline || "",
                  departure: itinerary.flights[1].departure || { airport: "", time: "", date: "" },
                  arrival: itinerary.flights[1].arrival || { airport: "", time: "" },
                  confirmation: itinerary.flights[1].confirmation || ""
                } : extractedData.flights.return
              },
              hotels: itinerary.accommodations?.map((hotel: any) => ({
                name: hotel.name || "",
                address: hotel.address || "",
                checkIn: hotel.check_in || "",
                checkOut: hotel.check_out || "",
                confirmation: hotel.confirmation || ""
              })) || [],
              extractedFrom: data.extracted_from || extractedData.extractedFrom
            };
            
            setExtractedData(newData);
          }
        }
      } catch (error) {
        console.error("Error fetching itinerary:", error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchItinerary();
  }, [tripId]);

  const handleEdit = (field: string) => {
    setIsEditing(field);
  };

  const handleSave = (field: string) => {
    setIsEditing(null);
    setHasChanges(true);
  };

  const handleCancel = () => {
    setIsEditing(null);
  };

  const handleConfirmAndContinue = () => {
    setIsProcessing(true);
    // Store tripId for the next pages
    if (tripId) {
      localStorage.setItem("currentTripId", tripId);
    }
    // Navigate to preferences page to personalize the guide
    setTimeout(() => {
      router.push(`/preferences-consolidated?tripId=${tripId}`);
    }, 1000);
  };

  const formatDate = (dateString: string) => {
    return formatTravelDate(dateString);
  };

  const calculateDuration = () => {
    return calculateTripDuration(extractedData.startDate, extractedData.endDate);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-gradient-to-br from-sky-500 to-blue-600">
            <Globe className="h-8 w-8 text-white animate-pulse" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading your travel information...</h2>
          <p className="text-gray-500">Please wait while we fetch your data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link href="/upload">
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
              Step 2 of 4
            </Badge>
          </div>
        </div>
      </nav>

      <div className="pt-24 pb-12 px-6">
        <div className="container mx-auto max-w-4xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-sky-600 bg-clip-text text-transparent">
              Review Your Travel Information
            </h1>
            <p className="text-gray-600 text-lg">
              Please verify the extracted information is correct before we create your itinerary
            </p>
          </motion.div>

          {/* Data Sources */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-6"
          >
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription>
                <strong>Successfully extracted information from:</strong>
                <div className="mt-2 flex flex-wrap gap-2">
                  {extractedData.extractedFrom.files.map((file) => (
                    <Badge key={file} variant="secondary" className="text-xs">
                      <FileText className="h-3 w-3 mr-1" />
                      {file}
                    </Badge>
                  ))}
                  {extractedData.extractedFrom.manualInput && (
                    <Badge variant="secondary" className="text-xs">
                      <Edit2 className="h-3 w-3 mr-1" />
                      Manual Input
                    </Badge>
                  )}
                  {extractedData.extractedFrom.freeText && (
                    <Badge variant="secondary" className="text-xs">
                      <FileText className="h-3 w-3 mr-1" />
                      Free Text
                    </Badge>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          </motion.div>

          {/* Trip Overview Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <MapPin className="h-5 w-5" />
                    Trip Overview
                  </span>
                  {hasChanges && (
                    <Badge className="bg-orange-100 text-orange-700">
                      Modified
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  {/* Destination */}
                  <div className="space-y-2">
                    <Label className="text-sm text-gray-500">Destination</Label>
                    {isEditing === "destination" ? (
                      <div className="flex gap-2">
                        <Input
                          value={extractedData.destination}
                          onChange={(e) => setExtractedData({
                            ...extractedData,
                            destination: e.target.value
                          })}
                          className="flex-1"
                        />
                        <Button size="sm" onClick={() => handleSave("destination")}>
                          <Save className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={handleCancel}>
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{extractedData.destination}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEdit("destination")}
                        >
                          <Edit2 className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Duration */}
                  <div className="space-y-2">
                    <Label className="text-sm text-gray-500">Duration</Label>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="font-medium">{calculateDuration()}</span>
                    </div>
                  </div>

                  {/* Start Date */}
                  <div className="space-y-2">
                    <Label className="text-sm text-gray-500">Start Date</Label>
                    {isEditing === "startDate" ? (
                      <div className="flex gap-2">
                        <Input
                          type="date"
                          value={extractedData.startDate}
                          onChange={(e) => setExtractedData({
                            ...extractedData,
                            startDate: e.target.value
                          })}
                          className="flex-1"
                        />
                        <Button size="sm" onClick={() => handleSave("startDate")}>
                          <Save className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={handleCancel}>
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{formatDate(extractedData.startDate)}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEdit("startDate")}
                        >
                          <Edit2 className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* End Date */}
                  <div className="space-y-2">
                    <Label className="text-sm text-gray-500">End Date</Label>
                    {isEditing === "endDate" ? (
                      <div className="flex gap-2">
                        <Input
                          type="date"
                          value={extractedData.endDate}
                          onChange={(e) => setExtractedData({
                            ...extractedData,
                            endDate: e.target.value
                          })}
                          className="flex-1"
                        />
                        <Button size="sm" onClick={() => handleSave("endDate")}>
                          <Save className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={handleCancel}>
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{formatDate(extractedData.endDate)}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEdit("endDate")}
                        >
                          <Edit2 className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Travelers */}
                  <div className="space-y-2">
                    <Label className="text-sm text-gray-500">Number of Travelers</Label>
                    {isEditing === "travelers" ? (
                      <div className="flex gap-2">
                        <Input
                          type="number"
                          min="1"
                          value={extractedData.travelers}
                          onChange={(e) => setExtractedData({
                            ...extractedData,
                            travelers: parseInt(e.target.value)
                          })}
                          className="flex-1"
                        />
                        <Button size="sm" onClick={() => handleSave("travelers")}>
                          <Save className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={handleCancel}>
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4 text-gray-400" />
                          <span className="font-medium">{extractedData.travelers} {extractedData.travelers === 1 ? "traveler" : "travelers"}</span>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEdit("travelers")}
                        >
                          <Edit2 className="h-3 w-3" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Flights Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Plane className="h-5 w-5" />
                  Flight Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Outbound Flight */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-700">Outbound Flight</h4>
                    <Badge variant="outline">{extractedData.flights.outbound.confirmation}</Badge>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold">{extractedData.flights.outbound.flightNumber}</p>
                        <p className="text-sm text-gray-500">{extractedData.flights.outbound.airline}</p>
                      </div>
                      <Button size="sm" variant="ghost">
                        <Edit2 className="h-3 w-3" />
                      </Button>
                    </div>
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Departure</p>
                        <p className="font-medium">{extractedData.flights.outbound.departure.airport}</p>
                        <p className="text-sm">{extractedData.flights.outbound.departure.time}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-500">Arrival</p>
                        <p className="font-medium">{extractedData.flights.outbound.arrival.airport}</p>
                        <p className="text-sm">{extractedData.flights.outbound.arrival.time}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Return Flight */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-700">Return Flight</h4>
                    <Badge variant="outline">{extractedData.flights.return.confirmation}</Badge>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold">{extractedData.flights.return.flightNumber}</p>
                        <p className="text-sm text-gray-500">{extractedData.flights.return.airline}</p>
                      </div>
                      <Button size="sm" variant="ghost">
                        <Edit2 className="h-3 w-3" />
                      </Button>
                    </div>
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Departure</p>
                        <p className="font-medium">{extractedData.flights.return.departure.airport}</p>
                        <p className="text-sm">{extractedData.flights.return.departure.time}</p>
                      </div>
                      <ArrowRight className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-sm text-gray-500">Arrival</p>
                        <p className="font-medium">{extractedData.flights.return.arrival.airport}</p>
                        <p className="text-sm">{extractedData.flights.return.arrival.time}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Hotels Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Hotel className="h-5 w-5" />
                  Accommodation
                </CardTitle>
              </CardHeader>
              <CardContent>
                {extractedData.hotels.map((hotel, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold">{hotel.name}</h4>
                        <p className="text-sm text-gray-500">{hotel.address}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{hotel.confirmation}</Badge>
                        <Button size="sm" variant="ghost">
                          <Edit2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mt-3">
                      <div>
                        <p className="text-sm text-gray-500">Check-in</p>
                        <p className="font-medium">{formatDate(hotel.checkIn)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Check-out</p>
                        <p className="font-medium">{formatDate(hotel.checkOut)}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          {/* Missing Information Alert */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Alert className="mb-6 border-yellow-200 bg-yellow-50">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <AlertDescription>
                <strong>Optional information you might want to add:</strong>
                <ul className="mt-2 space-y-1 text-sm">
                  <li>• Travel insurance details</li>
                  <li>• Car rental reservations</li>
                  <li>• Restaurant reservations</li>
                  <li>• Activity bookings</li>
                </ul>
              </AlertDescription>
            </Alert>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="flex justify-between items-center"
          >
            <Link href="/upload">
              <Button variant="outline" size="lg">
                <ChevronLeft className="h-4 w-4 mr-2" />
                Back to Upload
              </Button>
            </Link>
            
            <Button
              size="lg"
              className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700"
              onClick={handleConfirmAndContinue}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <Sparkles className="h-4 w-4 mr-2 animate-pulse" />
                  Continuing...
                </>
              ) : (
                <>
                  Personalize Travel Guide
                  <ArrowRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default function SummaryPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SummaryPageContent />
    </Suspense>
  );
}
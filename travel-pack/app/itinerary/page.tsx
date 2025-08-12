"use client";

import { Suspense } from "react";
import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { formatTravelDate, calculateTripDuration } from "@/lib/dateUtils";
import { 
  Loader2, 
  Globe, 
  ChevronLeft, 
  Calendar, 
  MapPin, 
  Clock,
  Plane,
  Hotel,
  Users,
  Download,
  Check,
  AlertTriangle,
  Sparkles,
  Settings,
  RefreshCw,
  Save
} from "lucide-react";
import Link from "next/link";
import EnhancedGuideDisplay from "@/app/components/EnhancedGuideDisplay";

function ItineraryPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tripId = searchParams.get("tripId");
  
  const [loading, setLoading] = useState(true);
  const [itinerary, setItinerary] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [enhancedGuide, setEnhancedGuide] = useState<any>(null);
  const [hasPreferences, setHasPreferences] = useState(false);
  const [dataAvailabilityNote, setDataAvailabilityNote] = useState<string | null>(null);

  useEffect(() => {
    if (!tripId) {
      // Try to get from localStorage as fallback
      const storedTripId = localStorage.getItem("currentTripId");
      if (storedTripId) {
        router.push(`/itinerary?tripId=${storedTripId}`);
      } else {
        setError("No trip ID found. Please start over.");
        setLoading(false);
      }
      return;
    }

    // Add a small delay to avoid race conditions
    const timer = setTimeout(() => {
      fetchItinerary();
    }, 500);

    return () => clearTimeout(timer);
  }, [tripId]);

  const fetchItinerary = async (retryCount = 0) => {
    if (!tripId) {
      console.error("No tripId available");
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      console.log("Fetching itinerary for tripId:", tripId);
      
      // Use Next.js proxy to avoid connection issues
      const statusUrl = `/api/proxy/status/${tripId}`;
      console.log("Checking status at:", statusUrl);
      
      const statusResponse = await fetch(statusUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (!statusResponse.ok) {
        if (statusResponse.status === 404) {
          throw new Error("Trip not found. It may have expired.");
        }
        throw new Error(`Failed to check status: ${statusResponse.status}`);
      }
      
      const statusData = await statusResponse.json();
      console.log("Status data:", statusData);
      
      if (statusData.status !== "completed") {
        console.log("Still processing, will retry in 3 seconds...");
        // Still processing, wait and retry
        setTimeout(() => fetchItinerary(0), 3000);
        return;
      }
      
      // Get the actual itinerary
      const itineraryUrl = `/api/proxy/itinerary/${tripId}`;
      console.log("Fetching itinerary from:", itineraryUrl);
      
      const response = await fetch(itineraryUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("Itinerary not found.");
        }
        throw new Error(`Failed to fetch itinerary: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("Itinerary data received:", data);
      setItinerary(data);
      // Check data availability and surface guidance (no mocks)
      try {
        const recs = data?.recommendations || {};
        const noneAvailable = !recs?.restaurants?.length && !recs?.attractions?.length && !recs?.events?.length;
        if (noneAvailable && !enhancedGuide) {
          setDataAvailabilityNote(
            "Live recommendations are unavailable. Configure required API keys (e.g., PERPLEXITY_API_KEY, GOOGLE_MAPS_API_KEY, OPENWEATHER_API_KEY) in your .env and re-run."
          );
        } else {
          setDataAvailabilityNote(null);
        }
      } catch {}
      
      // Check if enhanced guide exists
      try {
        const guideResponse = await fetch(`/api/proxy/enhanced-guide/${tripId}`);
        if (guideResponse.ok) {
          const guideData = await guideResponse.json();
          setEnhancedGuide(guideData.enhanced_guide);
          setHasPreferences(true);
        }
      } catch (err) {
        console.log("No enhanced guide yet");
      }
      
      setLoading(false);
    } catch (err: any) {
      console.error("Error fetching itinerary:", err);
      
      // Retry logic for connection errors
      if (err.message.includes('Failed to fetch') && retryCount < 3) {
        console.log(`Retrying... attempt ${retryCount + 1}`);
        setTimeout(() => fetchItinerary(retryCount + 1), 1000);
        return;
      }
      
      setError(`Failed to load itinerary: ${err.message}`);
      setLoading(false);
    }
  };

  const handleGeneratePdf = async () => {
    if (!tripId) return;
    
    try {
      setGeneratingPdf(true);
      
      const response = await fetch(`/api/proxy/generate-pdf/${tripId}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error("Failed to generate PDF");
      }
      
      const data = await response.json();
      
      // Download the PDF using the proxy
      window.open(`/api/proxy${data.pdf_url.replace('/api', '')}`, '_blank');
      
    } catch (err) {
      console.error("Error generating PDF:", err);
      alert("Failed to generate PDF. Please try again.");
    } finally {
      setGeneratingPdf(false);
    }
  };

  const formatTime = (time: string) => {
    if (!time) return "";
    return time;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
        <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
          <div className="container mx-auto px-6 py-4 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Link href="/summary">
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
            <Badge variant="outline" className="px-3 py-1">
              Generating Itinerary
            </Badge>
          </div>
        </nav>

        <div className="pt-24 pb-12 px-6">
          <div className="container mx-auto max-w-6xl">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center justify-center py-24"
            >
              <Card className="w-full max-w-md">
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center space-y-6">
                    <div className="relative">
                      <Loader2 className="h-16 w-16 text-sky-500 animate-spin" />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Globe className="h-8 w-8 text-sky-600" />
                      </div>
                    </div>
                    
                    <div className="text-center space-y-2">
                      <h3 className="text-xl font-semibold">Generating Your Itinerary</h3>
                      <p className="text-gray-500">Our AI is creating a personalized travel plan</p>
                    </div>

                    <div className="w-full space-y-3">
                      <div className="flex items-center gap-3">
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="text-sm text-gray-600">Documents analyzed</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="text-sm text-gray-600">Travel details extracted</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Loader2 className="h-3 w-3 text-sky-500 animate-spin" />
                        <span className="text-sm text-gray-600">Creating your itinerary...</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
        <div className="container mx-auto px-6 py-24">
          <Alert className="max-w-md mx-auto">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {error}
              <div className="mt-4">
                <Link href="/upload">
                  <Button size="sm">Start Over</Button>
                </Link>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  if (!itinerary) return null;

  const { trip_summary, flights, accommodations, daily_schedule, important_info } = itinerary.itinerary || {};
  const { recommendations } = itinerary;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link href="/summary">
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
            {!hasPreferences && (
              <Link href={`/preferences-consolidated?tripId=${tripId}`}>
                <Button variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Personalize
                </Button>
              </Link>
            )}
            {hasPreferences && (
              <Button
                onClick={() => window.location.reload()}
                variant="outline"
                size="sm"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            )}
            <Button
              onClick={() => {
                localStorage.setItem(`trip_${tripId}`, JSON.stringify({ itinerary, enhancedGuide }));
                alert("Trip saved locally!");
              }}
              variant="outline"
              size="sm"
            >
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
            <Button
              onClick={handleGeneratePdf}
              disabled={generatingPdf || !itinerary}
              className="bg-gradient-to-r from-sky-500 to-blue-600"
              size="sm"
            >
              {generatingPdf ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </>
              )}
            </Button>
          </div>
        </div>
      </nav>

      <div className="pt-24 pb-12 px-6">
        <div className="container mx-auto max-w-6xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <Badge className="mb-4 px-4 py-1 bg-gradient-to-r from-sky-500 to-blue-600">
              <Sparkles className="h-3 w-3 mr-1" />
              AI-Generated Itinerary
            </Badge>
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-sky-600 bg-clip-text text-transparent">
              Your {trip_summary?.destination || "Trip"} Adventure
            </h1>
            <p className="text-gray-600 text-lg">
              {trip_summary?.duration || ""} • {formatTravelDate(trip_summary?.start_date)} - {formatTravelDate(trip_summary?.end_date)}
            </p>
          </motion.div>

          {/* Data availability note (no mocks) */}
          {dataAvailabilityNote && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <Alert className="border-yellow-200 bg-yellow-50">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  {dataAvailabilityNote}
                </AlertDescription>
              </Alert>
            </motion.div>
          )}

          {/* Trip Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
          >
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3">
                  <Calendar className="h-8 w-8 text-sky-500" />
                  <div>
                    <p className="text-sm text-gray-500">Duration</p>
                    <p className="font-semibold">{trip_summary?.duration}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3">
                  <MapPin className="h-8 w-8 text-green-500" />
                  <div>
                    <p className="text-sm text-gray-500">Destination</p>
                    <p className="font-semibold">{trip_summary?.destination}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center space-x-3">
                  <Users className="h-8 w-8 text-purple-500" />
                  <div>
                    <p className="text-sm text-gray-500">Travelers</p>
                    <p className="font-semibold">{trip_summary?.total_passengers || 1} {trip_summary?.total_passengers === 1 ? 'Person' : 'People'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Flights */}
          {flights && flights.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-8"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Plane className="h-5 w-5 mr-2 text-sky-500" />
                    Flights
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {flights.map((flight: any, index: number) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <p className="font-semibold text-lg">{flight.flight_number}</p>
                          <p className="text-sm text-gray-500">{flight.airline}</p>
                        </div>
                        <Badge variant="outline">{flight.class}</Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Departure</p>
                          <p className="font-medium">{flight.departure?.airport}</p>
                          <p className="text-sm">{formatTravelDate(flight.departure?.date)}</p>
                          <p className="text-sm">{formatTime(flight.departure?.time)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Arrival</p>
                          <p className="font-medium">{flight.arrival?.airport}</p>
                          <p className="text-sm">{formatTravelDate(flight.arrival?.date)}</p>
                          <p className="text-sm">{formatTime(flight.arrival?.time)}</p>
                        </div>
                      </div>
                      {flight.seat && (
                        <div className="mt-3 pt-3 border-t">
                          <span className="text-sm text-gray-500">Seat: </span>
                          <span className="font-medium">{flight.seat}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Hotels */}
          {accommodations && accommodations.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mb-8"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Hotel className="h-5 w-5 mr-2 text-purple-500" />
                    Accommodations
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {accommodations.map((hotel: any, index: number) => (
                    <div key={index} className="border rounded-lg p-4">
                      <h3 className="font-semibold text-lg mb-2">{hotel.name}</h3>
                      <p className="text-sm text-gray-600 mb-3">{hotel.address}</p>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-500">Check-in</p>
                          <p className="font-medium">{formatTravelDate(hotel.check_in)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Check-out</p>
                          <p className="font-medium">{formatTravelDate(hotel.check_out)}</p>
                        </div>
                      </div>
                      {hotel.confirmation && (
                        <div className="mt-3 pt-3 border-t">
                          <span className="text-sm text-gray-500">Confirmation: </span>
                          <span className="font-mono font-medium">{hotel.confirmation}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Daily Schedule */}
          {daily_schedule && daily_schedule.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mb-8"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Calendar className="h-5 w-5 mr-2 text-green-500" />
                    Daily Schedule
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {daily_schedule.map((day: any, index: number) => (
                      <div key={index} className="border-l-2 border-sky-200 pl-4">
                        <h4 className="font-semibold mb-2">
                          Day {day.day} - {formatTravelDate(day.date)}
                        </h4>
                        <div className="space-y-2">
                          {day.activities?.map((activity: any, actIndex: number) => (
                            <div key={actIndex} className="flex items-start space-x-2">
                              <Clock className="h-4 w-4 text-gray-400 mt-0.5" />
                              <div>
                                {typeof activity === 'object' && activity.time && (
                                  <span className="font-medium text-sm">{activity.time}: </span>
                                )}
                                <span className="text-sm text-gray-600">
                                  {typeof activity === 'string' ? activity : (activity.description || activity)}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Important Information */}
          {important_info && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mb-8"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <AlertTriangle className="h-5 w-5 mr-2 text-yellow-500" />
                    Important Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(important_info).map(([key, value]: [string, any]) => (
                      <div key={key}>
                        <p className="text-sm text-gray-500 capitalize">{key.replace(/_/g, ' ')}</p>
                        <p className="font-medium">
                          {typeof value === 'object' && value !== null 
                            ? (key === 'dates' && value.start && value.end 
                                ? `${value.start} to ${value.end}`
                                : JSON.stringify(value))
                            : value || 'N/A'}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Enhanced Travel Guide Section */}
          {enhancedGuide && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <EnhancedGuideDisplay guide={enhancedGuide} tripId={tripId || ""} />
            </motion.div>
          )}

          {/* Call to Action for Preferences */}
          {!hasPreferences && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="mb-8"
            >
              <Card className="bg-gradient-to-r from-sky-50 to-blue-50 border-sky-200">
                <CardContent className="pt-6">
                  <div className="text-center space-y-4">
                    <Sparkles className="h-12 w-12 text-sky-500 mx-auto" />
                    <h3 className="text-xl font-semibold">Personalize Your Travel Guide</h3>
                    <p className="text-gray-600 max-w-md mx-auto">
                      Get personalized restaurant recommendations, curated attractions, and local events based on your interests and preferences.
                    </p>
                    <Link href={`/preferences-consolidated?tripId=${tripId}`}>
                      <Button className="bg-gradient-to-r from-sky-500 to-blue-600">
                        <Settings className="h-4 w-4 mr-2" />
                        Set Your Preferences
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ItineraryPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ItineraryPageContent />
    </Suspense>
  );
}
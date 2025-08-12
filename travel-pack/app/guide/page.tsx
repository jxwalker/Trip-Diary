"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  MapPin,
  Calendar,
  Cloud,
  Sun,
  CloudRain,
  Hotel,
  Utensils,
  Camera,
  Music,
  Star,
  DollarSign,
  Clock,
  Navigation,
  Download,
  Share2,
  Heart,
  Info,
  Thermometer,
  Wind,
  Droplets,
  Map,
  ChevronRight,
  Sparkles,
  Settings,
  User
} from "lucide-react";

interface WeatherDay {
  date: string;
  temp_high: number;
  temp_low: number;
  condition: string;
  icon: string;
  precipitation: number;
}

interface Restaurant {
  name: string;
  cuisine: string;
  price_range: string;
  rating: number;
  description: string;
  address: string;
  why_recommended: string;
  best_dishes: string[];
  ambiance: string;
}

interface Attraction {
  name: string;
  type: string;
  description: string;
  address: string;
  hours: string;
  price: string;
  tips: string;
  why_visit: string;
}

interface Event {
  name: string;
  date: string;
  venue: string;
  type: string;
  description: string;
  ticket_info: string;
}

export default function TravelGuidePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tripId = searchParams.get("tripId");
  
  const [loading, setLoading] = useState(true);
  const [guide, setGuide] = useState<any>(null);
  const [weather, setWeather] = useState<WeatherDay[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [userPreferences, setUserPreferences] = useState<any>(null);

  useEffect(() => {
    if (!tripId) {
      setError("No trip ID provided");
      setLoading(false);
      return;
    }

    fetchGuide();
  }, [tripId]);

  const fetchGuide = async () => {
    try {
      // First check if we have preferences
      const prefResponse = await fetch(`/api/proxy/preferences/${tripId}`);
      if (prefResponse.ok) {
        const prefs = await prefResponse.json();
        setUserPreferences(prefs);
      }

      // Get the enhanced guide
      const response = await fetch(`/api/proxy/enhanced-guide/${tripId}`);
      
      if (response.status === 404) {
        // Guide not generated yet, redirect to preferences
        router.push(`/preferences?tripId=${tripId}`);
        return;
      }
      
      if (!response.ok) {
        throw new Error(`Failed to load guide: ${response.status}`);
      }
      
      const data = await response.json();
      setGuide(data);
      
      // Fetch weather data
      fetchWeather(data.destination, data.start_date, data.end_date);
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchWeather = async (destination: string, startDate: string, endDate: string) => {
    try {
      const response = await fetch(`/api/proxy/weather?destination=${destination}&start=${startDate}&end=${endDate}`);
      if (response.ok) {
        const data = await response.json();
        setWeather(data.forecast || []);
      }
    } catch (err) {
      console.error("Failed to fetch weather:", err);
    }
  };

  const getWeatherIcon = (condition: string) => {
    const lower = condition.toLowerCase();
    if (lower.includes("rain")) return <CloudRain className="h-6 w-6" />;
    if (lower.includes("cloud")) return <Cloud className="h-6 w-6" />;
    return <Sun className="h-6 w-6 text-yellow-500" />;
  };

  const getPriceSymbol = (range: string) => {
    const count = (range.match(/\$/g) || []).length;
    return "💰".repeat(count || 1);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-6xl mx-auto">
          <Skeleton className="h-64 mb-8" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Skeleton className="h-96" />
            </div>
            <div>
              <Skeleton className="h-64" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !guide) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <Alert className="max-w-md mx-auto">
          <Info className="h-4 w-4" />
          <AlertDescription>
            {error || "Guide not found"}
            <Button 
              onClick={() => router.push(`/preferences?tripId=${tripId}`)}
              className="mt-4 w-full"
            >
              Set Preferences to Generate Guide
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const { itinerary, enhanced_guide, recommendations } = guide;
  const tripSummary = itinerary?.trip_summary || {};
  const hotels = itinerary?.accommodations || [];
  const restaurants = enhanced_guide?.restaurants || [];
  const attractions = enhanced_guide?.attractions || [];
  const events = enhanced_guide?.events || [];

  return (
    <div className="min-h-screen bg-white">
      {/* Magazine-style Header */}
      <div className="relative h-96 bg-gradient-to-br from-blue-600 to-indigo-800 overflow-hidden">
        <div className="absolute inset-0 bg-black/20" />
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative z-10 h-full flex flex-col justify-center items-center text-white text-center px-8"
        >
          <Badge className="mb-4 bg-white/20 backdrop-blur text-white border-white/30">
            Your Personal Travel Guide
          </Badge>
          <h1 className="text-6xl font-bold mb-4">
            {tripSummary.destination}
          </h1>
          <p className="text-xl mb-2">
            {tripSummary.start_date} - {tripSummary.end_date}
          </p>
          <p className="text-lg opacity-90">
            {tripSummary.duration} of curated experiences
          </p>
        </motion.div>

        {/* Decorative elements */}
        <div className="absolute top-10 right-10 opacity-20">
          <MapPin className="h-32 w-32" />
        </div>
        <div className="absolute bottom-10 left-10 opacity-20">
          <Camera className="h-24 w-24" />
        </div>
      </div>

      {/* Weather Strip */}
      {weather.length > 0 && (
        <div className="bg-gray-50 border-y">
          <div className="max-w-6xl mx-auto px-8 py-4">
            <div className="flex items-center gap-6 overflow-x-auto">
              <span className="font-semibold text-gray-700 whitespace-nowrap">Weather Forecast:</span>
              {weather.map((day, idx) => (
                <div key={idx} className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm whitespace-nowrap">
                  {getWeatherIcon(day.condition)}
                  <div className="text-sm">
                    <div className="font-medium">{day.date}</div>
                    <div className="text-gray-500">
                      {day.temp_high}°/{day.temp_low}°
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-8 py-12">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid grid-cols-5 w-full">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="hotels">Hotels</TabsTrigger>
            <TabsTrigger value="dining">Dining</TabsTrigger>
            <TabsTrigger value="attractions">Attractions</TabsTrigger>
            <TabsTrigger value="events">Events</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-yellow-500" />
                  Your Personalized Guide
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose max-w-none">
                  <p className="text-lg text-gray-700 leading-relaxed">
                    {enhanced_guide?.summary || `Welcome to ${tripSummary.destination}! Your personalized travel guide has been crafted based on your preferences and interests.`}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <div className="grid grid-cols-4 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold">{restaurants.length}</p>
                      <p className="text-sm text-gray-500">Restaurants</p>
                    </div>
                    <Utensils className="h-8 w-8 text-orange-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold">{attractions.length}</p>
                      <p className="text-sm text-gray-500">Attractions</p>
                    </div>
                    <Camera className="h-8 w-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold">{events.length}</p>
                      <p className="text-sm text-gray-500">Events</p>
                    </div>
                    <Music className="h-8 w-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-2xl font-bold">{hotels.length}</p>
                      <p className="text-sm text-gray-500">Hotels</p>
                    </div>
                    <Hotel className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Map Preview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Map className="h-5 w-5" />
                  Interactive Map
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <Button onClick={() => window.open(`https://maps.google.com/maps?q=${tripSummary.destination}`, '_blank')}>
                    Open Full Map
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Hotels Tab */}
          <TabsContent value="hotels" className="space-y-6">
            {hotels.map((hotel: any, idx: number) => (
              <Card key={idx} className="overflow-hidden">
                <div className="grid grid-cols-1 md:grid-cols-3">
                  <div className="md:col-span-2 p-6">
                    <h3 className="text-2xl font-bold mb-2">{hotel.name}</h3>
                    <p className="text-gray-600 mb-4 flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {hotel.address}
                    </p>
                    <div className="prose max-w-none">
                      <p className="text-gray-700">
                        {enhanced_guide?.hotel_writeup || `Experience comfort and luxury at ${hotel.name}. This carefully selected accommodation offers the perfect base for your ${tripSummary.destination} adventure.`}
                      </p>
                    </div>
                    <div className="mt-4 flex gap-4 text-sm">
                      <Badge variant="outline">
                        Check-in: {hotel.check_in}
                      </Badge>
                      <Badge variant="outline">
                        Check-out: {hotel.check_out}
                      </Badge>
                    </div>
                  </div>
                  <div className="bg-gray-50 p-6">
                    <h4 className="font-semibold mb-3">Amenities</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• Free WiFi</li>
                      <li>• Fitness Center</li>
                      <li>• Restaurant & Bar</li>
                      <li>• Concierge Service</li>
                    </ul>
                  </div>
                </div>
              </Card>
            ))}
          </TabsContent>

          {/* Dining Tab */}
          <TabsContent value="dining" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {restaurants.map((restaurant: any, idx: number) => (
                <Card key={idx} className="overflow-hidden hover:shadow-lg transition-shadow">
                  <CardHeader className="bg-gradient-to-r from-orange-50 to-red-50">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-xl">{restaurant.name}</CardTitle>
                        <p className="text-sm text-gray-600 mt-1">{restaurant.cuisine}</p>
                      </div>
                      <Badge className="bg-white">
                        {restaurant.price_range || "$$$"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <p className="text-gray-700 mb-3">
                      {restaurant.description}
                    </p>
                    <div className="text-sm text-gray-600 mb-3">
                      <p className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {restaurant.address}
                      </p>
                    </div>
                    {restaurant.why_recommended && (
                      <div className="bg-blue-50 p-3 rounded-lg">
                        <p className="text-sm font-medium text-blue-900">Why we recommend it:</p>
                        <p className="text-sm text-blue-700">{restaurant.why_recommended}</p>
                      </div>
                    )}
                    {restaurant.best_dishes && restaurant.best_dishes.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm font-medium">Must-try dishes:</p>
                        <p className="text-sm text-gray-600">{restaurant.best_dishes.join(", ")}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Attractions Tab */}
          <TabsContent value="attractions" className="space-y-6">
            {attractions.map((attraction: any, idx: number) => (
              <Card key={idx}>
                <CardContent className="pt-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="md:col-span-2">
                      <h3 className="text-xl font-bold mb-2">{attraction.name}</h3>
                      <Badge className="mb-3">{attraction.type}</Badge>
                      <p className="text-gray-700 mb-3">
                        {attraction.description}
                      </p>
                      {attraction.why_visit && (
                        <div className="bg-green-50 p-3 rounded-lg mb-3">
                          <p className="text-sm font-medium text-green-900">Why visit:</p>
                          <p className="text-sm text-green-700">{attraction.why_visit}</p>
                        </div>
                      )}
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-semibold mb-3">Visitor Info</h4>
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="text-gray-500">Address:</span>
                          <p className="font-medium">{attraction.address}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Hours:</span>
                          <p className="font-medium">{attraction.hours || "Check website"}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Price:</span>
                          <p className="font-medium">{attraction.price || "Varies"}</p>
                        </div>
                        {attraction.tips && (
                          <div className="pt-2 border-t">
                            <span className="text-gray-500">Tips:</span>
                            <p className="font-medium">{attraction.tips}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* Events Tab */}
          <TabsContent value="events" className="space-y-6">
            {events.length > 0 ? (
              events.map((event: any, idx: number) => (
                <Card key={idx}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle>{event.name}</CardTitle>
                        <p className="text-sm text-gray-600 mt-1">
                          {event.date} at {event.venue}
                        </p>
                      </div>
                      <Badge variant="outline">{event.type}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700 mb-3">{event.description}</p>
                    {event.ticket_info && (
                      <Alert>
                        <Info className="h-4 w-4" />
                        <AlertDescription>
                          {event.ticket_info}
                        </AlertDescription>
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="pt-6 text-center">
                  <Music className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No events found for your travel dates</p>
                  <p className="text-sm text-gray-400 mt-1">Check back closer to your trip for updates</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        {/* Action Bar */}
        <div className="mt-12 flex justify-center gap-4">
          <Button
            size="lg"
            className="bg-gradient-to-r from-blue-500 to-indigo-600"
            onClick={() => window.print()}
          >
            <Download className="h-5 w-5 mr-2" />
            Download Guide
          </Button>
          <Button
            size="lg"
            variant="outline"
          >
            <Share2 className="h-5 w-5 mr-2" />
            Share
          </Button>
          <Button
            size="lg"
            variant="outline"
            onClick={() => router.push(`/preferences?tripId=${tripId}`)}
          >
            <Settings className="h-5 w-5 mr-2" />
            Update Preferences
          </Button>
        </div>
      </div>
    </div>
  );
}
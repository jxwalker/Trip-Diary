"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { 
  MapPin,
  Calendar,
  Clock,
  DollarSign,
  Users,
  Star,
  ExternalLink,
  Navigation,
  Phone,
  Globe,
  ChevronDown,
  ChevronRight,
  Utensils,
  Camera,
  Hotel,
  Music,
  Sun,
  Cloud,
  CloudRain,
  Info,
  Download,
  Share2,
  Settings,
  Heart,
  BookOpen,
  Ticket,
  ShoppingBag,
  Coffee,
  Wine,
  Map,
  Filter,
  Search,
  Bookmark,
  Check,
  X,
  AlertCircle,
  ArrowRight,
  Sparkles,
  TrendingUp
} from "lucide-react";
import { cn } from "@/lib/utils";

interface GuideData {
  itinerary: any;
  enhanced_guide: any;
  recommendations: any;
}

export default function ModernGuidePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId");
  
  const [guide, setGuide] = useState<GuideData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedDay, setSelectedDay] = useState(0);
  const [bookmarkedItems, setBookmarkedItems] = useState<Set<string>>(new Set());
  const [filterPrice, setFilterPrice] = useState<string[]>([]);
  const [filterCategory, setFilterCategory] = useState<string[]>([]);
  const [showOnlyBookmarked, setShowOnlyBookmarked] = useState(false);

  useEffect(() => {
    if (tripId) {
      fetchGuide();
    }
  }, [tripId]);

  const fetchGuide = async () => {
    try {
      const response = await fetch(`/api/proxy/enhanced-guide/${tripId}`);
      
      if (response.status === 404) {
        router.push(`/preferences-modern?tripId=${tripId}`);
        return;
      }
      
      if (!response.ok) {
        throw new Error(`Failed to load guide: ${response.status}`);
      }
      
      const data = await response.json();
      setGuide(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleBookmark = (itemId: string) => {
    setBookmarkedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  const openBookingUrl = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const getPriceSymbol = (range: string) => {
    return range || "$$";
  };

  const getWeatherIcon = (condition: string) => {
    const lower = condition?.toLowerCase() || "";
    if (lower.includes("rain")) return <CloudRain className="h-5 w-5" />;
    if (lower.includes("cloud")) return <Cloud className="h-5 w-5" />;
    return <Sun className="h-5 w-5 text-yellow-500" />;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-sky-50 p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          <Skeleton className="h-48" />
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
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-sky-50 p-8">
        <Alert className="max-w-md mx-auto">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || "Guide not found"}
            <Button 
              onClick={() => router.push(`/preferences-modern?tripId=${tripId}`)}
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
  const dailyItinerary = enhanced_guide?.daily_itinerary || [];

  // Filter functions
  const filterByPrice = (items: any[], priceKey: string = "price_range") => {
    if (filterPrice.length === 0) return items;
    return items.filter(item => filterPrice.includes(item[priceKey]));
  };

  const filterByBookmark = (items: any[]) => {
    if (!showOnlyBookmarked) return items;
    return items.filter(item => bookmarkedItems.has(item.name));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Modern Header */}
      <div className="bg-white/90 backdrop-blur-md border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
                {tripSummary.destination}
              </h1>
              <p className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                <Calendar className="h-3 w-3" />
                {tripSummary.start_date} - {tripSummary.end_date}
                <Badge variant="outline" className="ml-2">
                  {tripSummary.duration}
                </Badge>
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowOnlyBookmarked(!showOnlyBookmarked)}
                className={cn(showOnlyBookmarked && "bg-yellow-50 border-yellow-400")}
              >
                <Bookmark className={cn("h-4 w-4", showOnlyBookmarked && "fill-yellow-500")} />
                <span className="ml-2 hidden sm:inline">
                  {bookmarkedItems.size > 0 && `(${bookmarkedItems.size})`}
                </span>
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.print()}
              >
                <Download className="h-4 w-4" />
              </Button>
              
              <Button
                variant="outline"
                size="sm"
              >
                <Share2 className="h-4 w-4" />
              </Button>
              
              <Button
                size="sm"
                className="bg-gradient-to-r from-sky-500 to-blue-600"
                onClick={() => router.push(`/preferences-modern?tripId=${tripId}`)}
              >
                <Settings className="h-4 w-4" />
                <span className="ml-2 hidden sm:inline">Preferences</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-3">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-5 mb-6">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
                <TabsTrigger value="dining">Dining</TabsTrigger>
                <TabsTrigger value="attractions">Explore</TabsTrigger>
                <TabsTrigger value="stay">Stay</TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-6">
                {/* Trip Highlights */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Sparkles className="h-5 w-5 text-yellow-500" />
                      Trip Highlights
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-red-50 rounded-lg">
                        <Utensils className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                        <div className="text-2xl font-bold">{restaurants.length}</div>
                        <div className="text-sm text-gray-600">Restaurants</div>
                      </div>
                      <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg">
                        <Camera className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                        <div className="text-2xl font-bold">{attractions.length}</div>
                        <div className="text-sm text-gray-600">Attractions</div>
                      </div>
                      <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
                        <Music className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                        <div className="text-2xl font-bold">{events.length}</div>
                        <div className="text-sm text-gray-600">Events</div>
                      </div>
                      <div className="text-center p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg">
                        <Hotel className="h-8 w-8 text-green-500 mx-auto mb-2" />
                        <div className="text-2xl font-bold">{hotels.length}</div>
                        <div className="text-sm text-gray-600">Hotels</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Interactive Map */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Map className="h-5 w-5" />
                      Interactive Map
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64 bg-gradient-to-br from-blue-50 to-sky-50 rounded-lg flex items-center justify-center">
                      <Button
                        onClick={() => openBookingUrl(`https://maps.google.com/maps?q=${tripSummary.destination}`)}
                        className="bg-gradient-to-r from-sky-500 to-blue-600"
                      >
                        <Map className="h-4 w-4 mr-2" />
                        Open Full Map
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Top Recommendations */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-green-500" />
                      Top Recommendations
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {restaurants.slice(0, 3).map((restaurant: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-medium">{restaurant.name}</h4>
                            <Badge variant="outline">{restaurant.cuisine}</Badge>
                            <Badge variant="outline">{restaurant.price_range}</Badge>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{restaurant.address}</p>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => toggleBookmark(restaurant.name)}
                          >
                            <Bookmark className={cn(
                              "h-4 w-4",
                              bookmarkedItems.has(restaurant.name) && "fill-yellow-500"
                            )} />
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => openBookingUrl(
                              restaurant.booking_urls?.opentable || 
                              `https://www.opentable.com/s?term=${encodeURIComponent(restaurant.name)}`
                            )}
                          >
                            Book Now
                          </Button>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Daily Itinerary Tab */}
              <TabsContent value="itinerary" className="space-y-6">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Daily Schedule</CardTitle>
                      <div className="flex gap-2">
                        {dailyItinerary.map((_: any, idx: number) => (
                          <Button
                            key={idx}
                            size="sm"
                            variant={selectedDay === idx ? "default" : "outline"}
                            onClick={() => setSelectedDay(idx)}
                          >
                            Day {idx + 1}
                          </Button>
                        ))}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {dailyItinerary[selectedDay] && (
                      <div className="space-y-4">
                        <div className="font-medium text-lg">
                          {dailyItinerary[selectedDay].date} - {dailyItinerary[selectedDay].theme}
                        </div>
                        
                        <div className="space-y-3">
                          {dailyItinerary[selectedDay].activities?.map((activity: any, idx: number) => (
                            <motion.div
                              key={idx}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: idx * 0.1 }}
                              className="flex gap-4 p-4 bg-white rounded-lg border"
                            >
                              <div className="flex-shrink-0">
                                <div className="w-12 h-12 bg-gradient-to-br from-sky-100 to-blue-100 rounded-full flex items-center justify-center">
                                  <Clock className="h-5 w-5 text-sky-600" />
                                </div>
                              </div>
                              <div className="flex-1">
                                <div className="flex items-start justify-between">
                                  <div>
                                    <div className="flex items-center gap-2">
                                      <h4 className="font-medium">{activity.time}</h4>
                                      <Badge variant="outline" className="text-xs">
                                        {activity.duration || "1-2 hours"}
                                      </Badge>
                                    </div>
                                    <h3 className="text-lg font-semibold mt-1">{activity.name}</h3>
                                    <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
                                    {activity.address && (
                                      <p className="text-sm text-gray-500 mt-2 flex items-center gap-1">
                                        <MapPin className="h-3 w-3" />
                                        {activity.address}
                                      </p>
                                    )}
                                    {activity.tips && (
                                      <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-900">
                                        <Info className="h-3 w-3 inline mr-1" />
                                        {activity.tips}
                                      </div>
                                    )}
                                  </div>
                                  <div className="flex flex-col gap-2">
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      onClick={() => toggleBookmark(`${activity.name}-${idx}`)}
                                    >
                                      <Bookmark className={cn(
                                        "h-4 w-4",
                                        bookmarkedItems.has(`${activity.name}-${idx}`) && "fill-yellow-500"
                                      )} />
                                    </Button>
                                    {activity.booking_url && (
                                      <Button
                                        size="sm"
                                        onClick={() => openBookingUrl(activity.booking_url)}
                                      >
                                        Book
                                      </Button>
                                    )}
                                    {activity.map_url && (
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => openBookingUrl(activity.map_url)}
                                      >
                                        <Navigation className="h-4 w-4" />
                                      </Button>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Dining Tab */}
              <TabsContent value="dining" className="space-y-6">
                {/* Filter Bar */}
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex flex-wrap gap-2">
                      <Badge 
                        variant="outline" 
                        className="cursor-pointer"
                        onClick={() => setFilterPrice([])}
                      >
                        All Prices
                      </Badge>
                      {["$", "$$", "$$$", "$$$$"].map(price => (
                        <Badge
                          key={price}
                          variant={filterPrice.includes(price) ? "default" : "outline"}
                          className="cursor-pointer"
                          onClick={() => {
                            setFilterPrice(prev => 
                              prev.includes(price) 
                                ? prev.filter(p => p !== price)
                                : [...prev, price]
                            );
                          }}
                        >
                          {price}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Restaurant Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filterByBookmark(filterByPrice(restaurants)).map((restaurant: any, idx: number) => (
                    <Card key={idx} className="overflow-hidden hover:shadow-lg transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg flex items-center gap-2">
                              {restaurant.name}
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => toggleBookmark(restaurant.name)}
                                className="h-6 w-6 p-0"
                              >
                                <Bookmark className={cn(
                                  "h-4 w-4",
                                  bookmarkedItems.has(restaurant.name) && "fill-yellow-500 text-yellow-500"
                                )} />
                              </Button>
                            </CardTitle>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="secondary">{restaurant.cuisine}</Badge>
                              <Badge variant="outline">{restaurant.price_range}</Badge>
                              {restaurant.rating && (
                                <div className="flex items-center gap-1">
                                  <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                                  <span className="text-sm">{restaurant.rating}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-gray-600">
                          {restaurant.description}
                        </p>
                        
                        <div className="text-sm text-gray-500 flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {restaurant.address}
                        </div>
                        
                        {restaurant.why_recommended && (
                          <div className="p-2 bg-green-50 rounded text-sm">
                            <span className="font-medium text-green-900">Why we recommend: </span>
                            <span className="text-green-700">{restaurant.why_recommended}</span>
                          </div>
                        )}
                        
                        {restaurant.best_dishes && restaurant.best_dishes.length > 0 && (
                          <div className="text-sm">
                            <span className="font-medium">Must try: </span>
                            {restaurant.best_dishes.join(", ")}
                          </div>
                        )}
                        
                        <Separator />
                        
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            className="flex-1"
                            onClick={() => openBookingUrl(
                              restaurant.booking_urls?.opentable || 
                              restaurant.primary_booking_url ||
                              `https://www.opentable.com/s?term=${encodeURIComponent(restaurant.name)}`
                            )}
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            Reserve Table
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => openBookingUrl(
                              restaurant.map_url ||
                              restaurant.booking_urls?.google_maps ||
                              `https://maps.google.com/maps?q=${encodeURIComponent(restaurant.name + " " + restaurant.address)}`
                            )}
                          >
                            <Navigation className="h-3 w-3" />
                          </Button>
                          {restaurant.booking_urls?.yelp && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => openBookingUrl(restaurant.booking_urls.yelp)}
                            >
                              Reviews
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              {/* Attractions Tab */}
              <TabsContent value="attractions" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filterByBookmark(attractions).map((attraction: any, idx: number) => (
                    <Card key={idx}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg flex items-center gap-2">
                              {attraction.name}
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => toggleBookmark(attraction.name)}
                                className="h-6 w-6 p-0"
                              >
                                <Bookmark className={cn(
                                  "h-4 w-4",
                                  bookmarkedItems.has(attraction.name) && "fill-yellow-500 text-yellow-500"
                                )} />
                              </Button>
                            </CardTitle>
                            <Badge variant="secondary" className="mt-1">
                              {attraction.type}
                            </Badge>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-gray-600">
                          {attraction.description}
                        </p>
                        
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-1 text-gray-500">
                            <MapPin className="h-3 w-3" />
                            {attraction.address}
                          </div>
                          {attraction.hours && (
                            <div className="flex items-center gap-1 text-gray-500">
                              <Clock className="h-3 w-3" />
                              {attraction.hours}
                            </div>
                          )}
                          {attraction.price && (
                            <div className="flex items-center gap-1 text-gray-500">
                              <DollarSign className="h-3 w-3" />
                              {attraction.price}
                            </div>
                          )}
                          {attraction.visit_duration && (
                            <div className="flex items-center gap-1 text-gray-500">
                              <Clock className="h-3 w-3" />
                              Suggested duration: {attraction.visit_duration}
                            </div>
                          )}
                        </div>
                        
                        {attraction.why_visit && (
                          <div className="p-2 bg-blue-50 rounded text-sm">
                            <span className="font-medium text-blue-900">Why visit: </span>
                            <span className="text-blue-700">{attraction.why_visit}</span>
                          </div>
                        )}
                        
                        {attraction.tips && (
                          <div className="p-2 bg-amber-50 rounded text-sm">
                            <span className="font-medium text-amber-900">Tip: </span>
                            <span className="text-amber-700">{attraction.tips}</span>
                          </div>
                        )}
                        
                        <Separator />
                        
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            className="flex-1"
                            onClick={() => openBookingUrl(
                              attraction.booking_urls?.viator ||
                              attraction.primary_booking_url ||
                              `https://www.viator.com/searchResults/all?text=${encodeURIComponent(attraction.name)}`
                            )}
                          >
                            <Ticket className="h-3 w-3 mr-1" />
                            Get Tickets
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => openBookingUrl(
                              attraction.map_url ||
                              attraction.booking_urls?.google_maps ||
                              `https://maps.google.com/maps?q=${encodeURIComponent(attraction.name + " " + attraction.address)}`
                            )}
                          >
                            <Navigation className="h-3 w-3" />
                          </Button>
                          {attraction.booking_urls?.tripadvisor && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => openBookingUrl(attraction.booking_urls.tripadvisor)}
                            >
                              Reviews
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Events Section */}
                {events.length > 0 && (
                  <>
                    <Separator />
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                      <Music className="h-5 w-5" />
                      Events During Your Stay
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {events.map((event: any, idx: number) => (
                        <Card key={idx}>
                          <CardHeader>
                            <CardTitle className="text-lg">{event.name}</CardTitle>
                            <CardDescription>
                              {event.date} at {event.venue}
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="space-y-3">
                            <p className="text-sm text-gray-600">{event.description}</p>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                onClick={() => openBookingUrl(
                                  event.ticket_urls?.ticketmaster ||
                                  event.primary_ticket_url ||
                                  `https://www.ticketmaster.com/search?q=${encodeURIComponent(event.name)}`
                                )}
                              >
                                <Ticket className="h-3 w-3 mr-1" />
                                Get Tickets
                              </Button>
                              {event.venue_info_url && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => openBookingUrl(event.venue_info_url)}
                                >
                                  Venue Info
                                </Button>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </>
                )}
              </TabsContent>

              {/* Hotels Tab */}
              <TabsContent value="stay" className="space-y-6">
                {hotels.map((hotel: any, idx: number) => (
                  <Card key={idx}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle>{hotel.name}</CardTitle>
                          <CardDescription className="flex items-center gap-1 mt-2">
                            <MapPin className="h-3 w-3" />
                            {hotel.address}
                          </CardDescription>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => toggleBookmark(hotel.name)}
                        >
                          <Bookmark className={cn(
                            "h-4 w-4",
                            bookmarkedItems.has(hotel.name) && "fill-yellow-500 text-yellow-500"
                          )} />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="md:col-span-2 space-y-3">
                          <p className="text-gray-600">
                            {enhanced_guide?.hotel_writeup || 
                             `Experience comfort at ${hotel.name}. This carefully selected accommodation offers the perfect base for your ${tripSummary.destination} adventure.`}
                          </p>
                          
                          <div className="flex gap-4 text-sm">
                            <Badge variant="outline" className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              Check-in: {hotel.check_in}
                            </Badge>
                            <Badge variant="outline" className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              Check-out: {hotel.check_out}
                            </Badge>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <h4 className="font-medium text-sm">Amenities</h4>
                          <div className="space-y-1 text-sm text-gray-600">
                            <div>• Free WiFi</div>
                            <div>• Fitness Center</div>
                            <div>• Restaurant & Bar</div>
                            <div>• Concierge Service</div>
                          </div>
                        </div>
                      </div>
                      
                      <Separator className="my-4" />
                      
                      <div className="flex gap-2">
                        <Button
                          className="flex-1"
                          onClick={() => openBookingUrl(
                            hotel.booking_urls?.booking_com ||
                            hotel.primary_booking_url ||
                            `https://www.booking.com/search.html?ss=${encodeURIComponent(hotel.name)}`
                          )}
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          Book on Booking.com
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => openBookingUrl(
                            hotel.compare_prices_url ||
                            hotel.booking_urls?.google_hotels ||
                            `https://www.google.com/travel/hotels/search?q=${encodeURIComponent(hotel.name)}`
                          )}
                        >
                          Compare Prices
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => openBookingUrl(
                            hotel.map_url ||
                            `https://maps.google.com/maps?q=${encodeURIComponent(hotel.name + " " + hotel.address)}`
                          )}
                        >
                          <Navigation className="h-3 w-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button className="w-full justify-start" variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </Button>
                <Button className="w-full justify-start" variant="outline" size="sm">
                  <Share2 className="h-4 w-4 mr-2" />
                  Share Trip
                </Button>
                <Button className="w-full justify-start" variant="outline" size="sm">
                  <Settings className="h-4 w-4 mr-2" />
                  Edit Preferences
                </Button>
              </CardContent>
            </Card>

            {/* Bookmarked Items */}
            {bookmarkedItems.size > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Bookmark className="h-4 w-4 fill-yellow-500 text-yellow-500" />
                    Saved Items ({bookmarkedItems.size})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-48">
                    <div className="space-y-2">
                      {Array.from(bookmarkedItems).map(item => (
                        <div key={item} className="text-sm p-2 bg-gray-50 rounded flex items-center justify-between">
                          <span className="truncate">{item}</span>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-6 w-6 p-0"
                            onClick={() => toggleBookmark(item)}
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            )}

            {/* Weather */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Weather Forecast</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {[1, 2, 3].map(day => (
                    <div key={day} className="flex items-center justify-between text-sm">
                      <span>Day {day}</span>
                      <div className="flex items-center gap-2">
                        <Sun className="h-4 w-4 text-yellow-500" />
                        <span>72°F</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Local Tips</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex gap-2">
                    <Info className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    <span>Best time for museums: Weekday mornings</span>
                  </div>
                  <div className="flex gap-2">
                    <Info className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    <span>Book restaurants 2-3 days in advance</span>
                  </div>
                  <div className="flex gap-2">
                    <Info className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    <span>Use public transport for city center</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
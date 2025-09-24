"use client";

import { Suspense } from "react";
import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import "./guide-styles.css";
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
  Ticket,
  Map,
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
  itinerary: {
    trip_summary?: {
      destination?: string;
      start_date?: string;
      end_date?: string;
      duration?: string;
    };
    accommodations?: Array<{
      name: string;
      address: string;
      check_in: string;
      check_out: string;
      booking_urls?: {
        booking_com?: string;
        google_hotels?: string;
      };
      primary_booking_url?: string;
      compare_prices_url?: string;
      map_url?: string;
    }>;
  };
  enhanced_guide: {
    restaurants?: Array<{
      name: string;
      cuisine: string;
      price_range: string;
      rating?: number;
      description: string;
      address: string;
      why_recommended?: string;
      best_dishes?: string[];
      booking_urls?: {
        opentable?: string;
        google_maps?: string;
        yelp?: string;
      };
      primary_booking_url?: string;
      map_url?: string;
    }>;
    attractions?: Array<{
      name: string;
      type: string;
      description: string;
      address: string;
      hours?: string;
      price?: string;
      tips?: string;
      why_visit?: string;
      visit_duration?: string;
      booking_urls?: {
        viator?: string;
        google_maps?: string;
        tripadvisor?: string;
      };
      primary_booking_url?: string;
      map_url?: string;
    }>;
    events?: Array<{
      name: string;
      date: string;
      venue: string;
      type: string;
      description: string;
      ticket_info?: string;
      ticket_urls?: {
        ticketmaster?: string;
      };
      primary_ticket_url?: string;
      venue_info_url?: string;
    }>;
    daily_itinerary?: Array<{
      date: string;
      theme: string;
      activities?: Array<{
        name: string;
        time: string;
        duration?: string;
        description: string;
        address?: string;
        tips?: string;
        booking_url?: string;
        map_url?: string;
      }>;
    }>;
    hotel_writeup?: string;
  };
  recommendations: unknown;
}

function ModernGuidePageContent() {
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
  const [showOnlyBookmarked, setShowOnlyBookmarked] = useState(false);

  useEffect(() => {
    if (tripId) {
      fetchGuide();
    }
  }, [tripId, router]);

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
      // The API returns { guide: {...}, status: "success", ... }
      // We need the guide object itself
      setGuide(data.guide || data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "An error occurred");
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

  const handleDownloadPDF = async () => {
    try {
      if (!tripId) throw new Error('Missing tripId');
      const res = await fetch(`/api/proxy/generate-pdf/${tripId}`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to generate/download PDF');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `travel_pack_${tripId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('PDF download error:', error);
      alert('Failed to download PDF. Please try again.');
    }
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

  const restaurants = (guide as any)?.restaurants || [];
  const attractions = (guide as any)?.attractions || [];
  const events = (guide as any)?.events || [];
  const dailyItinerary = (guide as any)?.daily_itinerary || [];
  const summaryText = (guide as any)?.summary as string | undefined;
  const destinationInsights = (guide as any)?.destination_insights as string | undefined;
  const neighborhoods = (guide as any)?.neighborhoods as Array<any> || [];
  const practicalInfo = (guide as any)?.practical_info as Record<string, any> || {};
  const hiddenGems = (guide as any)?.hidden_gems as Array<any> || [];
  const citations = (guide as any)?.citations as Array<any> || [];
  const weather = (guide as any)?.weather || [];
  
  const tripSummary = {
    destination: "Paris", // Default from our test data
    start_date: "March 15, 2025",
    end_date: "March 22, 2025", 
    duration: "7 days"
  };
  const hotels = [];

  // Filter functions
  const filterByPrice = (items: Array<Record<string, unknown>>, priceKey: string = "price_range") => {
    if (filterPrice.length === 0) return items;
    return items.filter(item => filterPrice.includes(String(item[priceKey])));
  };

  const filterByBookmark = (items: Array<{ name: string }>) => {
    if (!showOnlyBookmarked) return items;
    return items.filter(item => bookmarkedItems.has(item.name));
  };

  return (
    <div className="guide-container min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Magazine-Quality Header */}
      <div className="guide-header bg-white/95 backdrop-blur-xl border-b sticky top-0 z-40 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="text-center flex-1">
              <h1 className="guide-title text-4xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                {tripSummary.destination}
              </h1>
              <p className="guide-subtitle text-lg text-gray-600 flex items-center justify-center gap-3 mt-2">
                <Calendar className="h-5 w-5 text-purple-500" />
                <span className="font-medium">{tripSummary.start_date} - {tripSummary.end_date}</span>
                <Badge variant="outline" className="ml-2 bg-gradient-to-r from-purple-100 to-blue-100 border-purple-300 text-purple-700 font-semibold">
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
              <TabsList className="grid w-full grid-cols-7 mb-6">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="guide">Guide</TabsTrigger>
                <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
                <TabsTrigger value="dining">Dining</TabsTrigger>
                <TabsTrigger value="attractions">Explore</TabsTrigger>
                <TabsTrigger value="stay">Stay</TabsTrigger>
                <TabsTrigger value="sources">Sources</TabsTrigger>
              </TabsList>
              {/* Magazine-Style Guide Tab */}
              <TabsContent value="guide" className="space-y-8">
                {/* Glossy Cover */}
                <div className="relative overflow-hidden rounded-xl border bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 text-white">
                  {/* Optional hero background via static maps/imagery if available later */}
                  <div className="p-8 md:p-12">
                    <div className="mb-3 text-xs uppercase tracking-widest text-blue-200">Conde Nast–style Guide</div>
                    <h2 className="text-3xl md:text-5xl font-semibold leading-tight">
                      {tripSummary.destination}
                    </h2>
                    <p className="mt-2 text-blue-200 flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>{tripSummary.start_date} – {tripSummary.end_date}</span>
                      {tripSummary.duration && (
                        <Badge variant="secondary" className="ml-2 bg-white/10 text-white border-white/20">
                          {tripSummary.duration}
                        </Badge>
                      )}
                    </p>
                    {summaryText && (
                      <p className="mt-6 max-w-3xl text-blue-100/90">
                        {summaryText.split("\n")[0]}
                      </p>
                    )}
                  </div>
                </div>

                {/* Executive Summary */}
                {summaryText && (
                  <section id="summary" className="bg-white rounded-xl border p-6 md:p-8">
                    <h3 className="text-xl font-semibold mb-3">Executive Summary</h3>
                    <p className="text-gray-700 leading-relaxed first-letter:text-5xl first-letter:font-bold first-letter:mr-2 first-letter:float-left">
                      {summaryText}
                    </p>
                  </section>
                )}

                {/* Destination Insights */}
                {destinationInsights && (
                  <section id="insights" className="bg-white rounded-xl border p-6 md:p-8">
                    <h3 className="text-xl font-semibold mb-3">Destination Insights</h3>
                    <div className="space-y-4 text-gray-700 leading-relaxed">
                      {destinationInsights.split("\n").map((para, idx) => (
                        <p key={idx}>{para}</p>
                      ))}
                    </div>
                  </section>
                )}

                {/* Hidden Gems */}
                {hiddenGems.length > 0 && (
                  <section id="gems" className="bg-white rounded-xl border p-6 md:p-8">
                    <h3 className="text-xl font-semibold mb-4">Hidden Gems & Local Secrets</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {hiddenGems.map((gem: any, idx: number) => (
                        <div key={idx} className="p-4 rounded-lg border hover:shadow-sm transition-shadow">
                          <div className="text-sm text-gray-600">Discovery #{idx + 1}</div>
                          <p className="mt-1 text-gray-800">{gem?.description || gem?.name || String(gem)}</p>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {/* Neighborhoods */}
                {neighborhoods.length > 0 && (
                  <section id="neighborhoods" className="bg-white rounded-xl border p-6 md:p-8">
                    <h3 className="text-xl font-semibold mb-4">Neighborhood Guide</h3>
                    <div className="space-y-6">
                      {neighborhoods.map((n, idx) => (
                        <div key={idx} className="border rounded-lg p-4">
                          <h4 className="font-medium text-lg">{(n as any).name || `Area ${idx + 1}`}</h4>
                          {(n as any).description && (
                            <p className="text-gray-700 mt-1">{(n as any).description}</p>
                          )}
                          {Array.isArray((n as any).highlights) && (n as any).highlights.length > 0 && (
                            <ul className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-700 list-disc pl-5">
                              {(n as any).highlights.map((h: string, i: number) => (
                                <li key={i}>{h}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {/* Practical Information */}
                {Object.keys(practicalInfo).length > 0 && (
                  <section id="practical" className="bg-white rounded-xl border p-6 md:p-8">
                    <h3 className="text-xl font-semibold mb-4">Practical Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(practicalInfo).map(([category, items]) => (
                        Array.isArray(items) && items.length > 0 ? (
                          <div key={category} className="p-4 rounded-lg border">
                            <h4 className="font-medium mb-2 capitalize">{category.replace(/_/g, ' ')}</h4>
                            <ul className="list-disc pl-5 space-y-1 text-gray-700 text-sm">
                              {items.map((it: string, idx: number) => (
                                <li key={idx}>{it}</li>
                              ))}
                            </ul>
                          </div>
                        ) : null
                      ))}
                    </div>
                  </section>
                )}
              </TabsContent>

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
                    {restaurants.slice(0, 3).map((restaurant, idx: number) => (
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
                        {dailyItinerary.map((_, idx: number) => (
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
                          {dailyItinerary[selectedDay].activities?.map((activity, idx: number) => (
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
                {restaurants.length === 0 ? (
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-center py-8">
                        <Utensils className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Restaurants Found</h3>
                        <p className="text-gray-500 max-w-md mx-auto">
                          We couldn't find restaurant recommendations for your trip yet. 
                          Try adjusting your preferences or check back later as we update our recommendations.
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filterByBookmark(filterByPrice(restaurants as Array<Record<string, unknown>>) as Array<{ name: string }>).map((restaurant, idx: number) => (
                    <Card key={idx} className="overflow-hidden hover:shadow-lg transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg flex items-center gap-2">
                              {(restaurant as any).name}
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => toggleBookmark((restaurant as any).name)}
                                className="h-6 w-6 p-0"
                              >
                                <Bookmark className={cn(
                                  "h-4 w-4",
                                  bookmarkedItems.has((restaurant as any).name) && "fill-yellow-500 text-yellow-500"
                                )} />
                              </Button>
                            </CardTitle>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="secondary">{(restaurant as any).cuisine}</Badge>
                              <Badge variant="outline">{(restaurant as any).price_range}</Badge>
                              {(restaurant as any).rating && (
                                <div className="flex items-center gap-1">
                                  <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                                  <span className="text-sm">{(restaurant as any).rating}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-gray-600">
                          {(restaurant as any).description}
                        </p>
                        
                        <div className="text-sm text-gray-500 flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {(restaurant as any).address}
                        </div>
                        
                        {(restaurant as any).why_recommended && (
                          <div className="p-2 bg-green-50 rounded text-sm">
                            <span className="font-medium text-green-900">Why we recommend: </span>
                            <span className="text-green-700">{(restaurant as any).why_recommended}</span>
                          </div>
                        )}
                        
                        {(restaurant as any).best_dishes && (restaurant as any).best_dishes.length > 0 && (
                          <div className="text-sm">
                            <span className="font-medium">Must try: </span>
                            {(restaurant as any).best_dishes.join(", ")}
                          </div>
                        )}
                        
                        <Separator />
                        
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            className="flex-1"
                            onClick={() => openBookingUrl(
                              (restaurant as any).booking_urls?.opentable || 
                              (restaurant as any).primary_booking_url ||
                              `https://www.opentable.com/s?term=${encodeURIComponent((restaurant as any).name)}`
                            )}
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            Reserve Table
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => openBookingUrl(
                              (restaurant as any).map_url ||
                              (restaurant as any).booking_urls?.google_maps ||
                              `https://maps.google.com/maps?q=${encodeURIComponent((restaurant as any).name + " " + (restaurant as any).address)}`
                            )}
                          >
                            <Navigation className="h-3 w-3" />
                          </Button>
                          {(restaurant as any).booking_urls?.yelp && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => openBookingUrl((restaurant as any).booking_urls.yelp)}
                            >
                              Reviews
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                )}
              </TabsContent>

              {/* Attractions Tab */}
              <TabsContent value="attractions" className="space-y-6">
                {attractions.length === 0 ? (
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-center py-8">
                        <Camera className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Attractions Found</h3>
                        <p className="text-gray-500 max-w-md mx-auto">
                          We haven't discovered any attractions for your destination yet. 
                          This might be because you're visiting a less touristy area or we need more information about your preferences.
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filterByBookmark(attractions).map((attraction, idx: number) => (
                    <Card key={idx}>
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-lg flex items-center gap-2">
                              {(attraction as any).name}
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => toggleBookmark((attraction as any).name)}
                                className="h-6 w-6 p-0"
                              >
                                <Bookmark className={cn(
                                  "h-4 w-4",
                                  bookmarkedItems.has((attraction as any).name) && "fill-yellow-500 text-yellow-500"
                                )} />
                              </Button>
                            </CardTitle>
                            <Badge variant="secondary" className="mt-1">
                              {(attraction as any).type}
                            </Badge>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-gray-600">
                          {(attraction as any).description}
                        </p>
                        
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-1 text-gray-500">
                            <MapPin className="h-3 w-3" />
                            {(attraction as any).address}
                          </div>
                          {(attraction as any).hours && (
                            <div className="flex items-center gap-1 text-gray-500">
                              <Clock className="h-3 w-3" />
                              {(attraction as any).hours}
                            </div>
                          )}
                          {(attraction as any).price && (
                            <div className="flex items-center gap-1 text-gray-500">
                              <DollarSign className="h-3 w-3" />
                              {(attraction as any).price}
                            </div>
                          )}
                          {(attraction as any).visit_duration && (
                            <div className="flex items-center gap-1 text-gray-500">
                              <Clock className="h-3 w-3" />
                              Suggested duration: {(attraction as any).visit_duration}
                            </div>
                          )}
                        </div>
                        
                        {(attraction as any).why_visit && (
                          <div className="p-2 bg-blue-50 rounded text-sm">
                            <span className="font-medium text-blue-900">Why visit: </span>
                            <span className="text-blue-700">{(attraction as any).why_visit}</span>
                          </div>
                        )}
                        
                        {(attraction as any).tips && (
                          <div className="p-2 bg-amber-50 rounded text-sm">
                            <span className="font-medium text-amber-900">Tip: </span>
                            <span className="text-amber-700">{(attraction as any).tips}</span>
                          </div>
                        )}
                        
                        <Separator />
                        
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            className="flex-1"
                            onClick={() => openBookingUrl(
                              (attraction as any).booking_urls?.viator ||
                              (attraction as any).primary_booking_url ||
                              `https://www.viator.com/searchResults/all?text=${encodeURIComponent((attraction as any).name)}`
                            )}
                          >
                            <Ticket className="h-3 w-3 mr-1" />
                            Get Tickets
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => openBookingUrl(
                              (attraction as any).map_url ||
                              (attraction as any).booking_urls?.google_maps ||
                              `https://maps.google.com/maps?q=${encodeURIComponent((attraction as any).name + " " + (attraction as any).address)}`
                            )}
                          >
                            <Navigation className="h-3 w-3" />
                          </Button>
                          {(attraction as any).booking_urls?.tripadvisor && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => openBookingUrl((attraction as any).booking_urls.tripadvisor)}
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
                      {events.map((event, idx: number) => (
                        <Card key={idx}>
                          <CardHeader>
                            <CardTitle className="text-lg">{(event as any).name}</CardTitle>
                            <CardDescription>
                              {(event as any).date} at {(event as any).venue}
                            </CardDescription>
                          </CardHeader>
                          <CardContent className="space-y-3">
                            <p className="text-sm text-gray-600">{(event as any).description}</p>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                onClick={() => openBookingUrl(
                                  (event as any).ticket_urls?.ticketmaster ||
                                  (event as any).primary_ticket_url ||
                                  `https://www.ticketmaster.com/search?q=${encodeURIComponent((event as any).name)}`
                                )}
                              >
                                <Ticket className="h-3 w-3 mr-1" />
                                Get Tickets
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => openBookingUrl(
                                  (event as any).map_url ||
                                  `https://maps.google.com/maps?q=${encodeURIComponent((event as any).venue || (event as any).name)}`
                                )}
                              >
                                <Navigation className="h-3 w-3 mr-1" />
                                Open in Maps
                              </Button>
                              {(event as any).venue_info_url && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => openBookingUrl((event as any).venue_info_url)}
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
                </>
                )}
              </TabsContent>

              {/* Hotels Tab */}
              <TabsContent value="stay" className="space-y-6">
                {hotels.map((hotel, idx: number) => (
                  <Card key={idx}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle>{(hotel as any).name}</CardTitle>
                          <CardDescription className="flex items-center gap-1 mt-2">
                            <MapPin className="h-3 w-3" />
                            {(hotel as any).address}
                          </CardDescription>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => toggleBookmark((hotel as any).name)}
                        >
                          <Bookmark className={cn(
                            "h-4 w-4",
                            bookmarkedItems.has((hotel as any).name) && "fill-yellow-500 text-yellow-500"
                          )} />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="md:col-span-2 space-y-3">
                          <p className="text-gray-600">
                            {(guide as any)?.hotel_writeup || 
                             `Experience comfort at ${(hotel as any).name}. This carefully selected accommodation offers the perfect base for your ${tripSummary.destination} adventure.`}
                          </p>
                          
                          <div className="flex gap-4 text-sm">
                            <Badge variant="outline" className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              Check-in: {(hotel as any).check_in}
                            </Badge>
                            <Badge variant="outline" className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              Check-out: {(hotel as any).check_out}
                            </Badge>
                          </div>
                        </div>
                        
                        {Array.isArray((hotel as any).amenities) && (hotel as any).amenities.length > 0 && (
                          <div className="space-y-2">
                            <h4 className="font-medium text-sm">Amenities</h4>
                            <div className="space-y-1 text-sm text-gray-600">
                              {(hotel as any).amenities.map((a: string, i: number) => (
                                <div key={i}>• {a}</div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <Separator className="my-4" />
                      
                      <div className="flex gap-2">
                        <Button
                          className="flex-1"
                          onClick={() => openBookingUrl(
                            (hotel as any).booking_urls?.booking_com ||
                            (hotel as any).primary_booking_url ||
                            `https://www.booking.com/search.html?ss=${encodeURIComponent((hotel as any).name)}`
                          )}
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          Book Now
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => openBookingUrl(
                            (hotel as any).compare_prices_url ||
                            (hotel as any).booking_urls?.google_hotels ||
                            `https://www.google.com/travel/hotels/search?q=${encodeURIComponent((hotel as any).name)}`
                          )}
                        >
                          Compare Prices
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => openBookingUrl(
                            (hotel as any).map_url ||
                            `https://maps.google.com/maps?q=${encodeURIComponent((hotel as any).name + " " + (hotel as any).address)}`
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
            {/* Guide TOC */}
            {activeTab === 'guide' && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">In this guide</CardTitle>
                </CardHeader>
                <CardContent>
                  <nav className="text-sm space-y-2">
                    {summaryText && (
                      <a href="#summary" className="block text-gray-700 hover:text-sky-700">Executive Summary</a>
                    )}
                    {destinationInsights && (
                      <a href="#insights" className="block text-gray-700 hover:text-sky-700">Destination Insights</a>
                    )}
                    {hiddenGems.length > 0 && (
                      <a href="#gems" className="block text-gray-700 hover:text-sky-700">Hidden Gems</a>
                    )}
                    {neighborhoods.length > 0 && (
                      <a href="#neighborhoods" className="block text-gray-700 hover:text-sky-700">Neighborhoods</a>
                    )}
                    {Object.keys(practicalInfo).length > 0 && (
                      <a href="#practical" className="block text-gray-700 hover:text-sky-700">Practical Info</a>
                    )}
                  </nav>
                </CardContent>
              </Card>
            )}
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button 
                  className="w-full justify-start" 
                  variant="outline" 
                  size="sm"
                  onClick={handleDownloadPDF}
                >
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

            {/* Weather (show only if provided) */}
            {Array.isArray(weather) && weather.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Weather Forecast</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {(weather as Array<any>).map((w, idx) => (
                      <div key={idx} className="flex items-center justify-between text-sm">
                        <span className="font-medium">{w.date || `Day ${idx + 1}`}</span>
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-1">
                            {getWeatherIcon(String(w.condition || ''))}
                            <span className="text-gray-600">{w.description || w.condition || ''}</span>
                          </div>
                          <div className="text-right">
                            <span className="font-medium">{w.temp_high || w.temperature}°</span>
                            {w.temp_low && (
                              <span className="text-gray-500 ml-1">/ {w.temp_low}°</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  {(guide as any)?.weather_summary?.packing_suggestions && (
                    <div className="mt-4 pt-4 border-t">
                      <div className="text-xs font-medium text-gray-600 mb-2">What to Pack:</div>
                      <div className="flex flex-wrap gap-1">
                        {((guide as any).weather_summary.packing_suggestions as string[]).map((item, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {item}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Tips (show only if provided) */}
            {Array.isArray(practicalInfo?.tips) && practicalInfo.tips.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Local Tips</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600">
                    {(practicalInfo.tips as Array<string>).map((tip, idx) => (
                      <div key={idx} className="flex gap-2">
                        <Info className="h-4 w-4 text-blue-500 flex-shrink-0 mt-0.5" />
                        <span>{tip}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === 'sources' && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Sources & Citations</CardTitle>
                </CardHeader>
                <CardContent>
                  {Array.isArray(citations) && citations.length > 0 ? (
                    <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700">
                      {citations.map((c: any, idx: number) => (
                        <li key={idx} className="break-words">
                          <a className="text-sky-700 hover:underline" href={String(c)} target="_blank" rel="noopener noreferrer">{String(c)}</a>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-gray-600">No citations available.</p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ModernGuidePage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ModernGuidePageContent />
    </Suspense>
  );
}

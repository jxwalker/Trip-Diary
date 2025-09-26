"use client";

import { Suspense, useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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
  Sparkles,
  TrendingUp,
  ArrowRight,
  Filter,
  Search,
  Car,
  CreditCard,
  Eye,
  ChefHat,
  Wine,
  Coffee
} from "lucide-react";
import { cn } from "@/lib/utils";

interface GuideData {
  destination?: string;
  dates?: string;
  preferences?: string;
  restaurants?: Array<any>;
  attractions?: Array<any>;
  events?: Array<any>;
  weather?: Array<any>;
  practical_info?: any;
  daily_itinerary?: Array<any>;
  summary?: string;
  destination_insights?: string;
  neighborhoods?: Array<any>;
  hidden_gems?: Array<any>;
  citations?: Array<any>;
}

const HeroSection = ({ destination, dates }: { destination: string; dates: string }) => (
  <motion.div 
    initial={{ opacity: 0 }} 
    animate={{ opacity: 1 }} 
    transition={{ duration: 0.8 }}
    className="relative w-full h-80 md:h-96 lg:h-[500px] mb-12 rounded-2xl overflow-hidden shadow-2xl"
  >
    <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/80 z-10" />
    <div 
      className="absolute inset-0 bg-cover bg-center z-0 transition-transform duration-700 hover:scale-105" 
      style={{ 
        backgroundImage: `url(https://images.unsplash.com/photo-1502602898536-47ad22581b52?w=1600&h=900&fit=crop&crop=entropy&auto=format&q=80)`,
        filter: 'brightness(0.9) contrast(1.1) saturate(1.2)'
      }}
    />
    <div className="absolute bottom-0 left-0 right-0 p-8 z-20">
      <motion.div
        initial={{ y: 30, opacity: 0 }} 
        animate={{ y: 0, opacity: 1 }} 
        transition={{ delay: 0.3, duration: 0.6 }}
        className="max-w-4xl"
      >
        <div className="flex items-center gap-3 mb-4">
          <Badge className="bg-white/20 text-white border-white/30 backdrop-blur-sm px-3 py-1">
            <Sparkles className="h-4 w-4 mr-1" />
            AI-Curated Guide
          </Badge>
        </div>
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4 leading-tight">
          {destination || "Your Destination"}
        </h1>
        <div className="flex items-center gap-6 text-white/90">
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            <span className="text-lg font-medium">{dates || "Your Travel Dates"}</span>
          </div>
          <div className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            <span className="text-lg">Personalized Recommendations</span>
          </div>
        </div>
      </motion.div>
    </div>
  </motion.div>
);

const RestaurantCard = ({ restaurant, index }: { restaurant: any; index: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: index * 0.08, duration: 0.6, ease: "easeOut" }}
    className="group"
  >
    <Card className="h-full overflow-hidden hover:shadow-2xl hover:-translate-y-2 transition-all duration-500 border-0 bg-white dark:bg-gray-800 rounded-2xl">
      <div className="relative h-56 overflow-hidden">
        {restaurant.photo_url ? (
          <img 
            src={restaurant.photo_url} 
            alt={restaurant.name} 
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-orange-100 to-red-100 dark:from-orange-900/20 dark:to-red-900/20 flex items-center justify-center">
            <div className="text-center">
              <ChefHat className="h-16 w-16 text-orange-400 dark:text-orange-500 mx-auto mb-2" />
              <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Culinary Experience</p>
            </div>
          </div>
        )}
        <div className="absolute top-4 right-4 flex gap-2">
          <Badge className="bg-white/95 text-gray-800 hover:bg-white shadow-lg backdrop-blur-sm border-0 font-semibold">
            {restaurant.price_range || "$$$"}
          </Badge>
          <Button size="sm" variant="ghost" className="h-8 w-8 p-0 bg-white/90 hover:bg-white shadow-lg backdrop-blur-sm">
            <Heart className="h-4 w-4 text-gray-600" />
          </Button>
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
          <div className="flex items-center gap-2 text-white">
            {restaurant.rating && (
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                <span className="font-semibold">{restaurant.rating}</span>
              </div>
            )}
            {restaurant.reviews && (
              <span className="text-sm opacity-90">({typeof restaurant.reviews === 'object' ? restaurant.reviews.count || restaurant.reviews.total || 'Many' : restaurant.reviews} reviews)</span>
            )}
          </div>
        </div>
      </div>
      <CardHeader className="pb-3">
        <CardTitle className="text-xl font-bold line-clamp-1 group-hover:text-orange-600 transition-colors">
          {restaurant.name}
        </CardTitle>
        <CardDescription className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
          <MapPin className="h-4 w-4 text-orange-500" />
          <span className="line-clamp-1">{restaurant.address || "Address unavailable"}</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-4">
        <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2 mb-3">
          {restaurant.description || "Discover authentic flavors and exceptional dining experiences at this carefully selected restaurant."}
        </p>
        <div className="flex flex-wrap gap-2">
          {restaurant.cuisine ? restaurant.cuisine.split(',').map((cuisine: string, i: number) => (
            <Badge key={i} variant="secondary" className="text-xs bg-orange-50 text-orange-700 hover:bg-orange-100 border-orange-200">
              {cuisine.trim()}
            </Badge>
          )) : (
            <>
              <Badge variant="secondary" className="text-xs bg-orange-50 text-orange-700">French Cuisine</Badge>
              <Badge variant="secondary" className="text-xs bg-orange-50 text-orange-700">Fine Dining</Badge>
            </>
          )}
        </div>
      </CardContent>
      <div className="p-4 pt-0">
        <div className="flex gap-2 w-full">
          <Button className="flex-1 bg-orange-600 hover:bg-orange-700 text-white">
            <ExternalLink className="h-4 w-4 mr-2" />
            View Details
          </Button>
          <Button variant="outline" size="sm" className="px-3">
            <Navigation className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  </motion.div>
);

const AttractionCard = ({ attraction, index }: { attraction: any; index: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: index * 0.08, duration: 0.6, ease: "easeOut" }}
    className="group"
  >
    <Card className="h-full overflow-hidden hover:shadow-2xl hover:-translate-y-2 transition-all duration-500 border-0 bg-white dark:bg-gray-800 rounded-2xl">
      <div className="relative h-56 overflow-hidden">
        {attraction.photo_url ? (
          <img 
            src={attraction.photo_url} 
            alt={attraction.name} 
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 flex items-center justify-center">
            <div className="text-center">
              <Camera className="h-16 w-16 text-blue-400 dark:text-blue-500 mx-auto mb-2" />
              <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Cultural Experience</p>
            </div>
          </div>
        )}
        <div className="absolute top-4 right-4 flex gap-2">
          <Badge className="bg-white/95 text-gray-800 hover:bg-white shadow-lg backdrop-blur-sm border-0 font-semibold">
            {attraction.category || "Must-See"}
          </Badge>
          <Button size="sm" variant="ghost" className="h-8 w-8 p-0 bg-white/90 hover:bg-white shadow-lg backdrop-blur-sm">
            <Bookmark className="h-4 w-4 text-gray-600" />
          </Button>
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
          <div className="flex items-center gap-2 text-white">
            {attraction.rating && (
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                <span className="font-semibold">{attraction.rating}</span>
              </div>
            )}
            {attraction.duration && (
              <Badge variant="secondary" className="bg-white/20 text-white border-white/30 text-xs">
                {attraction.duration}
              </Badge>
            )}
          </div>
        </div>
      </div>
      <CardHeader className="pb-3">
        <CardTitle className="text-xl font-bold line-clamp-1 group-hover:text-blue-600 transition-colors">
          {attraction.name}
        </CardTitle>
        <CardDescription className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
          <MapPin className="h-4 w-4 text-blue-500" />
          <span className="line-clamp-1">{attraction.address || "Address unavailable"}</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-4">
        <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2 mb-3">
          {attraction.description || "Discover iconic landmarks and cultural treasures at this carefully selected attraction."}
        </p>
        <div className="flex flex-wrap gap-2">
          {attraction.tags ? attraction.tags.split(',').map((tag: string, i: number) => (
            <Badge key={i} variant="secondary" className="text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-200">
              {tag.trim()}
            </Badge>
          )) : (
            <>
              <Badge variant="secondary" className="text-xs bg-blue-50 text-blue-700">Historic</Badge>
              <Badge variant="secondary" className="text-xs bg-blue-50 text-blue-700">Cultural</Badge>
            </>
          )}
        </div>
      </CardContent>
      <div className="p-4 pt-0">
        <div className="flex gap-2 w-full">
          <Button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white">
            <ExternalLink className="h-4 w-4 mr-2" />
            Explore
          </Button>
          <Button variant="outline" size="sm" className="px-3">
            <Navigation className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  </motion.div>
);

const WeatherDisplay = ({ weather }: { weather: any[] }) => {
  const getWeatherIcon = (conditions: string) => {
    if (conditions?.toLowerCase().includes('rain')) return <CloudRain className="h-5 w-5" />;
    if (conditions?.toLowerCase().includes('cloud')) return <Cloud className="h-5 w-5" />;
    return <Sun className="h-5 w-5" />;
  };

  return (
    <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-0 shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sun className="h-5 w-5 text-blue-500" />
          Weather Forecast
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {weather && weather.length > 0 ? (
            weather.map((day, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05, duration: 0.3 }}
                className="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm"
              >
                <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                </div>
                <div className="flex items-center justify-between mt-2">
                  <div className="text-2xl font-bold">
                    {day.temperature?.high}°
                    <span className="text-sm font-normal text-gray-500 dark:text-gray-400 ml-1">
                      / {day.temperature?.low}°
                    </span>
                  </div>
                  <div className="text-blue-500 dark:text-blue-400">
                    {getWeatherIcon(day.conditions)}
                  </div>
                </div>
                <div className="text-sm mt-1 line-clamp-1">{day.conditions}</div>
              </motion.div>
            ))
          ) : (
            <div className="col-span-full text-center py-4 text-gray-500 dark:text-gray-400">
              Weather data unavailable
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

const EmptyState = ({ type, message, icon: Icon }: { type: string; message: string; icon: any }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    className="flex flex-col items-center justify-center p-8 bg-gray-50 dark:bg-gray-800/50 rounded-xl text-center"
  >
    <div className="bg-white dark:bg-gray-800 p-4 rounded-full mb-4">
      <Icon className="h-8 w-8 text-gray-400 dark:text-gray-500" />
    </div>
    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No {type} Found</h3>
    <p className="text-gray-500 dark:text-gray-400 max-w-md mb-4">{message}</p>
    <Button variant="outline" size="sm">
      Refresh Data
    </Button>
  </motion.div>
);

const HighlightCard = ({ icon, title, count }: { icon: React.ReactNode; title: string; count: number }) => (
  <div className="text-center p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
    <div className="flex justify-center mb-2 text-blue-500">
      {icon}
    </div>
    <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{count}</div>
    <div className="text-sm text-gray-500 dark:text-gray-400">{title}</div>
  </div>
);

function ModernGuidePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams?.get('tripId');
  
  const [guide, setGuide] = useState<GuideData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchGuide = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/demo-guide');
        if (!response.ok) throw new Error('Failed to fetch guide');
        const data = await response.json();
        setGuide(data.guide || data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    
    fetchGuide();
  }, [tripId]);

  if (loading) {
    return (
      <div className="container mx-auto py-12 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mb-4"></div>
          <h2 className="text-2xl font-bold">Loading your travel guide...</h2>
          <p className="text-gray-500 dark:text-gray-400 mt-2">This may take a moment</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-12">
        <div className="bg-red-50 dark:bg-red-900/20 p-6 rounded-xl text-center">
          <div className="text-red-500 dark:text-red-400 mb-4">
            <AlertCircle className="h-12 w-12 mx-auto" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Failed to load guide</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
      </div>
    );
  }

  if (!guide) {
    return (
      <div className="container mx-auto py-12">
        <div className="bg-yellow-50 dark:bg-yellow-900/20 p-6 rounded-xl text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">No Trip Selected</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-4">Please select a trip to view its guide</p>
          <Button asChild>
            <a href="/">Go to Trips</a>
          </Button>
        </div>
      </div>
    );
  }

  const restaurants = guide.restaurants || [];
  const attractions = guide.attractions || [];
  const events = guide.events || [];
  const weather = guide.weather || [];

  return (
    <div className="container mx-auto py-8 px-4">
      <HeroSection 
        destination="Paris, France" 
        dates="December 20-23, 2024" 
      />
      
      <Tabs defaultValue="overview" className="w-full">
        <div className="sticky top-0 z-40 bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700 mb-8">
          <TabsList className="grid grid-cols-7 w-full max-w-4xl mx-auto bg-transparent p-1">
            <TabsTrigger 
              value="overview" 
              className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-700 data-[state=active]:shadow-sm transition-all duration-200"
            >
              <Eye className="h-4 w-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger 
              value="itinerary"
              className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-700 data-[state=active]:shadow-sm transition-all duration-200"
            >
              <Calendar className="h-4 w-4 mr-2" />
              Itinerary
            </TabsTrigger>
            <TabsTrigger 
              value="dining"
              className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-700 data-[state=active]:shadow-sm transition-all duration-200"
            >
              <Utensils className="h-4 w-4 mr-2" />
              Dining
            </TabsTrigger>
            <TabsTrigger 
              value="explore"
              className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-700 data-[state=active]:shadow-sm transition-all duration-200"
            >
              <Camera className="h-4 w-4 mr-2" />
              Explore
            </TabsTrigger>
            <TabsTrigger 
              value="stay"
              className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-700 data-[state=active]:shadow-sm transition-all duration-200"
            >
              <Hotel className="h-4 w-4 mr-2" />
              Stay
            </TabsTrigger>
            <TabsTrigger 
              value="practical"
              className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-700 data-[state=active]:shadow-sm transition-all duration-200"
            >
              <Info className="h-4 w-4 mr-2" />
              Practical
            </TabsTrigger>
            <TabsTrigger 
              value="map"
              className="data-[state=active]:bg-orange-100 data-[state=active]:text-orange-700 data-[state=active]:shadow-sm transition-all duration-200"
            >
              <Map className="h-4 w-4 mr-2" />
              Map
            </TabsTrigger>
          </TabsList>
        </div>
        
        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2 space-y-8">
              <Card>
                <CardHeader>
                  <CardTitle>Trip Highlights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <HighlightCard 
                      icon={<Utensils className="h-6 w-6" />}
                      title="Restaurants"
                      count={restaurants.length}
                    />
                    <HighlightCard 
                      icon={<Camera className="h-6 w-6" />}
                      title="Attractions"
                      count={attractions.length}
                    />
                    <HighlightCard 
                      icon={<Calendar className="h-6 w-6" />}
                      title="Events"
                      count={events.length}
                    />
                    <HighlightCard 
                      icon={<Hotel className="h-6 w-6" />}
                      title="Hotels"
                      count={1}
                    />
                  </div>
                </CardContent>
              </Card>
              
              <WeatherDisplay weather={weather} />
            </div>
            
            <div>
              <Card className="h-full">
                <CardHeader>
                  <CardTitle>Interactive Map</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="aspect-square bg-gray-100 dark:bg-gray-800 relative">
                    <img 
                      src={`https://maps.googleapis.com/maps/api/staticmap?center=${encodeURIComponent(guide.destination || 'Paris,France')}&zoom=12&size=400x400&key=AIzaSyAGeboqYB7rxycwOkOmQoF7KSSSyOR4vjo`}
                      alt="Map"
                      className="w-full h-full object-cover"
                    />
                  </div>
                </CardContent>
                <div className="p-4">
                  <Button variant="outline" className="w-full">Open Full Map</Button>
                </div>
              </Card>
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-4">
                  <Button className="flex items-center gap-2">
                    <Download className="h-4 w-4" />
                    Download PDF
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2">
                    <Share2 className="h-4 w-4" />
                    Share Trip
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2">
                    <Settings className="h-4 w-4" />
                    Edit Preferences
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        {/* Dining Tab */}
        <TabsContent value="dining">
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Restaurants</h2>
              <Button variant="outline" size="sm">Filter</Button>
            </div>
            
            {restaurants && restaurants.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {restaurants.map((restaurant, index) => (
                  <RestaurantCard key={index} restaurant={restaurant} index={index} />
                ))}
              </div>
            ) : (
              <EmptyState 
                type="Restaurants" 
                message="We couldn't find any restaurants matching your preferences. Try adjusting your filters or preferences."
                icon={Utensils}
              />
            )}
          </div>
        </TabsContent>
        
        {/* Explore Tab */}
        <TabsContent value="explore">
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Attractions</h2>
              <Button variant="outline" size="sm">Filter</Button>
            </div>
            
            {attractions && attractions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {attractions.map((attraction, index) => (
                  <AttractionCard key={index} attraction={attraction} index={index} />
                ))}
              </div>
            ) : (
              <EmptyState 
                type="Attractions" 
                message="We couldn't find any attractions matching your preferences. Try adjusting your filters or preferences."
                icon={Camera}
              />
            )}
          </div>
        </TabsContent>
        
        {/* Itinerary Tab */}
        <TabsContent value="itinerary" className="space-y-8">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Daily Itinerary</h2>
            <button className="px-4 py-2 border rounded-lg hover:bg-gray-50">Customize</button>
          </div>
          
          {guide.daily_itinerary && guide.daily_itinerary.length > 0 ? (
            <div className="space-y-6">
              {guide.daily_itinerary.map((day, index) => (
                <div key={index} className="bg-white rounded-xl border p-6 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold">Day {day.day || index + 1}</h3>
                    <span className="text-sm text-gray-500">{day.date}</span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                        <svg className="h-4 w-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z" clipRule="evenodd" />
                        </svg>
                        Morning
                      </h4>
                      <ul className="space-y-1">
                        {(day.morning || []).map((activity, i) => (
                          <li key={i} className="text-sm text-gray-600">• {activity}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                        <svg className="h-4 w-4 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z" clipRule="evenodd" />
                        </svg>
                        Afternoon
                      </h4>
                      <ul className="space-y-1">
                        {(day.afternoon || []).map((activity, i) => (
                          <li key={i} className="text-sm text-gray-600">• {activity}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                        <svg className="h-4 w-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z" clipRule="evenodd" />
                        </svg>
                        Evening
                      </h4>
                      <ul className="space-y-1">
                        {(day.evening || []).map((activity, i) => (
                          <li key={i} className="text-sm text-gray-600">• {activity}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  {day.notes && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-800">{day.notes}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-xl">
              <svg className="h-12 w-12 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Itinerary Available</h3>
              <p className="text-gray-500">Your personalized daily itinerary will appear here once generated.</p>
            </div>
          )}
        </TabsContent>
        
        {/* Stay Tab */}
        <TabsContent value="stay" className="space-y-8">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Where to Stay</h2>
            <Button variant="outline" size="sm">Find Hotels</Button>
          </div>
          
          <div className="text-center py-12 bg-gray-50 rounded-xl">
            <Hotel className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Hotels Listed</h3>
            <p className="text-gray-500">Hotel recommendations will appear here based on your preferences.</p>
          </div>
        </TabsContent>
        
        <TabsContent value="practical" className="space-y-8">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Practical Information</h2>
            <Button variant="outline" size="sm">Download Guide</Button>
          </div>
          
          {guide.practical_info && Object.keys(guide.practical_info).length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {guide.practical_info.transportation && (
                <div className="bg-white rounded-xl border p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Car className="h-5 w-5 text-blue-500" />
                    Transportation
                  </h3>
                  <ul className="space-y-2">
                    {guide.practical_info.transportation.map((item, i) => (
                      <li key={i} className="text-sm text-gray-600">• {item}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {guide.practical_info.money && (
                <div className="bg-white rounded-xl border p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <CreditCard className="h-5 w-5 text-green-500" />
                    Money & Payments
                  </h3>
                  <ul className="space-y-2">
                    {(guide.practical_info?.money && Array.isArray(guide.practical_info.money)) ? 
                      guide.practical_info.money.map((item, i) => (
                        <li key={i} className="text-sm text-gray-600">• {item}</li>
                      )) : 
                      [<li key="no-payment" className="text-sm text-gray-500">No payment information available</li>]
                    }
                  </ul>
                </div>
              )}
              
              {guide.practical_info?.tips && (
                <div className="bg-white rounded-xl border p-6 md:col-span-2">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Info className="h-5 w-5 text-yellow-500" />
                    Local Tips
                  </h3>
                  <ul className="space-y-2">
                    {(guide.practical_info?.tips && Array.isArray(guide.practical_info.tips)) ? 
                      guide.practical_info.tips.map((item, i) => (
                        <li key={i} className="text-sm text-gray-600">• {item}</li>
                      )) : 
                      [<li key="no-tips" className="text-sm text-gray-500">No local tips available</li>]
                    }
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-xl">
              <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Practical Information</h3>
              <p className="text-gray-500">Practical travel tips and information will appear here.</p>
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="map" className="space-y-8">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Interactive Map</h2>
            <Button variant="outline" size="sm">Full Screen</Button>
          </div>
          
          <div className="bg-white rounded-xl border overflow-hidden">
            <div className="aspect-video bg-gray-100 relative">
              <img 
                src={`https://maps.googleapis.com/maps/api/staticmap?center=${encodeURIComponent(guide.destination || 'Paris,France')}&zoom=12&size=800x600&key=AIzaSyAGeboqYB7rxycwOkOmQoF7KSSSyOR4vjo`}
                alt="Map"
                className="w-full h-full object-cover"
              />
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{restaurants?.length || 0}</div>
                  <div className="text-sm text-gray-500">Restaurants</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{attractions?.length || 0}</div>
                  <div className="text-sm text-gray-500">Attractions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{guide.events?.length || 0}</div>
                  <div className="text-sm text-gray-500">Events</div>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
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

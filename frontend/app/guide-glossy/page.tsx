"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion, useScroll, useTransform } from "framer-motion";
import { 
  MapPin, Calendar, Clock, Utensils, Camera, Hotel, 
  Sun, Cloud, CloudRain, Sparkles, Star, Navigation,
  Phone, Globe, DollarSign, Heart, ArrowRight, Info
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

function GlossyGuideContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId");
  
  const [guide, setGuide] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { scrollYProgress } = useScroll();
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0.3]);
  
  useEffect(() => {
    if (tripId) fetchGuide();
  }, [tripId]);
  
  const fetchGuide = async () => {
    try {
      const response = await fetch(`/api/proxy/enhanced-guide/${tripId}`);
      if (response.ok) {
        const data = await response.json();
        // Keep the original structure for backward compatibility
        // But ensure we have the guide data
        if (data.guide) {
          // New API structure: { guide: {...}, status: "success" }
          setGuide({ enhanced_guide: data.guide, itinerary: data.guide });
        } else {
          // Old structure
          setGuide(data);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <Sparkles className="h-12 w-12 text-gold-500" />
        </motion.div>
      </div>
    );
  }
  
  if (!guide) return null;
  
  const { itinerary, enhanced_guide } = guide;
  const trip = itinerary?.trip_summary || {};
  const restaurants = enhanced_guide?.restaurants || [];
  const attractions = enhanced_guide?.attractions || [];
  const weather = enhanced_guide?.weather || [];
  const itineraryDays = enhanced_guide?.daily_itinerary || [];
  
  return (
    <div className="min-h-screen bg-white">
      {/* HERO COVER - Full Bleed Magazine Style */}
      <motion.section 
        className="relative h-screen flex items-center justify-center overflow-hidden"
        style={{ opacity }}
      >
        {/* Gradient Background - Destination Inspired */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900" />
        
        {/* Floating Elements */}
        <motion.div
          className="absolute top-20 left-20"
          animate={{ y: [0, -20, 0] }}
          transition={{ duration: 4, repeat: Infinity }}
        >
          <div className="w-32 h-32 bg-white/10 rounded-full blur-3xl" />
        </motion.div>
        
        <motion.div
          className="absolute bottom-20 right-20"
          animate={{ y: [0, 20, 0] }}
          transition={{ duration: 5, repeat: Infinity }}
        >
          <div className="w-48 h-48 bg-blue-400/20 rounded-full blur-3xl" />
        </motion.div>
        
        {/* Magazine Title */}
        <div className="relative z-10 text-center text-white px-8 max-w-6xl mx-auto">
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1 }}
          >
            <div className="mb-6">
              <span className="text-xs uppercase tracking-[0.3em] text-blue-200">
                Your Personal Travel Guide
              </span>
            </div>
            
            <h1 className="text-6xl md:text-8xl font-serif mb-6">
              {trip.destination}
            </h1>
            
            <div className="flex items-center justify-center gap-8 text-sm uppercase tracking-wider text-blue-100">
              <span className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                {trip.start_date}
              </span>
              <span className="w-px h-4 bg-blue-300" />
              <span>{trip.duration}</span>
              <span className="w-px h-4 bg-blue-300" />
              <span className="flex items-center gap-2">
                {trip.end_date}
                <Calendar className="h-4 w-4" />
              </span>
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 1 }}
            className="mt-12"
          >
            <p className="text-xl text-blue-100 italic font-serif max-w-3xl mx-auto leading-relaxed">
              "Your journey through {trip.destination} awaits. From hidden culinary gems to 
              breathtaking landmarks, every moment has been curated for an unforgettable experience."
            </p>
          </motion.div>
        </div>
        
        {/* Scroll Indicator */}
        <motion.div
          className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-white/50 rounded-full mt-2" />
          </div>
        </motion.div>
      </motion.section>
      
      {/* WEATHER STRIP - Elegant Forecast */}
      {weather.length > 0 && (
        <section className="py-8 bg-gradient-to-r from-sky-50 to-blue-50">
          <div className="max-w-6xl mx-auto px-8">
            <div className="flex items-center justify-between">
              <h3 className="text-sm uppercase tracking-wider text-gray-600">Weather Forecast</h3>
              <div className="flex gap-8">
                {weather.slice(0, 5).map((day: any, idx: number) => (
                  <div key={idx} className="text-center">
                    <div className="text-xs text-gray-500 mb-1">
                      {new Date(day.date).toLocaleDateString('en', { weekday: 'short' })}
                    </div>
                    <div className="text-2xl mb-1">
                      {day.condition === 'Clear' ? '☀️' : 
                       day.condition === 'Clouds' ? '☁️' : 
                       day.condition === 'Rain' ? '🌧️' : '⛅'}
                    </div>
                    <div className="text-sm font-medium">
                      {day.temp_high}°
                      <span className="text-gray-400 ml-1">/ {day.temp_low}°</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}
      
      {/* DAILY JOURNEY - Editorial Style */}
      <section className="py-20 px-8">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-serif mb-4">Your Daily Journey</h2>
            <div className="w-24 h-px bg-gray-300 mx-auto" />
          </motion.div>
          
          {itineraryDays.map((day: any, idx: number) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: idx % 2 === 0 ? -50 : 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="mb-20"
            >
              <div className={cn(
                "grid grid-cols-1 md:grid-cols-2 gap-12 items-center",
                idx % 2 === 1 && "md:flex-row-reverse"
              )}>
                <div className={idx % 2 === 1 ? "md:order-2" : ""}>
                  <div className="text-6xl font-serif text-gray-200 mb-4">
                    {String(idx + 1).padStart(2, '0')}
                  </div>
                  <h3 className="text-3xl font-serif mb-4">
                    {day.theme || `Day ${idx + 1} Adventures`}
                  </h3>
                  <div className="space-y-4 text-gray-600">
                    {(day.activities || []).map((activity: any, i: number) => (
                      <div key={i} className="flex gap-3">
                        <div className="w-2 h-2 rounded-full bg-gold-500 mt-2 flex-shrink-0" />
                        <p className="leading-relaxed">{activity}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div className={cn(
                  "relative h-96 bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg overflow-hidden",
                  idx % 2 === 1 ? "md:order-1" : ""
                )}>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <MapPin className="h-24 w-24 text-gray-300" />
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
      
      {/* CULINARY GUIDE - Restaurant Showcase */}
      <section className="py-20 bg-gradient-to-br from-orange-50 to-red-50">
        <div className="max-w-6xl mx-auto px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-serif mb-4">Culinary Discoveries</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              From Michelin-worthy establishments to hidden local gems, 
              each venue has been selected to create unforgettable dining memories.
            </p>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {restaurants.slice(0, 6).map((restaurant: any, idx: number) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
              >
                <div className="h-48 bg-gradient-to-br from-orange-100 to-red-100 relative">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Utensils className="h-16 w-16 text-orange-300" />
                  </div>
                  <div className="absolute top-4 right-4">
                    <Badge className="bg-white/90">{restaurant.price_range}</Badge>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-serif mb-2">{restaurant.name}</h3>
                  <p className="text-sm text-gray-500 mb-3">{restaurant.cuisine}</p>
                  <p className="text-gray-600 text-sm leading-relaxed mb-4">
                    {restaurant.description || restaurant.why_recommended}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {restaurant.address?.split(',')[0]}
                    </span>
                    {restaurant.rating && (
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
                        <span className="text-sm font-medium">{restaurant.rating}</span>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
      
      {/* MUST-SEE ATTRACTIONS - Visual Grid */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-serif mb-4">Essential Experiences</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Iconic landmarks and hidden treasures that define {trip.destination}.
            </p>
          </motion.div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {attractions.slice(0, 4).map((attraction: any, idx: number) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                className="group relative h-96 rounded-lg overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600" />
                <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors" />
                <div className="absolute inset-0 p-8 flex flex-col justify-end text-white">
                  <Badge className="self-start mb-4 bg-white/20 backdrop-blur">
                    {attraction.type}
                  </Badge>
                  <h3 className="text-3xl font-serif mb-2">{attraction.name}</h3>
                  <p className="text-white/90 mb-4 line-clamp-3">
                    {attraction.description}
                  </p>
                  <div className="flex items-center gap-4 text-sm">
                    {attraction.hours && (
                      <span className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {attraction.hours}
                      </span>
                    )}
                    {attraction.price && (
                      <span className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4" />
                        {attraction.price}
                      </span>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
      
      {/* CLOSING - Call to Adventure */}
      <section className="py-32 bg-gradient-to-br from-slate-900 to-black text-white">
        <div className="max-w-4xl mx-auto text-center px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-5xl font-serif mb-6">Your Journey Awaits</h2>
            <p className="text-xl text-gray-300 mb-12 leading-relaxed">
              Every great adventure begins with a single step. Your personalized guide to 
              {trip.destination} is ready to transform your travel dreams into unforgettable memories.
            </p>
            <div className="flex gap-4 justify-center">
              <Button 
                size="lg"
                className="bg-white text-black hover:bg-gray-100 px-8"
                onClick={() => window.print()}
              >
                Download Guide
              </Button>
              <Button 
                size="lg"
                variant="outline"
                className="border-white text-white hover:bg-white/10 px-8"
                onClick={() => router.push(`/preferences-modern?tripId=${tripId}`)}
              >
                Refine Preferences
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}

export default function GlossyGuidePage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <GlossyGuideContent />
    </Suspense>
  );
}
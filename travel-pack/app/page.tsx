"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Plane, 
  Upload, 
  Sparkles, 
  MapPin, 
  Calendar,
  Cloud,
  Utensils,
  Palette,
  Ticket,
  FileText,
  ArrowRight,
  Check,
  Globe,
  Sun,
  Settings
} from "lucide-react";
import Link from "next/link";

export default function Home() {
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null);

  const features = [
    {
      icon: Upload,
      title: "Smart Document Processing",
      description: "Upload any travel document - PDFs, confirmations, or just paste text",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: Sparkles,
      title: "Real Recommendations",
      description: "Get actual restaurants and attractions from Perplexity AI - no placeholders",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: MapPin,
      title: "Complete Itinerary",
      description: "Day-by-day schedule with real venues, addresses, and local tips",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: FileText,
      title: "Save & Export",
      description: "Save all trips, export to PDF, access anywhere",
      color: "from-orange-500 to-red-500"
    }
  ];

  const steps = [
    { icon: Upload, label: "Upload Documents" },
    { icon: Sparkles, label: "AI Processing" },
    { icon: MapPin, label: "Enrich Data" },
    { icon: FileText, label: "Export PDF" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <motion.div
              initial={{ rotate: 0 }}
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: -1, ease: "linear" }}
            >
              <Globe className="h-8 w-8 text-sky-500" />
            </motion.div>
            <span className="text-2xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
              TripCraft AI
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <Link href="/trips">
              <Button variant="ghost">My Trips</Button>
            </Link>
            <Link href="/upload">
              <Button className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700">
                Upload Trip
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge className="mb-4 px-4 py-1 text-sm bg-sky-100 text-sky-700 border-sky-200">
              <Sparkles className="w-3 h-3 mr-1" />
              Powered by Perplexity AI - Real Recommendations
            </Badge>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-blue-800 to-sky-600 bg-clip-text text-transparent">
              Turn Travel Documents
              <br />
              Into Perfect Itineraries
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Upload any travel confirmation and get real restaurant recommendations, 
              actual attractions, and a complete day-by-day itinerary powered by Perplexity AI.
            </p>

            <div className="flex gap-4 justify-center mb-12">
              <Link href="/upload">
                <Button size="lg" className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700 text-lg px-8 py-6">
                  <Upload className="mr-2 h-5 w-5" />
                  Upload Your Trip
                </Button>
              </Link>
              <Link href="/trips">
                <Button size="lg" variant="outline" className="text-lg px-8 py-6">
                  View Saved Trips
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>

            {/* Animated Icons */}
            <div className="relative h-64 max-w-4xl mx-auto">
              <motion.div
                className="absolute top-0 left-0"
                animate={{ 
                  x: [0, 100, 0],
                  y: [0, -50, 0]
                }}
                transition={{ duration: 8, repeat: -1 }}
              >
                <Plane className="h-12 w-12 text-sky-500" />
              </motion.div>
              
              <motion.div
                className="absolute top-20 right-0"
                animate={{ 
                  x: [0, -100, 0],
                  y: [0, 50, 0]
                }}
                transition={{ duration: 10, repeat: -1 }}
              >
                <MapPin className="h-10 w-10 text-green-500" />
              </motion.div>
              
              <motion.div
                className="absolute bottom-0 left-1/4"
                animate={{ 
                  scale: [1, 1.2, 1],
                  rotate: [0, 180, 360]
                }}
                transition={{ duration: 12, repeat: -1 }}
              >
                <Sun className="h-8 w-8 text-yellow-500" />
              </motion.div>
              
              <motion.div
                className="absolute top-10 left-1/2"
                animate={{ 
                  y: [0, -20, 0]
                }}
                transition={{ duration: 4, repeat: -1 }}
              >
                <Cloud className="h-16 w-16 text-gray-300" />
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Process Steps */}
      <section className="py-20 px-6 bg-white/50">
        <div className="container mx-auto">
          <motion.h2 
            className="text-4xl font-bold text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            How It Works
          </motion.h2>
          
          <div className="flex justify-between items-center max-w-4xl mx-auto mb-16">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                className="flex flex-col items-center"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <div className={`
                  w-20 h-20 rounded-full flex items-center justify-center
                  bg-gradient-to-br from-sky-500 to-blue-600 text-white
                  shadow-lg transform transition-transform hover:scale-110
                `}>
                  <step.icon className="h-10 w-10" />
                </div>
                <p className="mt-3 text-sm font-medium text-gray-700">{step.label}</p>
                {index < steps.length - 1 && (
                  <ArrowRight className="absolute left-full top-10 -ml-4 text-gray-300 hidden md:block" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-6">
        <div className="container mx-auto">
          <motion.h2 
            className="text-4xl font-bold text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            Everything You Need for Perfect Travel
          </motion.h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                onHoverStart={() => setHoveredFeature(index)}
                onHoverEnd={() => setHoveredFeature(null)}
              >
                <Card className={`
                  p-6 h-full cursor-pointer transition-all duration-300
                  ${hoveredFeature === index ? 'shadow-2xl scale-105' : 'shadow-lg'}
                  border-0
                `}>
                  <div className={`
                    w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color}
                    flex items-center justify-center mb-4 text-white
                  `}>
                    <feature.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* What's Included */}
      <section className="py-20 px-6 bg-gradient-to-br from-sky-50 to-blue-50">
        <div className="container mx-auto max-w-4xl">
          <motion.h2 
            className="text-4xl font-bold text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            Your Travel Pack Includes
          </motion.h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            {[
              { icon: Calendar, text: "Day-by-day itinerary with timing" },
              { icon: MapPin, text: "Interactive maps with all locations" },
              { icon: Cloud, text: "Weather forecast for your dates" },
              { icon: Utensils, text: "Restaurant recommendations" },
              { icon: Palette, text: "Art & culture attractions" },
              { icon: Ticket, text: "Local events and tickets" },
            ].map((item, index) => (
              <motion.div
                key={index}
                className="flex items-center space-x-4"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                  <Check className="h-5 w-5 text-green-600" />
                </div>
                <div className="flex items-center space-x-3">
                  <item.icon className="h-5 w-5 text-gray-600" />
                  <span className="text-lg text-gray-700">{item.text}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="bg-gradient-to-r from-sky-500 to-blue-600 rounded-3xl p-12 text-white max-w-4xl mx-auto"
          >
            <h2 className="text-4xl font-bold mb-4">Ready to Plan Your Next Trip?</h2>
            <p className="text-xl mb-8 opacity-90">
              No more generic suggestions - get real venues with actual addresses
            </p>
            <Link href="/upload">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 text-lg px-8 py-6">
                Upload Your Documents
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-6">
        <div className="container mx-auto text-center">
          <p className="text-gray-400">© 2024 TripCraft AI. Transforming travel, one trip at a time.</p>
        </div>
      </footer>
    </div>
  );
}
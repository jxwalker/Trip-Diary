"use client"

import React from "react"
import { motion } from "framer-motion"
import { Calendar, MapPin } from "lucide-react"

interface HeroSectionProps {
  destination: string
  dates: string
}

export function HeroSection({ destination, dates }: HeroSectionProps) {
  return (
    <motion.div 
      initial={{ opacity: 0 }} 
      animate={{ opacity: 1 }} 
      transition={{ duration: 0.5 }}
      className="relative w-full h-64 md:h-80 lg:h-96 mb-8 rounded-xl overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/70 z-10" />
      <div 
        className="absolute inset-0 bg-cover bg-center z-0" 
        style={{ 
          backgroundImage: `url(https://source.unsplash.com/1600x900/${encodeURIComponent(destination || 'travel')})` 
        }}
      />
      <div className="absolute bottom-0 left-0 p-6 z-20 w-full">
        <motion.h1 
          initial={{ y: 20, opacity: 0 }} 
          animate={{ y: 0, opacity: 1 }} 
          transition={{ delay: 0.2, duration: 0.5 }}
          className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2"
        >
          {destination || "Your Destination"}
        </motion.h1>
        <motion.p 
          initial={{ y: 20, opacity: 0 }} 
          animate={{ y: 0, opacity: 1 }} 
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-lg text-white/90 flex items-center gap-2"
        >
          <Calendar className="h-5 w-5" />
          {dates || "Your Travel Dates"}
        </motion.p>
      </div>
    </motion.div>
  )
}

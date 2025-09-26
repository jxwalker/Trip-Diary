"use client"

import React from "react"
import { motion } from "framer-motion"
import { MapPin, Camera, Star, Clock, Globe, Ticket } from "lucide-react"

interface AttractionCardProps {
  attraction: {
    name: string
    address?: string
    description?: string
    category?: string
    type?: string
    rating?: number
    duration?: string
    price?: string
    website?: string
    photo?: string
    photo_url?: string
    hours?: string[]
    booking_url?: string
    ticket_info?: string
  }
  index: number
}

export function AttractionCard({ attraction, index }: AttractionCardProps) {
  const photoUrl = attraction.photo_url || attraction.photo

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      className="group"
    >
      <div className="h-full overflow-hidden hover:shadow-lg transition-all duration-300 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="relative h-48 overflow-hidden">
          {photoUrl ? (
            <img 
              src={photoUrl} 
              alt={attraction.name} 
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          ) : (
            <div className="w-full h-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
              <Camera className="h-12 w-12 text-gray-400 dark:text-gray-500" />
            </div>
          )}
          <div className="absolute top-3 right-3">
            <span className="bg-white/90 text-black hover:bg-white/80 dark:bg-black/80 dark:text-white px-2 py-1 rounded-full text-xs font-medium">
              {attraction.category || attraction.type || "Attraction"}
            </span>
          </div>
          {attraction.rating && (
            <div className="absolute top-3 left-3 bg-white/90 dark:bg-black/80 rounded-full px-2 py-1 flex items-center gap-1">
              <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
              <span className="text-xs font-medium">{attraction.rating}</span>
            </div>
          )}
        </div>
        <div className="p-4 pb-2">
          <h3 className="text-xl font-bold line-clamp-1">{attraction.name}</h3>
          <p className="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400">
            <MapPin className="h-3.5 w-3.5" />
            <span className="line-clamp-1">{attraction.address || "Address unavailable"}</span>
          </p>
        </div>
        <div className="px-4 pb-2">
          <p className="text-sm line-clamp-2 mb-2">{attraction.description || "No description available"}</p>
          <div className="flex items-center gap-2 mb-2">
            {attraction.duration && (
              <span className="border border-gray-300 dark:border-gray-600 px-2 py-1 rounded text-xs flex items-center">
                <Clock className="h-3 w-3 mr-1" />
                {attraction.duration}
              </span>
            )}
            {attraction.price && (
              <span className="border border-gray-300 dark:border-gray-600 px-2 py-1 rounded text-xs flex items-center">
                <Ticket className="h-3 w-3 mr-1" />
                {attraction.price}
              </span>
            )}
          </div>
          {attraction.ticket_info && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">{attraction.ticket_info}</p>
          )}
          {attraction.hours && attraction.hours.length > 0 && (
            <div className="text-xs text-gray-500 dark:text-gray-400">
              <Clock className="h-3 w-3 inline mr-1" />
              {attraction.hours[0]}
            </div>
          )}
        </div>
        <div className="p-4 pt-0 flex gap-2">
          {attraction.booking_url && (
            <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm font-medium flex items-center justify-center">
              <Ticket className="h-3 w-3 mr-1" />
              Book Now
            </button>
          )}
          {attraction.website && (
            <button className="flex-1 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 px-3 py-2 rounded text-sm font-medium flex items-center justify-center">
              <Globe className="h-3 w-3 mr-1" />
              Website
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}

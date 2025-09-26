"use client"

import React from "react"
import { motion } from "framer-motion"
import { MapPin, Utensils, Star, Clock, Phone, Globe } from "lucide-react"

interface RestaurantCardProps {
  restaurant: {
    name: string
    address?: string
    description?: string
    cuisine?: string
    price_range?: string
    rating?: number
    phone?: string
    website?: string
    photo?: string
    photo_url?: string
    hours?: string[]
    booking_url?: string
  }
  index: number
}

export function RestaurantCard({ restaurant, index }: RestaurantCardProps) {
  const photoUrl = restaurant.photo_url || restaurant.photo

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
              alt={restaurant.name} 
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          ) : (
            <div className="w-full h-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
              <Utensils className="h-12 w-12 text-gray-400 dark:text-gray-500" />
            </div>
          )}
          <div className="absolute top-3 right-3">
            <span className="bg-white/90 text-black hover:bg-white/80 dark:bg-black/80 dark:text-white px-2 py-1 rounded-full text-xs font-medium">
              {restaurant.price_range || "$$$"}
            </span>
          </div>
          {restaurant.rating && (
            <div className="absolute top-3 left-3 bg-white/90 dark:bg-black/80 rounded-full px-2 py-1 flex items-center gap-1">
              <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
              <span className="text-xs font-medium">{restaurant.rating}</span>
            </div>
          )}
        </div>
        <div className="p-4 pb-2">
          <h3 className="text-xl font-bold line-clamp-1">{restaurant.name}</h3>
          <p className="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400">
            <MapPin className="h-3.5 w-3.5" />
            <span className="line-clamp-1">{restaurant.address || "Address unavailable"}</span>
          </p>
        </div>
        <div className="px-4 pb-2">
          <p className="text-sm line-clamp-2 mb-2">{restaurant.description || "No description available"}</p>
          <div className="flex flex-wrap gap-1 mb-2">
            {restaurant.cuisine && restaurant.cuisine.split(',').map((cuisine, i) => (
              <span key={i} className="border border-gray-300 dark:border-gray-600 px-2 py-1 rounded text-xs">{cuisine.trim()}</span>
            ))}
          </div>
          <div className="space-y-1 text-xs text-gray-500 dark:text-gray-400">
            {restaurant.phone && (
              <div className="flex items-center gap-1">
                <Phone className="h-3 w-3" />
                <span>{restaurant.phone}</span>
              </div>
            )}
            {restaurant.hours && restaurant.hours.length > 0 && (
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{restaurant.hours[0]}</span>
              </div>
            )}
          </div>
        </div>
        <div className="p-4 pt-0 flex gap-2">
          {restaurant.booking_url && (
            <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm font-medium">
              Reserve
            </button>
          )}
          {restaurant.website && (
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

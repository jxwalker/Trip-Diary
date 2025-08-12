"use client";

import { useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { 
  ChevronRight,
  Music,
  Palette,
  Camera,
  Utensils,
  ShoppingBag,
  Mountain,
  Building,
  Wine,
  Coffee,
  Heart,
  Users,
  MapPin,
  Landmark,
  TreePine,
  Theater,
  Waves,
  Dumbbell,
  Baby,
  Star,
  Footprints,
  Compass,
  Check,
  Loader2,
  DollarSign
} from "lucide-react";

export default function SinglePagePreferences() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId");
  
  const [isGenerating, setIsGenerating] = useState(false);
  
  const [preferences, setPreferences] = useState({
    // Interests
    interests: {
      artGalleries: false,
      museums: false,
      historicalSites: false,
      architecture: false,
      liveMusic: false,
      concerts: false,
      theater: false,
      localCuisine: true,
      fineDining: false,
      streetFood: false,
      cafes: false,
      bars: false,
      nightclubs: false,
      shopping: false,
      localMarkets: false,
      nature: false,
      beaches: false,
      hiking: false,
      photography: false,
      wellness: false,
      sports: false,
      familyActivities: false,
    },
    
    // Food & Budget
    cuisineTypes: ["Local Cuisine"],
    dietaryRestrictions: [],
    priceRanges: ["$$"],
    
    // Activity
    walkingTolerance: 3,
    adventureLevel: 3,
    
    // Style
    pace: "balanced",
    groupType: "couple",
  });

  const interestIcons = {
    artGalleries: Palette,
    museums: Building,
    historicalSites: Landmark,
    architecture: Building,
    liveMusic: Music,
    concerts: Music,
    theater: Theater,
    localCuisine: Utensils,
    fineDining: Star,
    streetFood: MapPin,
    cafes: Coffee,
    bars: Wine,
    nightclubs: Music,
    shopping: ShoppingBag,
    localMarkets: MapPin,
    nature: TreePine,
    beaches: Waves,
    hiking: Mountain,
    photography: Camera,
    wellness: Heart,
    sports: Dumbbell,
    familyActivities: Baby,
  };

  const interestLabels = {
    artGalleries: "Art Galleries",
    museums: "Museums",
    historicalSites: "Historical Sites",
    architecture: "Architecture",
    liveMusic: "Live Music",
    concerts: "Concerts",
    theater: "Theater",
    localCuisine: "Local Food",
    fineDining: "Fine Dining",
    streetFood: "Street Food",
    cafes: "Cafés",
    bars: "Bars & Pubs",
    nightclubs: "Nightlife",
    shopping: "Shopping",
    localMarkets: "Markets",
    nature: "Nature",
    beaches: "Beaches",
    hiking: "Hiking",
    photography: "Photography",
    wellness: "Spa & Wellness",
    sports: "Sports",
    familyActivities: "Family",
  };

  const cuisineOptions = [
    "Local Cuisine", "Italian", "French", "Japanese", "Chinese", 
    "Mexican", "Indian", "Thai", "Mediterranean", "American",
    "Korean", "Vietnamese", "Seafood", "Vegetarian", "Vegan"
  ];

  const dietaryOptions = [
    "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", 
    "Halal", "Kosher", "Nut Allergy"
  ];

  const handleInterestToggle = (key: string) => {
    setPreferences(prev => ({
      ...prev,
      interests: {
        ...prev.interests,
        [key]: !prev.interests[key as keyof typeof prev.interests]
      }
    }));
  };

  const handleCuisineToggle = (cuisine: string) => {
    setPreferences(prev => ({
      ...prev,
      cuisineTypes: prev.cuisineTypes.includes(cuisine)
        ? prev.cuisineTypes.filter(c => c !== cuisine)
        : [...prev.cuisineTypes, cuisine]
    }));
  };

  const handleDietaryToggle = (restriction: string) => {
    setPreferences(prev => ({
      ...prev,
      dietaryRestrictions: prev.dietaryRestrictions.includes(restriction)
        ? prev.dietaryRestrictions.filter(r => r !== restriction)
        : [...prev.dietaryRestrictions, restriction]
    }));
  };

  const handlePriceToggle = (price: string) => {
    setPreferences(prev => ({
      ...prev,
      priceRanges: prev.priceRanges.includes(price)
        ? prev.priceRanges.filter(p => p !== price)
        : [...prev.priceRanges, price]
    }));
  };

  const handleGenerateItinerary = async () => {
    setIsGenerating(true);
    
    try {
      const response = await fetch(`/api/proxy/preferences/${tripId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...preferences,
          specialInterests: Object.entries(preferences.interests)
            .filter(([_, value]) => value)
            .map(([key, _]) => key),
          travelStyle: preferences.pace,
          groupType: preferences.groupType,
        })
      });
      
      if (response.ok) {
        router.push(`/generate-itinerary?tripId=${tripId}`);
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      setIsGenerating(false);
    }
  };

  const selectedInterestsCount = Object.values(preferences.interests).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-sky-50">
      {/* Fixed Header */}
      <div className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Personalize Your Trip</h1>
            <p className="text-sm text-gray-600">Tell us what you love</p>
          </div>
          <Button
            size="lg"
            onClick={handleGenerateItinerary}
            disabled={isGenerating || selectedInterestsCount === 0}
            className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating Guide...
              </>
            ) : (
              <>
                Generate My Guide
                <ChevronRight className="h-4 w-4 ml-2" />
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6 max-w-7xl">
        <div className="grid lg:grid-cols-3 gap-6">
          
          {/* Left Column - Interests & Activities */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Interests Grid */}
            <Card className="p-6">
              <div className="mb-4">
                <h2 className="text-lg font-semibold">What interests you?</h2>
                <p className="text-sm text-gray-600">Select all that apply ({selectedInterestsCount} selected)</p>
              </div>
              
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                {Object.entries(preferences.interests).map(([key, isSelected]) => {
                  const Icon = interestIcons[key as keyof typeof interestIcons];
                  const label = interestLabels[key as keyof typeof interestLabels];
                  return (
                    <motion.div
                      key={key}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleInterestToggle(key)}
                      className={`
                        p-3 rounded-xl border-2 cursor-pointer transition-all text-center
                        ${isSelected 
                          ? 'border-sky-500 bg-sky-50 shadow-md' 
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                        }
                      `}
                    >
                      <Icon className={`h-6 w-6 mx-auto mb-1 ${isSelected ? 'text-sky-600' : 'text-gray-500'}`} />
                      <span className={`text-xs ${isSelected ? 'font-medium text-sky-900' : 'text-gray-700'}`}>
                        {label}
                      </span>
                      {isSelected && (
                        <Check className="h-3 w-3 text-sky-600 mx-auto mt-1" />
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </Card>

            {/* Cuisine Preferences */}
            <Card className="p-6">
              <div className="mb-4">
                <h2 className="text-lg font-semibold">Cuisine Preferences</h2>
                <p className="text-sm text-gray-600">What kind of food do you enjoy?</p>
              </div>
              
              <div className="flex flex-wrap gap-2">
                {cuisineOptions.map((cuisine) => (
                  <Badge
                    key={cuisine}
                    variant={preferences.cuisineTypes.includes(cuisine) ? "default" : "outline"}
                    className="cursor-pointer py-1.5 px-3 hover:scale-105 transition-transform"
                    onClick={() => handleCuisineToggle(cuisine)}
                  >
                    {preferences.cuisineTypes.includes(cuisine) && (
                      <Check className="h-3 w-3 mr-1" />
                    )}
                    {cuisine}
                  </Badge>
                ))}
              </div>

              {/* Dietary Restrictions */}
              <div className="mt-4 pt-4 border-t">
                <Label className="text-sm mb-2 block">Dietary Restrictions</Label>
                <div className="flex flex-wrap gap-2">
                  {dietaryOptions.map((restriction) => (
                    <Badge
                      key={restriction}
                      variant={preferences.dietaryRestrictions.includes(restriction) ? "destructive" : "outline"}
                      className="cursor-pointer py-1 px-2 text-xs"
                      onClick={() => handleDietaryToggle(restriction)}
                    >
                      {restriction}
                    </Badge>
                  ))}
                </div>
              </div>
            </Card>
          </div>

          {/* Right Column - Settings */}
          <div className="space-y-6">
            
            {/* Budget */}
            <Card className="p-6">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-green-600" />
                Budget Range
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {["$", "$$", "$$$", "$$$$"].map((price) => {
                  const labels = {
                    "$": "Budget",
                    "$$": "Moderate",
                    "$$$": "Upscale",
                    "$$$$": "Luxury"
                  };
                  const isSelected = preferences.priceRanges.includes(price);
                  return (
                    <div
                      key={price}
                      onClick={() => handlePriceToggle(price)}
                      className={`
                        p-3 rounded-lg border-2 cursor-pointer transition-all text-center
                        ${isSelected 
                          ? 'border-green-500 bg-green-50' 
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                        }
                      `}
                    >
                      <div className="font-bold">{price}</div>
                      <div className={`text-xs ${isSelected ? 'text-green-700' : 'text-gray-500'}`}>
                        {labels[price as keyof typeof labels]}
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Activity Level */}
            <Card className="p-6">
              <h3 className="font-semibold mb-4">Activity Level</h3>
              
              {/* Walking */}
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <Label className="text-sm flex items-center gap-2">
                    <Footprints className="h-4 w-4 text-sky-500" />
                    Walking
                  </Label>
                  <span className="text-xs text-gray-600">
                    {["Minimal", "Light", "Moderate", "Active", "Very Active"][preferences.walkingTolerance - 1]}
                  </span>
                </div>
                <Slider
                  value={[preferences.walkingTolerance]}
                  onValueChange={(value) => setPreferences(prev => ({ ...prev, walkingTolerance: value[0] }))}
                  max={5}
                  min={1}
                  step={1}
                  className="h-2"
                />
              </div>

              {/* Adventure */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <Label className="text-sm flex items-center gap-2">
                    <Compass className="h-4 w-4 text-purple-500" />
                    Adventure
                  </Label>
                  <span className="text-xs text-gray-600">
                    {["Tourist", "Popular", "Mixed", "Adventurous", "Explorer"][preferences.adventureLevel - 1]}
                  </span>
                </div>
                <Slider
                  value={[preferences.adventureLevel]}
                  onValueChange={(value) => setPreferences(prev => ({ ...prev, adventureLevel: value[0] }))}
                  max={5}
                  min={1}
                  step={1}
                  className="h-2"
                />
              </div>
            </Card>

            {/* Travel Style */}
            <Card className="p-6">
              <h3 className="font-semibold mb-4">Travel Style</h3>
              
              {/* Pace */}
              <div className="mb-4">
                <Label className="text-sm mb-2 block">Pace</Label>
                <div className="grid grid-cols-1 gap-2">
                  {[
                    { value: "relaxed", label: "Relaxed" },
                    { value: "balanced", label: "Balanced" },
                    { value: "packed", label: "Packed" }
                  ].map((option) => (
                    <div
                      key={option.value}
                      onClick={() => setPreferences(prev => ({ ...prev, pace: option.value }))}
                      className={`
                        px-3 py-2 rounded-lg border cursor-pointer transition-all text-sm
                        ${preferences.pace === option.value 
                          ? 'border-sky-500 bg-sky-50 font-medium' 
                          : 'border-gray-200 hover:border-gray-300'
                        }
                      `}
                    >
                      {option.label}
                    </div>
                  ))}
                </div>
              </div>

              {/* Group */}
              <div>
                <Label className="text-sm mb-2 block">Group</Label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { value: "solo", label: "Solo", icon: Users },
                    { value: "couple", label: "Couple", icon: Heart },
                    { value: "family", label: "Family", icon: Baby },
                    { value: "friends", label: "Friends", icon: Users }
                  ].map((option) => {
                    const Icon = option.icon;
                    return (
                      <div
                        key={option.value}
                        onClick={() => setPreferences(prev => ({ ...prev, groupType: option.value }))}
                        className={`
                          p-2 rounded-lg border cursor-pointer transition-all text-center
                          ${preferences.groupType === option.value 
                            ? 'border-sky-500 bg-sky-50' 
                            : 'border-gray-200 hover:border-gray-300'
                          }
                        `}
                      >
                        <Icon className={`h-4 w-4 mx-auto mb-1 ${preferences.groupType === option.value ? 'text-sky-600' : 'text-gray-500'}`} />
                        <div className={`text-xs ${preferences.groupType === option.value ? 'font-medium' : ''}`}>
                          {option.label}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
"use client";

import { useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  ChevronLeft,
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
  Sparkles,
  MapPin,
  Landmark,
  TreePine,
  Theater,
  Waves,
  Dumbbell,
  Baby,
  Star,
  Clock,
  Footprints,
  Compass,
  Check,
  Loader2
} from "lucide-react";

export default function ConsolidatedPreferencesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId");
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState("");
  
  const [preferences, setPreferences] = useState({
    // Activity & Adventure
    walkingTolerance: 3,
    adventureLevel: 3,
    
    // Interests (combined)
    interests: {
      artGalleries: false,
      museums: false,
      historicalSites: false,
      architecture: false,
      liveMusic: false,
      concerts: false,
      theater: false,
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
    
    // Food & Dining (consolidated)
    cuisineTypes: ["Local Cuisine"],
    dietaryRestrictions: [],
    priceRanges: ["$$"],
    
    // Travel Style
    pace: "balanced",
    groupType: "couple",
    
    // Time preferences
    preferredTimes: {
      earlyMorning: false,
      morning: true,
      afternoon: true,
      evening: true,
      lateNight: false,
    }
  });

  const cuisineOptions = [
    "Local Cuisine", "Italian", "French", "Japanese", "Chinese", 
    "Mexican", "Indian", "Thai", "Mediterranean", "American",
    "Korean", "Vietnamese", "Spanish", "Greek", "Turkish",
    "Seafood", "Steakhouse", "Vegetarian", "Vegan", "Street Food"
  ];

  const dietaryOptions = [
    "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", 
    "Halal", "Kosher", "Nut Allergy", "Shellfish Allergy"
  ];

  const interestCategories = [
    {
      title: "Arts & Culture",
      icon: Palette,
      interests: [
        { key: "artGalleries", label: "Art Galleries", icon: Palette },
        { key: "museums", label: "Museums", icon: Building },
        { key: "historicalSites", label: "Historical Sites", icon: Landmark },
        { key: "architecture", label: "Architecture", icon: Building },
        { key: "theater", label: "Theater & Shows", icon: Theater },
      ]
    },
    {
      title: "Entertainment",
      icon: Music,
      interests: [
        { key: "liveMusic", label: "Live Music", icon: Music },
        { key: "concerts", label: "Concerts", icon: Music },
        { key: "bars", label: "Bars & Pubs", icon: Wine },
        { key: "nightclubs", label: "Nightclubs", icon: Sparkles },
      ]
    },
    
    {
      title: "Shopping",
      icon: ShoppingBag,
      interests: [
        { key: "shopping", label: "Shopping", icon: ShoppingBag },
        { key: "localMarkets", label: "Local Markets", icon: MapPin },
      ]
    },
    {
      title: "Nature & Outdoors",
      icon: Mountain,
      interests: [
        { key: "nature", label: "Nature & Parks", icon: TreePine },
        { key: "beaches", label: "Beaches", icon: Waves },
        { key: "hiking", label: "Hiking & Trails", icon: Mountain },
      ]
    },
    {
      title: "Activities",
      icon: Heart,
      interests: [
        { key: "photography", label: "Photography", icon: Camera },
        { key: "wellness", label: "Spa & Wellness", icon: Heart },
        { key: "sports", label: "Sports", icon: Dumbbell },
        { key: "familyActivities", label: "Family", icon: Baby },
      ]
    }
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
    setGenerationProgress(10);
    setProgressMessage("Saving your preferences...");
    
    try {
      // Save preferences and redirect to generation page
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
        })
      });
      
      if (response.ok) {
        // Navigate to itinerary generation page
        router.push(`/generate-itinerary?tripId=${tripId}`);
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Header */}
      <div className="sticky top-0 bg-white/80 backdrop-blur-md z-40 border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
              Personalize Your Trip
            </h1>
            <Button
              size="lg"
              onClick={handleGenerateItinerary}
              disabled={isGenerating}
              className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  Generate Itinerary
                  <ChevronRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8 max-w-6xl">
        {/* All preferences in a single scrollable view */}
        <div className="space-y-6">
          
          {/* Interests Section */}
          <Card>
            <CardHeader>
              <CardTitle>What interests you?</CardTitle>
              <CardDescription>Select all that apply to get personalized recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                {interestCategories.map((category) => (
                  <div key={category.title}>
                    <h3 className="font-medium mb-3 flex items-center gap-2">
                      <category.icon className="h-4 w-4 text-sky-500" />
                      {category.title}
                    </h3>
                    <div className="space-y-2">
                      {category.interests.map((interest) => {
                        const Icon = interest.icon;
                        const isSelected = preferences.interests[interest.key as keyof typeof preferences.interests];
                        return (
                          <div
                            key={interest.key}
                            onClick={() => handleInterestToggle(interest.key)}
                            className={`
                              p-3 rounded-lg border-2 cursor-pointer transition-all flex items-center gap-3
                              ${isSelected 
                                ? 'border-sky-500 bg-sky-50' 
                                : 'border-gray-200 hover:border-gray-300 bg-white'
                              }
                            `}
                          >
                            <Icon className={`h-4 w-4 ${isSelected ? 'text-sky-600' : 'text-gray-500'}`} />
                            <span className={`text-sm ${isSelected ? 'font-medium text-sky-900' : 'text-gray-700'}`}>
                              {interest.label}
                            </span>
                            {isSelected && (
                              <Check className="h-4 w-4 text-sky-600 ml-auto" />
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Food Preferences */}
          <Card>
            <CardHeader>
              <CardTitle>Food & Dining</CardTitle>
              <CardDescription>Help us find the perfect dining experiences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Budget */}
              <div>
                <Label className="mb-3 block">Budget Range</Label>
                <div className="grid grid-cols-4 gap-3">
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
                        <div className="font-semibold text-lg">{price}</div>
                        <div className={`text-xs ${isSelected ? 'text-green-700' : 'text-gray-500'}`}>
                          {labels[price as keyof typeof labels]}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Cuisines */}
              <div>
                <Label className="mb-3 block">Favorite Cuisines</Label>
                <div className="flex flex-wrap gap-2">
                  {cuisineOptions.map((cuisine) => (
                    <Badge
                      key={cuisine}
                      variant={preferences.cuisineTypes.includes(cuisine) ? "default" : "outline"}
                      className="cursor-pointer py-1.5 px-3"
                      onClick={() => handleCuisineToggle(cuisine)}
                    >
                      {preferences.cuisineTypes.includes(cuisine) && (
                        <Check className="h-3 w-3 mr-1" />
                      )}
                      {cuisine}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Dietary */}
              <div>
                <Label className="mb-3 block">Dietary Restrictions</Label>
                <div className="flex flex-wrap gap-2">
                  {dietaryOptions.map((restriction) => (
                    <Badge
                      key={restriction}
                      variant={preferences.dietaryRestrictions.includes(restriction) ? "destructive" : "outline"}
                      className="cursor-pointer py-1.5 px-3"
                      onClick={() => handleDietaryToggle(restriction)}
                    >
                      {preferences.dietaryRestrictions.includes(restriction) && (
                        <Check className="h-3 w-3 mr-1" />
                      )}
                      {restriction}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Activity Level */}
          <Card>
            <CardHeader>
              <CardTitle>Activity Preferences</CardTitle>
              <CardDescription>How active do you want to be?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center gap-2">
                    <Footprints className="h-5 w-5 text-sky-500" />
                    <Label>Walking Tolerance</Label>
                  </div>
                  <span className="text-sm font-medium px-3 py-1 bg-sky-100 text-sky-700 rounded-full">
                    {["Minimal", "Light", "Moderate", "Active", "Very Active"][preferences.walkingTolerance - 1]}
                  </span>
                </div>
                <Slider
                  value={[preferences.walkingTolerance]}
                  onValueChange={(value) => setPreferences(prev => ({ ...prev, walkingTolerance: value[0] }))}
                  max={5}
                  min={1}
                  step={1}
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center gap-2">
                    <Compass className="h-5 w-5 text-sky-500" />
                    <Label>Adventure Level</Label>
                  </div>
                  <span className="text-sm font-medium px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
                    {["Tourist spots", "Popular", "Mixed", "Adventurous", "Explorer"][preferences.adventureLevel - 1]}
                  </span>
                </div>
                <Slider
                  value={[preferences.adventureLevel]}
                  onValueChange={(value) => setPreferences(prev => ({ ...prev, adventureLevel: value[0] }))}
                  max={5}
                  min={1}
                  step={1}
                />
              </div>
            </CardContent>
          </Card>

          {/* Travel Style */}
          <Card>
            <CardHeader>
              <CardTitle>Travel Style</CardTitle>
              <CardDescription>How do you like to travel?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Pace */}
              <div>
                <Label className="mb-4 block">Travel Pace</Label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: "relaxed", label: "Relaxed", desc: "Plenty of downtime" },
                    { value: "balanced", label: "Balanced", desc: "Mix of activities" },
                    { value: "packed", label: "Packed", desc: "See everything" }
                  ].map((option) => (
                    <div
                      key={option.value}
                      onClick={() => setPreferences(prev => ({ ...prev, pace: option.value }))}
                      className={`
                        p-4 rounded-lg border-2 cursor-pointer transition-all text-center
                        ${preferences.pace === option.value 
                          ? 'border-sky-500 bg-sky-50' 
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                        }
                      `}
                    >
                      <div className={`font-medium mb-1 ${preferences.pace === option.value ? 'text-sky-900' : 'text-gray-700'}`}>
                        {option.label}
                      </div>
                      <div className={`text-xs ${preferences.pace === option.value ? 'text-sky-700' : 'text-gray-500'}`}>
                        {option.desc}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Group Type */}
              <div>
                <Label className="mb-4 block">Who's Traveling</Label>
                <div className="grid grid-cols-4 gap-3">
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
                          p-4 rounded-lg border-2 cursor-pointer transition-all text-center
                          ${preferences.groupType === option.value 
                            ? 'border-sky-500 bg-sky-50' 
                            : 'border-gray-200 hover:border-gray-300 bg-white'
                          }
                        `}
                      >
                        <Icon className={`h-6 w-6 mx-auto mb-2 ${preferences.groupType === option.value ? 'text-sky-600' : 'text-gray-500'}`} />
                        <div className={`text-sm font-medium ${preferences.groupType === option.value ? 'text-sky-900' : 'text-gray-700'}`}>
                          {option.label}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
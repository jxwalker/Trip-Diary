"use client";

import { useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Globe, 
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
  DollarSign,
  Users,
  Sparkles,
  MapPin,
  Calendar,
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
  Check
} from "lucide-react";

interface Preferences {
  // Activity levels
  walkingTolerance: number;
  adventureLevel: number;
  
  // Interests with expanded categories
  interests: {
    artGalleries: boolean;
    museums: boolean;
    historicalSites: boolean;
    architecture: boolean;
    liveMusic: boolean;
    concerts: boolean;
    theater: boolean;
    localCuisine: boolean;
    fineDining: boolean;
    streetFood: boolean;
    cafes: boolean;
    bars: boolean;
    nightclubs: boolean;
    shopping: boolean;
    localMarkets: boolean;
    nature: boolean;
    beaches: boolean;
    hiking: boolean;
    photography: boolean;
    wellness: boolean;
    sports: boolean;
    familyActivities: boolean;
  };
  
  // Food preferences
  cuisineTypes: string[];
  dietaryRestrictions: string[];
  priceRanges: string[]; // Multiple selections allowed
  
  // Travel style
  pace: string;
  groupType: string;
  
  // Time preferences
  preferredTimes: {
    earlyMorning: boolean;
    morning: boolean;
    afternoon: boolean;
    evening: boolean;
    lateNight: boolean;
  };
}

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

function PreferencesContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId");
  
  const [currentTab, setCurrentTab] = useState("interests");
  const [preferences, setPreferences] = useState<Preferences>({
    walkingTolerance: 3,
    adventureLevel: 3,
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
    cuisineTypes: ["Local Cuisine"],
    dietaryRestrictions: [],
    priceRanges: ["$$"],
    pace: "balanced",
    groupType: "couple",
    preferredTimes: {
      earlyMorning: false,
      morning: true,
      afternoon: true,
      evening: true,
      lateNight: false,
    }
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);

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
      title: "Shopping & Markets",
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
        { key: "photography", label: "Photography Spots", icon: Camera },
        { key: "wellness", label: "Spa & Wellness", icon: Heart },
        { key: "sports", label: "Sports & Adventure", icon: Dumbbell },
        { key: "familyActivities", label: "Family Activities", icon: Baby },
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

  const handleSliderChange = (field: keyof Preferences, value: number[]) => {
    setPreferences(prev => ({ ...prev, [field]: value[0] }));
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

  const handleTimeToggle = (time: keyof typeof preferences.preferredTimes) => {
    setPreferences(prev => ({
      ...prev,
      preferredTimes: {
        ...prev.preferredTimes,
        [time]: !prev.preferredTimes[time]
      }
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Convert preferences to backend format
      const backendPreferences = {
        walkingTolerance: preferences.walkingTolerance,
        adventureLevel: preferences.adventureLevel,
        artCulture: preferences.interests.artGalleries || preferences.interests.museums ? 5 : 2,
        music: preferences.interests.liveMusic || preferences.interests.concerts ? 5 : 2,
        food: preferences.cuisineTypes.length > 0 ? 5 : 3,
        nightlife: preferences.interests.bars || preferences.interests.nightclubs ? 5 : 2,
        shopping: preferences.interests.shopping || preferences.interests.localMarkets ? 5 : 2,
        nature: preferences.interests.nature || preferences.interests.beaches ? 5 : 2,
        history: preferences.interests.historicalSites ? 5 : 2,
        photography: preferences.interests.photography ? 5 : 2,
        cuisineTypes: preferences.cuisineTypes,
        dietaryRestrictions: preferences.dietaryRestrictions,
        priceRange: preferences.priceRanges.join(","),
        travelStyle: preferences.pace,
        groupType: preferences.groupType,
        specialInterests: Object.entries(preferences.interests)
          .filter(([_, value]) => value)
          .map(([key, _]) => key),
        preferredTimes: preferences.preferredTimes
      };

      const response = await fetch(`/api/proxy/preferences/${tripId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendPreferences)
      });
      
      if (response.ok) {
        // Navigate to real progress page for guide creation
        router.push(`/generate-itinerary?tripId=${tripId}`);
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link href="/summary">
              <Button variant="ghost" size="sm">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <div className="flex items-center space-x-2">
              <Globe className="h-6 w-6 text-sky-500" />
              <span className="text-xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
                TripCraft AI
              </span>
            </div>
          </div>
        </div>
      </nav>

      <div className="pt-24 pb-12 px-6">
        <div className="container mx-auto max-w-5xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-sky-600 bg-clip-text text-transparent">
              Personalize Your Travel Guide
            </h1>
            <p className="text-gray-600 text-lg">
              Tell us what you love and we'll create the perfect itinerary
            </p>
          </motion.div>

          <Tabs value={currentTab} onValueChange={setCurrentTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="interests">Interests</TabsTrigger>
            <TabsTrigger value="food">Food</TabsTrigger>
            <TabsTrigger value="style">Pace & Group</TabsTrigger>
          </TabsList>

            {/* Interests Tab */}
            <TabsContent value="interests" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>What interests you?</CardTitle>
                  <CardDescription>Select all that apply - we'll find the best spots for you</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {interestCategories.map((category) => (
                      <div key={category.title}>
                        <h3 className="font-medium mb-3 flex items-center gap-2">
                          <category.icon className="h-4 w-4 text-sky-500" />
                          {category.title}
                        </h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                          {category.interests.map((interest) => {
                            const Icon = interest.icon;
                            const isSelected = preferences.interests[interest.key as keyof typeof preferences.interests];
                            return (
                              <div
                                key={interest.key}
                                onClick={() => handleInterestToggle(interest.key)}
                                className={`
                                  relative p-3 rounded-lg border-2 cursor-pointer transition-all
                                  ${isSelected 
                                    ? 'border-sky-500 bg-sky-50' 
                                    : 'border-gray-200 hover:border-gray-300 bg-white'
                                  }
                                `}
                              >
                                <div className="flex items-center gap-2">
                                  <Icon className={`h-4 w-4 ${isSelected ? 'text-sky-600' : 'text-gray-500'}`} />
                                  <span className={`text-sm ${isSelected ? 'font-medium text-sky-900' : 'text-gray-700'}`}>
                                    {interest.label}
                                  </span>
                                </div>
                                {isSelected && (
                                  <Check className="absolute top-2 right-2 h-4 w-4 text-sky-600" />
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
            </TabsContent>

            {/* Food & Dining Tab (single place; removed duplicates elsewhere) */}
            <TabsContent value="food" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Food & Dining Preferences</CardTitle>
                  <CardDescription>Help us find the perfect dining experiences</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Price Ranges - Multiple Selection */}
                  <div>
                    <Label className="mb-3 block">Budget Range (select all that apply)</Label>
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

                  {/* Cuisine Types */}
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

                  {/* Dietary Restrictions */}
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
            </TabsContent>

            {/* Pace & Group Tab (combines activity + travel style) */}
            <TabsContent value="style" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Activity & Style</CardTitle>
                  <CardDescription>Set your preferred activity level and pace</CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  <div>
                    <div className="flex justify-between items-center mb-4">
                      <div className="flex items-center gap-2">
                        <Footprints className="h-5 w-5 text-sky-500" />
                        <Label className="text-base">Walking Tolerance</Label>
                      </div>
                      <span className="text-sm font-medium px-3 py-1 bg-sky-100 text-sky-700 rounded-full">
                        {preferences.walkingTolerance === 1 && "Minimal walking"}
                        {preferences.walkingTolerance === 2 && "Light walking"}
                        {preferences.walkingTolerance === 3 && "Moderate walking"}
                        {preferences.walkingTolerance === 4 && "Lots of walking"}
                        {preferences.walkingTolerance === 5 && "Marathon walker"}
                      </span>
                    </div>
                    <Slider
                      value={[preferences.walkingTolerance]}
                      onValueChange={(value) => handleSliderChange('walkingTolerance', value)}
                      max={5}
                      min={1}
                      step={1}
                      className="mb-2"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-4">
                      <div className="flex items-center gap-2">
                        <Compass className="h-5 w-5 text-sky-500" />
                        <Label className="text-base">Adventure Level</Label>
                      </div>
                      <span className="text-sm font-medium px-3 py-1 bg-purple-100 text-purple-700 rounded-full">
                        {preferences.adventureLevel === 1 && "Tourist spots only"}
                        {preferences.adventureLevel === 2 && "Mostly popular"}
                        {preferences.adventureLevel === 3 && "Balanced mix"}
                        {preferences.adventureLevel === 4 && "Some hidden gems"}
                        {preferences.adventureLevel === 5 && "Off the beaten path"}
                      </span>
                    </div>
                    <Slider
                      value={[preferences.adventureLevel]}
                      onValueChange={(value) => handleSliderChange('adventureLevel', value)}
                      max={5}
                      min={1}
                      step={1}
                      className="mb-2"
                    />
                  </div>

                  <div>
                    <Label className="mb-4 block flex items-center gap-2">
                      <Clock className="h-5 w-5 text-sky-500" />
                      Preferred Activity Times
                    </Label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {[
                        { key: "morning", label: "Morning", time: "8am-12pm" },
                        { key: "afternoon", label: "Afternoon", time: "12pm-5pm" },
                        { key: "evening", label: "Evening", time: "5pm-9pm" },
                        { key: "lateNight", label: "Late Night", time: "9pm+" },
                      ].map((period) => {
                        const isSelected = preferences.preferredTimes[period.key as keyof typeof preferences.preferredTimes];
                        return (
                          <div
                            key={period.key}
                            onClick={() => handleTimeToggle(period.key as keyof typeof preferences.preferredTimes)}
                            className={`
                              p-3 rounded-lg border-2 cursor-pointer transition-all
                              ${isSelected 
                                ? 'border-orange-500 bg-orange-50' 
                                : 'border-gray-200 hover:border-gray-300 bg-white'
                              }
                            `}
                          >
                            <div className={`font-medium text-sm ${isSelected ? 'text-orange-900' : 'text-gray-700'}`}>
                              {period.label}
                            </div>
                            <div className={`text-xs ${isSelected ? 'text-orange-700' : 'text-gray-500'}`}>
                              {period.time}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Travel Style (pace/group) */}
              <Card>
                <CardHeader>
                  <CardTitle>Travel Style</CardTitle>
                  <CardDescription>How do you like to travel?</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Travel Pace */}
                  <div>
                    <Label className="mb-4 block">Travel Pace</Label>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      {[
                        { value: "relaxed", label: "Relaxed", desc: "Plenty of downtime" },
                        { value: "balanced", label: "Balanced", desc: "Mix of activities and rest" },
                        { value: "packed", label: "Packed", desc: "See everything possible" }
                      ].map((option) => (
                        <div
                          key={option.value}
                          onClick={() => setPreferences(prev => ({ ...prev, pace: option.value }))}
                          className={`
                            p-4 rounded-lg border-2 cursor-pointer transition-all
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
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
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
            </TabsContent>

            {/* Removed duplicate Travel Style tab to avoid redundancy */}
          </Tabs>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-between items-center mt-8"
          >
            <Link href={`/summary?tripId=${tripId}`}>
              <Button variant="outline" size="lg">
                <ChevronLeft className="h-4 w-4 mr-2" />
                Back to Summary
              </Button>
            </Link>
            
            <Button
              size="lg"
              className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-600 hover:to-blue-700"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Sparkles className="h-4 w-4 mr-2 animate-pulse" />
                  Creating Personalized Guide...
                </>
              ) : (
                <>
                  Generate Travel Guide
                  <ChevronRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default function PreferencesPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <PreferencesContent />
    </Suspense>
  );
}

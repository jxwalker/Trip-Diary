"use client";

import { Suspense } from "react";
import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  ChevronRight,
  Utensils,
  Heart,
  MapPin,
  Settings,
  Sparkles,
  Check,
  Loader2,
  Save,
  User,
  Plus,
  Coffee,
  Wine,
  Palmtree,
  Mountain,
  Building2,
  Music,
  ShoppingBag,
  Camera,
  Baby,
  Dumbbell,
  Theater,
  Palette,
  TreePine,
  Waves,
  Star,
  DollarSign,
  Clock,
  Users,
  Zap,
  BookOpen,
  Download,
  Upload,
  X,
  Info
} from "lucide-react";
import { cn } from "@/lib/utils";
import { inferDefaultsFromDestination } from "@/utils/smartDefaults";

// Quick template configurations
const QUICK_TEMPLATES = {
  foodie: {
    name: "Foodie Explorer",
    icon: Utensils,
    color: "from-orange-500 to-red-500",
    description: "Focus on local cuisine and unique dining experiences"
  },
  culture: {
    name: "Culture Enthusiast",
    icon: Building2,
    color: "from-purple-500 to-pink-500",
    description: "Museums, history, and local culture"
  },
  adventure: {
    name: "Adventure Seeker",
    icon: Mountain,
    color: "from-green-500 to-emerald-500",
    description: "Outdoor activities and exploration"
  },
  relaxation: {
    name: "Relaxation Mode",
    icon: Palmtree,
    color: "from-sky-500 to-blue-500",
    description: "Spa, beaches, and leisure"
  },
  family: {
    name: "Family Fun",
    icon: Baby,
    color: "from-yellow-500 to-orange-500",
    description: "Kid-friendly activities"
  },
  budget: {
    name: "Budget Traveler",
    icon: DollarSign,
    color: "from-gray-500 to-slate-500",
    description: "Cost-effective options"
  }
};

function ModernPreferencesPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId");
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState("quick");
  const [profileName, setProfileName] = useState("My Travel Profile");
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  
  // Consolidated preferences state
  const [preferences, setPreferences] = useState({
    // Profile info
    profileName: "My Travel Profile",
    
    // Dining - All in one place
    dining: {
      cuisineTypes: ["Local Cuisine"],
      dietaryRestrictions: [],
      priceRanges: ["$$", "$$$"], // Multiple selections enabled
      mealPreferences: {
        breakfast: true,
        lunch: true,
        dinner: true,
        streetFood: false,
        fineDining: false,
        cafes: true,
        bars: false
      }
    },
    
    // Interests - Organized by category
    interests: {
      culture: {
        artGalleries: false,
        museums: false,
        historicalSites: false,
        architecture: false,
        theaters: false,
        localCulture: true
      },
      entertainment: {
        liveMusic: false,
        nightclubs: false,
        barsPubs: false,
        comedyClubs: false
      },
      outdoors: {
        natureParks: false,
        beaches: false,
        hiking: false,
        waterSports: false,
        cycling: false
      },
      lifestyle: {
        shopping: false,
        localMarkets: false,
        spaWellness: false,
        photography: false,
        cookingClasses: false,
        wineTasting: false
      },
      family: {
        kidFriendly: false,
        playgrounds: false,
        zoosAquariums: false,
        themeParks: false
      }
    },
    
    // Travel style
    travelStyle: {
      pace: "balanced",
      groupType: "couple",
      activityLevel: 3,
      adventureLevel: 3
    },
    
    // Time preferences
    timePreferences: {
      earlyMorning: false,
      morning: true,
      afternoon: true,
      evening: true,
      lateNight: false
    }
  });

  // Cuisine options
  const cuisineOptions = [
    { name: "Local Cuisine", icon: MapPin },
    { name: "Italian", icon: Coffee },
    { name: "Asian", icon: Utensils },
    { name: "Mediterranean", icon: Palmtree },
    { name: "American", icon: Utensils },
    { name: "Mexican", icon: Utensils },
    { name: "Indian", icon: Utensils },
    { name: "French", icon: Wine },
    { name: "Seafood", icon: Waves },
    { name: "Steakhouse", icon: Utensils },
    { name: "Vegetarian", icon: TreePine },
    { name: "Street Food", icon: MapPin }
  ];

  const dietaryOptions = [
    "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free",
    "Halal", "Kosher", "Nut Allergy", "Shellfish Allergy"
  ];

  const priceRanges = [
    { value: "$", label: "Budget", description: "Under $15" },
    { value: "$$", label: "Moderate", description: "$15-30" },
    { value: "$$$", label: "Upscale", description: "$30-60" },
    { value: "$$$$", label: "Luxury", description: "$60+" }
  ];

  // Apply quick template
  const applyTemplate = (templateKey: string) => {
    setSelectedTemplate(templateKey);
    
    const templates: any = {
      foodie: {
        dining: {
          ...preferences.dining,
          mealPreferences: {
            ...preferences.dining.mealPreferences,
            streetFood: true,
            fineDining: true,
            cafes: true
          },
          priceRanges: ["$$", "$$$"]
        },
        interests: {
          ...preferences.interests,
          lifestyle: {
            ...preferences.interests.lifestyle,
            cookingClasses: true,
            wineTasting: true,
            localMarkets: true
          }
        }
      },
      culture: {
        interests: {
          ...preferences.interests,
          culture: {
            artGalleries: true,
            museums: true,
            historicalSites: true,
            architecture: true,
            localCulture: true,
            theaters: true
          }
        },
        travelStyle: {
          ...preferences.travelStyle,
          pace: "balanced"
        }
      },
      adventure: {
        interests: {
          ...preferences.interests,
          outdoors: {
            natureParks: true,
            hiking: true,
            waterSports: true,
            cycling: true,
            beaches: false
          }
        },
        travelStyle: {
          ...preferences.travelStyle,
          activityLevel: 5,
          adventureLevel: 5,
          pace: "packed"
        }
      },
      relaxation: {
        interests: {
          ...preferences.interests,
          lifestyle: {
            ...preferences.interests.lifestyle,
            spaWellness: true
          },
          outdoors: {
            ...preferences.interests.outdoors,
            beaches: true,
            natureParks: true
          }
        },
        travelStyle: {
          ...preferences.travelStyle,
          pace: "relaxed",
          activityLevel: 2
        }
      },
      family: {
        interests: {
          ...preferences.interests,
          family: {
            kidFriendly: true,
            playgrounds: true,
            zoosAquariums: true,
            themeParks: true
          }
        },
        travelStyle: {
          ...preferences.travelStyle,
          groupType: "family"
        }
      },
      budget: {
        dining: {
          ...preferences.dining,
          priceRanges: ["$", "$$"]
        }
      }
    };

    if (templates[templateKey]) {
      setPreferences(prev => ({
        ...prev,
        ...templates[templateKey]
      }));
    }
  };

  // Apply destination-based smart defaults (Quick Start)
  const applyDestinationDefaultsFromSession = () => {
    try {
      if (!tripId) return;
      const key = `tripcraft.trip.${tripId}.destination`;
      const dest = sessionStorage.getItem(key);
      if (!dest) return;
      const patch = inferDefaultsFromDestination(dest);
      setPreferences((prev: any) => ({
        ...prev,
        ...(patch.dining ? { dining: { ...prev.dining, ...patch.dining } } : {}),
        ...(patch.interests ? { interests: deepMerge(prev.interests, patch.interests) } : {}),
        ...(patch.travelStyle ? { travelStyle: { ...prev.travelStyle, ...patch.travelStyle } } : {}),
      }));
    } catch (e) {}
  };

  const deepMerge = (a: any, b: any) => {
    const out = { ...a };
    for (const k of Object.keys(b || {})) {
      out[k] = typeof b[k] === 'object' && b[k] !== null ? deepMerge(a?.[k] || {}, b[k]) : b[k];
    }
    return out;
  };

  // Save profile
  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      const response = await fetch(`/api/proxy/profile/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tripId,
          profile: preferences
        })
      });
      
      if (response.ok) {
        // Show success toast or notification
      }
    } catch (error) {
      console.error('Error saving profile:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Generate itinerary
  const handleGenerateItinerary = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch(`/api/proxy/preferences/${tripId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preferences)
      });
      
      if (response.ok) {
        router.push(`/generate-itinerary?tripId=${tripId}`);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  // Toggle functions for multi-select
  const toggleCuisine = (cuisine: string) => {
    setPreferences(prev => ({
      ...prev,
      dining: {
        ...prev.dining,
        cuisineTypes: prev.dining.cuisineTypes.includes(cuisine)
          ? prev.dining.cuisineTypes.filter(c => c !== cuisine)
          : [...prev.dining.cuisineTypes, cuisine]
      }
    }));
  };

  const togglePriceRange = (price: string) => {
    setPreferences(prev => ({
      ...prev,
      dining: {
        ...prev.dining,
        priceRanges: prev.dining.priceRanges.includes(price)
          ? prev.dining.priceRanges.filter(p => p !== price)
          : [...prev.dining.priceRanges, price]
      }
    }));
  };

  const toggleInterest = (category: string, interest: string) => {
    setPreferences(prev => ({
      ...prev,
      interests: {
        ...prev.interests,
        [category]: {
          ...prev.interests[category as keyof typeof prev.interests],
          [interest]: !prev.interests[category as keyof typeof prev.interests][interest as any]
        }
      }
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Header with Profile */}
      <div className="sticky top-0 bg-white/90 backdrop-blur-md z-40 border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Avatar className="h-10 w-10">
                <AvatarFallback>
                  <User className="h-5 w-5" />
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-xl font-bold">Travel Preferences</h1>
                <p className="text-sm text-gray-500">{profileName}</p>
              </div>
            </div>
            
              <div className="flex items-center gap-3">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={applyDestinationDefaultsFromSession}
                >
                  Quick Start
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSaveProfile}
                  disabled={isSaving}
                >
                {isSaving ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Save className="h-4 w-4" />
                )}
                <span className="ml-2 hidden sm:inline">Save Profile</span>
              </Button>
              
              <Button
                size="sm"
                onClick={handleGenerateItinerary}
                disabled={isGenerating}
                className="bg-gradient-to-r from-sky-500 to-blue-600"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
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
      </div>

      <div className="container mx-auto px-6 py-8 max-w-7xl">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-3">
            <TabsTrigger value="quick">Quick Start</TabsTrigger>
            <TabsTrigger value="custom">Customize</TabsTrigger>
            <TabsTrigger value="saved">Saved</TabsTrigger>
          </TabsList>

          {/* Quick Start Tab */}
          <TabsContent value="quick" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Choose a Travel Style</CardTitle>
                <CardDescription>
                  Select a template to quickly set your preferences, or customize them in detail
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(QUICK_TEMPLATES).map(([key, template]) => {
                    const Icon = template.icon;
                    const isSelected = selectedTemplate === key;
                    
                    return (
                      <motion.div
                        key={key}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Card
                          className={cn(
                            "cursor-pointer transition-all relative overflow-hidden",
                            isSelected && "ring-2 ring-sky-500"
                          )}
                          onClick={() => applyTemplate(key)}
                        >
                          <div className={cn(
                            "absolute inset-0 opacity-10 bg-gradient-to-br",
                            template.color
                          )} />
                          <CardContent className="relative p-6">
                            <div className="flex flex-col items-center text-center space-y-3">
                              <div className={cn(
                                "p-3 rounded-xl bg-gradient-to-br text-white",
                                template.color
                              )}>
                                <Icon className="h-6 w-6" />
                              </div>
                              <div>
                                <h3 className="font-semibold">{template.name}</h3>
                                <p className="text-xs text-gray-500 mt-1">
                                  {template.description}
                                </p>
                              </div>
                              {isSelected && (
                                <Badge className="absolute top-2 right-2 bg-sky-500">
                                  <Check className="h-3 w-3 mr-1" />
                                  Selected
                                </Badge>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    );
                  })}
                </div>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <div className="flex gap-2">
                    <Info className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-blue-900">
                      <p className="font-medium mb-1">Quick Start Tips:</p>
                      <ul className="space-y-1 text-blue-700">
                        <li>• Templates are just starting points - customize further in the next tab</li>
                        <li>• You can save multiple profiles for different trip types</li>
                        <li>• Your preferences help us find real, current recommendations</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Customize Tab */}
          <TabsContent value="custom" className="space-y-6">
            {/* Dining Preferences - All in One */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Utensils className="h-5 w-5 text-orange-500" />
                  Dining Preferences
                </CardTitle>
                <CardDescription>
                  All your food preferences in one place
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Price Ranges - Multiple Selection */}
                <div>
                  <Label className="text-base font-medium mb-3 block">
                    Budget Range (select all that apply)
                  </Label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {priceRanges.map((range) => {
                      const isSelected = preferences.dining.priceRanges.includes(range.value);
                      return (
                        <button
                          type="button"
                          key={range.value}
                          onClick={() => togglePriceRange(range.value)}
                          aria-pressed={isSelected}
                          className={cn(
                            "p-4 rounded-lg border-2 transition-all text-left touch-target w-full",
                            isSelected
                              ? "border-green-500 bg-green-50"
                              : "border-gray-200 hover:border-gray-300 bg-white"
                          )}
                        >
                          <div className="text-center">
                            <div className="font-bold text-lg">{range.value}</div>
                            <div className="text-sm font-medium">{range.label}</div>
                            <div className="text-xs text-gray-500 mt-1">
                              {range.description}
                            </div>
                            {isSelected && (
                              <Check className="h-4 w-4 text-green-600 mx-auto mt-2" />
                            )}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <Separator />

                {/* Cuisines */}
                <div>
                  <Label className="text-base font-medium mb-3 block">
                    Favorite Cuisines
                  </Label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {cuisineOptions.map((cuisine) => {
                      const Icon = cuisine.icon;
                      const isSelected = preferences.dining.cuisineTypes.includes(cuisine.name);
                      return (
                        <button
                          type="button"
                          key={cuisine.name}
                          onClick={() => toggleCuisine(cuisine.name)}
                          aria-pressed={isSelected}
                          className={cn(
                            "p-3 rounded-lg border-2 transition-all flex items-center gap-2 touch-target w-full text-left",
                            isSelected
                              ? "border-orange-500 bg-orange-50"
                              : "border-gray-200 hover:border-gray-300 bg-white"
                          )}
                        >
                          <Icon className={cn(
                            "h-4 w-4",
                            isSelected ? "text-orange-600" : "text-gray-500"
                          )} />
                          <span className={cn(
                            "text-sm",
                            isSelected ? "font-medium text-orange-900" : "text-gray-700"
                          )}>
                            {cuisine.name}
                          </span>
                          {isSelected && (
                            <Check className="h-3 w-3 text-orange-600 ml-auto" />
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <Separator />

                {/* Meal Types */}
                <div>
                  <Label className="text-base font-medium mb-3 block">
                    Meal Preferences
                  </Label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Object.entries({
                      breakfast: "Breakfast",
                      lunch: "Lunch",
                      dinner: "Dinner",
                      streetFood: "Street Food",
                      fineDining: "Fine Dining",
                      cafes: "Cafés",
                      bars: "Bars"
                    }).map(([key, label]) => {
                      const isSelected = preferences.dining.mealPreferences[key as keyof typeof preferences.dining.mealPreferences];
                      return (
                        <button
                          type="button"
                          key={key}
                          onClick={() => setPreferences(prev => ({
                            ...prev,
                            dining: {
                              ...prev.dining,
                              mealPreferences: {
                                ...prev.dining.mealPreferences,
                                [key]: !isSelected
                              }
                            }
                          }))}
                          aria-pressed={isSelected}
                          className={cn(
                            "p-3 rounded-lg border transition-all touch-target text-left",
                            isSelected
                              ? "border-sky-500 bg-sky-50"
                              : "border-gray-200 hover:border-gray-300"
                          )}
                        >
                          <span className={cn(
                            "text-sm",
                            isSelected ? "font-medium" : ""
                          )}>
                            {label}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <Separator />

                {/* Dietary Restrictions */}
                <div>
                  <Label className="text-base font-medium mb-3 block">
                    Dietary Restrictions
                  </Label>
                  <div className="flex flex-wrap gap-2">
                    {dietaryOptions.map((restriction) => {
                      const isSelected = preferences.dining.dietaryRestrictions.includes(restriction);
                      return (
                        <Badge
                          key={restriction}
                          variant={isSelected ? "destructive" : "outline"}
                          className="cursor-pointer py-1.5 px-3"
                          onClick={() => setPreferences(prev => ({
                            ...prev,
                            dining: {
                              ...prev.dining,
                              dietaryRestrictions: isSelected
                                ? prev.dining.dietaryRestrictions.filter(r => r !== restriction)
                                : [...prev.dining.dietaryRestrictions, restriction]
                            }
                          }))}
                        >
                          {isSelected && <Check className="h-3 w-3 mr-1" />}
                          {restriction}
                        </Badge>
                      );
                    })}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Interests & Activities */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="h-5 w-5 text-pink-500" />
                  Interests & Activities
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {Object.entries({
                    culture: { icon: Building2, label: "Arts & Culture", color: "purple" },
                    entertainment: { icon: Music, label: "Entertainment", color: "pink" },
                    outdoors: { icon: Mountain, label: "Outdoors", color: "green" },
                    lifestyle: { icon: Sparkles, label: "Lifestyle", color: "amber" },
                    family: { icon: Baby, label: "Family", color: "blue" }
                  }).map(([category, config]) => {
                    const Icon = config.icon;
                    const interests = preferences.interests[category as keyof typeof preferences.interests];
                    
                    return (
                      <div key={category}>
                        <div className="flex items-center gap-2 mb-3">
                          <Icon className={`h-4 w-4 text-${config.color}-500`} />
                          <Label className="text-base font-medium">{config.label}</Label>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                          {Object.entries(interests).map(([key, value]) => {
                            const label = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
                            return (
                              <button
                                type="button"
                                key={key}
                                onClick={() => toggleInterest(category, key)}
                                aria-pressed={value}
                                className={cn(
                                  "p-2.5 rounded-lg border transition-all text-sm touch-target text-left w-full",
                                  value
                                    ? `border-${config.color}-500 bg-${config.color}-50`
                                    : "border-gray-200 hover:border-gray-300"
                                )}
                              >
                                <div className="flex items-center justify-between">
                                  <span>{label}</span>
                                  {value && <Check className="h-3 w-3 ml-2" />}
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Travel Style */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5 text-gray-500" />
                  Travel Style
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Activity Level Slider */}
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <Label>Activity Level</Label>
                    <Badge variant="outline">
                      {["Minimal", "Light", "Moderate", "Active", "Very Active"][preferences.travelStyle.activityLevel - 1]}
                    </Badge>
                  </div>
                  <Slider
                    value={[preferences.travelStyle.activityLevel]}
                    onValueChange={(value) => setPreferences(prev => ({
                      ...prev,
                      travelStyle: {
                        ...prev.travelStyle,
                        activityLevel: value[0]
                      }
                    }))}
                    max={5}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Travel Pace */}
                <div>
                  <Label className="mb-3 block">Travel Pace</Label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { value: "relaxed", label: "Relaxed", icon: Coffee },
                      { value: "balanced", label: "Balanced", icon: Clock },
                      { value: "packed", label: "Packed", icon: Zap }
                    ].map((option) => {
                      const Icon = option.icon;
                      const isSelected = preferences.travelStyle.pace === option.value;
                      return (
                        <div
                          key={option.value}
                          onClick={() => setPreferences(prev => ({
                            ...prev,
                            travelStyle: {
                              ...prev.travelStyle,
                              pace: option.value
                            }
                          }))}
                          className={cn(
                            "p-4 rounded-lg border-2 cursor-pointer transition-all text-center",
                            isSelected
                              ? "border-sky-500 bg-sky-50"
                              : "border-gray-200 hover:border-gray-300"
                          )}
                        >
                          <Icon className={cn(
                            "h-6 w-6 mx-auto mb-2",
                            isSelected ? "text-sky-600" : "text-gray-500"
                          )} />
                          <span className="text-sm font-medium">{option.label}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Group Type */}
                <div>
                  <Label className="mb-3 block">Who's Traveling</Label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {[
                      { value: "solo", label: "Solo", icon: User },
                      { value: "couple", label: "Couple", icon: Heart },
                      { value: "family", label: "Family", icon: Users },
                      { value: "friends", label: "Friends", icon: Users }
                    ].map((option) => {
                      const Icon = option.icon;
                      const isSelected = preferences.travelStyle.groupType === option.value;
                      return (
                        <div
                          key={option.value}
                          onClick={() => setPreferences(prev => ({
                            ...prev,
                            travelStyle: {
                              ...prev.travelStyle,
                              groupType: option.value
                            }
                          }))}
                          className={cn(
                            "p-3 rounded-lg border-2 cursor-pointer transition-all text-center",
                            isSelected
                              ? "border-sky-500 bg-sky-50"
                              : "border-gray-200 hover:border-gray-300"
                          )}
                        >
                          <Icon className={cn(
                            "h-5 w-5 mx-auto mb-1",
                            isSelected ? "text-sky-600" : "text-gray-500"
                          )} />
                          <span className="text-sm">{option.label}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Saved Profiles Tab */}
          <TabsContent value="saved" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Saved Profiles</CardTitle>
                <CardDescription>
                  Load a previously saved preference profile
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <User className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p>No saved profiles yet</p>
                  <p className="text-sm mt-1">Save your current preferences to reuse them later</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Summary Card */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-base">Current Selection Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary">
                {preferences.travelStyle.groupType} traveler
              </Badge>
              <Badge variant="secondary">
                {preferences.travelStyle.pace} pace
              </Badge>
              {preferences.dining.priceRanges.map(range => (
                <Badge key={range} variant="secondary">
                  {range}
                </Badge>
              ))}
              {preferences.dining.cuisineTypes.slice(0, 3).map(cuisine => (
                <Badge key={cuisine} variant="secondary">
                  {cuisine}
                </Badge>
              ))}
              {Object.entries(preferences.interests).map(([category, interests]) => {
                const activeCount = Object.values(interests).filter(v => v).length;
                if (activeCount > 0) {
                  return (
                    <Badge key={category} variant="secondary">
                      {activeCount} {category} interests
                    </Badge>
                  );
                }
                return null;
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function ModernPreferencesPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ModernPreferencesPageContent />
    </Suspense>
  );
}
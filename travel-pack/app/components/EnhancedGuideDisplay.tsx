"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  MapPin, 
  Calendar,
  Utensils,
  Camera,
  Music,
  Info,
  Star,
  Clock,
  DollarSign,
  Navigation,
  Sparkles,
  Map,
  Newspaper,
  Sun,
  ChevronRight,
  Globe,
  Heart,
  BookOpen,
  Lightbulb
} from "lucide-react";

interface EnhancedGuideDisplayProps {
  guide: any;
  tripId: string;
}

export default function EnhancedGuideDisplay({ guide, tripId }: EnhancedGuideDisplayProps) {
  if (!guide) return null;

  // Parse raw content if it exists
  const hasRawContent = guide.raw_content && typeof guide.raw_content === 'string';
  
  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      {guide.summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="border-2 border-sky-200 bg-gradient-to-br from-sky-50 to-blue-50">
            <CardHeader>
              <CardTitle className="flex items-center text-2xl">
                <Sparkles className="h-6 w-6 mr-2 text-sky-500" />
                Your Personalized Travel Guide
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {guide.summary}
              </p>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Main Content Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Tabs defaultValue="itinerary" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
            <TabsTrigger value="dining">Dining</TabsTrigger>
            <TabsTrigger value="attractions">Attractions</TabsTrigger>
            <TabsTrigger value="events">Events</TabsTrigger>
            <TabsTrigger value="insights">Local Insights</TabsTrigger>
          </TabsList>

          {/* Daily Itinerary Tab */}
          <TabsContent value="itinerary" className="space-y-4 mt-4">
            {guide.daily_itinerary && guide.daily_itinerary.length > 0 ? (
              guide.daily_itinerary.map((day: any, index: number) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Calendar className="h-5 w-5 mr-2 text-sky-500" />
                      {day.title || `Day ${day.day}`}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {day.activities && day.activities.map((activity: string, actIndex: number) => (
                        <div key={actIndex} className="flex items-start gap-3">
                          <ChevronRight className="h-4 w-4 text-sky-500 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-gray-700">{activity}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : hasRawContent ? (
              <Card>
                <CardContent className="pt-6">
                  <ScrollArea className="h-[600px] pr-4">
                    <div className="prose prose-sm max-w-none">
                      <div className="whitespace-pre-wrap">
                        {guide.raw_content.split('## Daily Itinerary')[1]?.split('##')[0] || 
                         guide.raw_content.split('## Your Personalized Itinerary')[1]?.split('##')[0] ||
                         "No itinerary available yet. Please set your preferences to generate a personalized itinerary."}
                      </div>
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-gray-500 text-center">No itinerary generated yet.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Dining Tab */}
          <TabsContent value="dining" className="space-y-4 mt-4">
            {guide.restaurants && guide.restaurants.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {guide.restaurants.map((restaurant: any, index: number) => (
                  <Card key={index} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center">
                          <Utensils className="h-4 w-4 mr-2 text-orange-500" />
                          {restaurant.name}
                        </span>
                        {restaurant.rating && (
                          <Badge variant="outline" className="ml-2">
                            <Star className="h-3 w-3 mr-1 fill-yellow-500 text-yellow-500" />
                            {restaurant.rating}
                          </Badge>
                        )}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 mb-3">{restaurant.description}</p>
                      {restaurant.details && restaurant.details.length > 0 && (
                        <div className="space-y-1">
                          {restaurant.details.map((detail: string, idx: number) => (
                            <p key={idx} className="text-xs text-gray-500">• {detail}</p>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : hasRawContent ? (
              <Card>
                <CardContent className="pt-6">
                  <ScrollArea className="h-[600px] pr-4">
                    <div className="prose prose-sm max-w-none">
                      <div className="whitespace-pre-wrap">
                        {guide.raw_content.split('## Dining Guide')[1]?.split('##')[0] ||
                         guide.raw_content.split('## Restaurant')[1]?.split('##')[0] ||
                         "Restaurant recommendations will appear here after preferences are set."}
                      </div>
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-gray-500 text-center">No dining recommendations yet.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Attractions Tab */}
          <TabsContent value="attractions" className="space-y-4 mt-4">
            {guide.attractions && guide.attractions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {guide.attractions.map((attraction: any, index: number) => (
                  <Card key={index} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Camera className="h-4 w-4 mr-2 text-purple-500" />
                        {attraction.name}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge variant="outline" className="mb-2">{attraction.type}</Badge>
                      <p className="text-sm text-gray-600">{attraction.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : hasRawContent ? (
              <Card>
                <CardContent className="pt-6">
                  <ScrollArea className="h-[600px] pr-4">
                    <div className="prose prose-sm max-w-none">
                      <div className="whitespace-pre-wrap">
                        {guide.raw_content.split('## Cultural & Entertainment')[1]?.split('##')[0] ||
                         guide.raw_content.split('## Must-See Attractions')[1]?.split('##')[0] ||
                         "Attraction recommendations will appear here."}
                      </div>
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-gray-500 text-center">No attractions listed yet.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Events Tab */}
          <TabsContent value="events" className="space-y-4 mt-4">
            {guide.events && guide.events.length > 0 ? (
              <div className="space-y-3">
                {guide.events.map((event: any, index: number) => (
                  <Card key={index}>
                    <CardContent className="pt-4">
                      <div className="flex items-start gap-3">
                        <Music className="h-4 w-4 text-green-500 mt-0.5" />
                        <p className="text-sm text-gray-700">{event.description || event}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : hasRawContent ? (
              <Card>
                <CardContent className="pt-6">
                  <ScrollArea className="h-[600px] pr-4">
                    <div className="prose prose-sm max-w-none">
                      <div className="whitespace-pre-wrap">
                        {guide.raw_content.split('## Events')[1]?.split('##')[0] ||
                         "Events and activities will be listed here."}
                      </div>
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-gray-500 text-center">No events found for your dates.</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Local Insights Tab */}
          <TabsContent value="insights" className="space-y-4 mt-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Lightbulb className="h-5 w-5 mr-2 text-yellow-500" />
                  Destination Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                {guide.destination_insights ? (
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {guide.destination_insights}
                  </p>
                ) : hasRawContent ? (
                  <ScrollArea className="h-[400px] pr-4">
                    <div className="prose prose-sm max-w-none">
                      <div className="whitespace-pre-wrap">
                        {guide.raw_content.split('## Destination Insights')[1]?.split('##')[0] ||
                         guide.raw_content.split('## Local Insights')[1]?.split('##')[0] ||
                         "Local insights and tips will appear here."}
                      </div>
                    </div>
                  </ScrollArea>
                ) : (
                  <p className="text-gray-500">No local insights available yet.</p>
                )}
              </CardContent>
            </Card>

            {/* Practical Information */}
            {guide.practical_info && Object.keys(guide.practical_info).length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Info className="h-5 w-5 mr-2 text-blue-500" />
                    Practical Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(guide.practical_info).map(([category, items]: [string, any]) => (
                      <div key={category}>
                        <h4 className="font-medium text-sm mb-2 capitalize">{category}</h4>
                        <div className="space-y-1">
                          {Array.isArray(items) ? items.map((item: string, idx: number) => (
                            <p key={idx} className="text-xs text-gray-600 pl-4">• {item}</p>
                          )) : (
                            <p className="text-xs text-gray-600 pl-4">{items}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Hidden Gems */}
            {guide.hidden_gems && guide.hidden_gems.length > 0 && (
              <Card className="border-2 border-purple-200">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Heart className="h-5 w-5 mr-2 text-purple-500" />
                    Hidden Gems & Local Secrets
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {guide.hidden_gems.map((gem: any, index: number) => (
                      <div key={index} className="flex items-start gap-3">
                        <Star className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-gray-700">
                          {typeof gem === 'string' ? gem : gem.description}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </motion.div>

      {/* Citations */}
      {guide.citations && guide.citations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card className="bg-gray-50">
            <CardHeader>
              <CardTitle className="text-sm flex items-center">
                <BookOpen className="h-4 w-4 mr-2" />
                Sources
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {guide.citations.map((citation: any, index: number) => (
                  <a 
                    key={index}
                    href={citation.url || citation}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline block"
                  >
                    {citation.title || citation.url || citation}
                  </a>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Full Raw Content (Optional - for debugging or detailed view) */}
      {hasRawContent && (
        <details className="mt-8">
          <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
            View Full Generated Content
          </summary>
          <Card className="mt-4">
            <CardContent className="pt-6">
              <ScrollArea className="h-[600px] pr-4">
                <div className="prose prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-xs">
                    {guide.raw_content}
                  </div>
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </details>
      )}
    </div>
  );
}
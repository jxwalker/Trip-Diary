"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import {
  CalendarIcon,
  Plane,
  Hotel,
  MapPin,
  ArrowRight,
  Info,
  Plus,
  Trash2,
  Loader2,
  Car,
  Train
} from "lucide-react";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { useRouter } from "next/navigation";

interface FlightData {
  airline: string;
  flightNumber: string;
  departure: string;
  arrival: string;
  date: Date | undefined;
}

interface TripData {
  destination: {
    city: string;
    country: string;
  };
  dates: {
    startDate: Date | undefined;
    endDate: Date | undefined;
  };
  flights: {
    outbound: FlightData;
    return: FlightData;
  };
  hotel: {
    name: string;
    address: string;
  };
}

export default function CreateTripPage() {
  console.log("CREATE TRIP PAGE LOADED - TRANSPORTATION MODE ENABLED!");
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transportMode, setTransportMode] = useState<"flight" | "car" | "train">("flight");
  
  const [tripData, setTripData] = useState<TripData>({
    destination: {
      city: "",
      country: ""
    },
    dates: {
      startDate: undefined,
      endDate: undefined
    },
    flights: {
      outbound: {
        airline: "",
        flightNumber: "",
        departure: "",
        arrival: "",
        date: undefined
      },
      return: {
        airline: "",
        flightNumber: "",
        departure: "",
        arrival: "",
        date: undefined
      }
    },
    hotel: {
      name: "",
      address: ""
    }
  });

  const handleSubmit = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      // Build flights array only if flight data is provided
      const flights = [];
      
      // Add outbound flight only if it has data
      if (tripData.flights.outbound.airline || tripData.flights.outbound.flightNumber) {
        flights.push({
          airline: tripData.flights.outbound.airline,
          flight_number: tripData.flights.outbound.flightNumber,
          departure_airport: tripData.flights.outbound.departure,
          arrival_airport: tripData.flights.outbound.arrival,
          departure_date: tripData.flights.outbound.date ? format(tripData.flights.outbound.date, "yyyy-MM-dd") : null,
          arrival_date: tripData.flights.outbound.date ? format(tripData.flights.outbound.date, "yyyy-MM-dd") : null,
        });
      }
      
      // Add return flight only if it has data
      if (tripData.flights.return.airline || tripData.flights.return.flightNumber) {
        flights.push({
          airline: tripData.flights.return.airline,
          flight_number: tripData.flights.return.flightNumber,
          departure_airport: tripData.flights.return.departure,
          arrival_airport: tripData.flights.return.arrival,
          departure_date: tripData.flights.return.date ? format(tripData.flights.return.date, "yyyy-MM-dd") : null,
          arrival_date: tripData.flights.return.date ? format(tripData.flights.return.date, "yyyy-MM-dd") : null,
        });
      }
      
      // Format the data for the backend
      const formattedData = {
        flights: flights,
        hotels: [{
          name: tripData.hotel.name,
          address: tripData.hotel.address,
          city: tripData.destination.city,
          check_in_date: tripData.dates.startDate ? format(tripData.dates.startDate, "yyyy-MM-dd") : null,
          check_out_date: tripData.dates.endDate ? format(tripData.dates.endDate, "yyyy-MM-dd") : null,
        }],
        trip_details: {
          destination: `${tripData.destination.city}, ${tripData.destination.country}`,
          start_date: tripData.dates.startDate ? format(tripData.dates.startDate, "yyyy-MM-dd") : null,
          end_date: tripData.dates.endDate ? format(tripData.dates.endDate, "yyyy-MM-dd") : null,
          transportation_mode: transportMode
        }
      };

      // Send as form data with JSON string
      const formData = new FormData();
      formData.append("trip_details", JSON.stringify(formattedData));
      formData.append("use_vision", "false");

      const response = await fetch("/api/proxy/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to create trip: ${response.status}`);
      }

      const data = await response.json();
      const tripId = data.trip_id;

      // Wait briefly for processing
      setTimeout(() => {
        router.push(`/preferences-modern?tripId=${tripId}`);
      }, 1500);

    } catch (err: any) {
      console.error("Error creating trip:", err);
      setError(err.message || "Failed to create trip");
      setIsProcessing(false);
    }
  };

  const isFormValid = () => {
    // Basic required fields
    const hasBasicInfo = (
      tripData.destination.city &&
      tripData.destination.country &&
      tripData.dates.startDate &&
      tripData.dates.endDate &&
      tripData.hotel.name
    );
    
    // Only require flight info if flight mode is selected
    if (transportMode === "flight") {
      return hasBasicInfo && 
        tripData.flights.outbound.airline &&
        tripData.flights.outbound.flightNumber;
    }
    
    // For car/train, just need basic info
    return hasBasicInfo;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Create Your Trip Manually
          </h1>
          <p className="text-lg text-gray-600">
            Enter your travel details and we'll create your perfect itinerary
          </p>
        </motion.div>

        {/* Main Form */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="p-8 shadow-xl bg-white">
            <div className="space-y-8">
              {/* Destination Section */}
              <div>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-blue-500" />
                  Destination
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="city">City *</Label>
                    <Input
                      id="city"
                      placeholder="e.g., Paris"
                      value={tripData.destination.city}
                      onChange={(e) => setTripData(prev => ({
                        ...prev,
                        destination: { ...prev.destination, city: e.target.value }
                      }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="country">Country *</Label>
                    <Input
                      id="country"
                      placeholder="e.g., France"
                      value={tripData.destination.country}
                      onChange={(e) => setTripData(prev => ({
                        ...prev,
                        destination: { ...prev.destination, country: e.target.value }
                      }))}
                    />
                  </div>
                </div>
              </div>

              {/* Travel Dates Section */}
              <div>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <CalendarIcon className="h-5 w-5 text-blue-500" />
                  Travel Dates
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Start Date *</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !tripData.dates.startDate && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {tripData.dates.startDate ? (
                            format(tripData.dates.startDate, "PPP")
                          ) : (
                            <span>Pick a date</span>
                          )}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={tripData.dates.startDate}
                          onSelect={(date) => setTripData(prev => ({
                            ...prev,
                            dates: { ...prev.dates, startDate: date },
                            flights: {
                              ...prev.flights,
                              outbound: { ...prev.flights.outbound, date }
                            }
                          }))}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                  <div>
                    <Label>End Date *</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !tripData.dates.endDate && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {tripData.dates.endDate ? (
                            format(tripData.dates.endDate, "PPP")
                          ) : (
                            <span>Pick a date</span>
                          )}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0">
                        <Calendar
                          mode="single"
                          selected={tripData.dates.endDate}
                          onSelect={(date) => setTripData(prev => ({
                            ...prev,
                            dates: { ...prev.dates, endDate: date },
                            flights: {
                              ...prev.flights,
                              return: { ...prev.flights.return, date }
                            }
                          }))}
                          disabled={(date) => 
                            tripData.dates.startDate ? date < tripData.dates.startDate : false
                          }
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>
              </div>

              {/* Transportation Mode */}
              <div>
                <h2 className="text-xl font-semibold mb-4">Transportation</h2>
                <RadioGroup value={transportMode} onValueChange={(value: any) => setTransportMode(value)}>
                  <div className="flex gap-4 mb-4">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="flight" id="flight" />
                      <Label htmlFor="flight" className="flex items-center gap-2 cursor-pointer">
                        <Plane className="h-4 w-4" />
                        Flight
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="car" id="car" />
                      <Label htmlFor="car" className="flex items-center gap-2 cursor-pointer">
                        <Car className="h-4 w-4" />
                        Car
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="train" id="train" />
                      <Label htmlFor="train" className="flex items-center gap-2 cursor-pointer">
                        <Train className="h-4 w-4" />
                        Train
                      </Label>
                    </div>
                  </div>
                </RadioGroup>
              </div>

              {/* Flights Section - Only show if flight mode selected */}
              {transportMode === "flight" && (
              <div>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Plane className="h-5 w-5 text-blue-500" />
                  Flight Details
                </h2>
                
                {/* Outbound Flight */}
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-600 mb-2">Outbound Flight</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="outbound-airline">Airline</Label>
                      <Input
                        id="outbound-airline"
                        placeholder="e.g., Delta"
                        value={tripData.flights.outbound.airline}
                        onChange={(e) => setTripData(prev => ({
                          ...prev,
                          flights: {
                            ...prev.flights,
                            outbound: { ...prev.flights.outbound, airline: e.target.value }
                          }
                        }))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="outbound-flight">Flight Number</Label>
                      <Input
                        id="outbound-flight"
                        placeholder="e.g., DL123"
                        value={tripData.flights.outbound.flightNumber}
                        onChange={(e) => setTripData(prev => ({
                          ...prev,
                          flights: {
                            ...prev.flights,
                            outbound: { ...prev.flights.outbound, flightNumber: e.target.value }
                          }
                        }))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="outbound-from">From Airport</Label>
                      <Input
                        id="outbound-from"
                        placeholder="e.g., JFK"
                        value={tripData.flights.outbound.departure}
                        onChange={(e) => setTripData(prev => ({
                          ...prev,
                          flights: {
                            ...prev.flights,
                            outbound: { ...prev.flights.outbound, departure: e.target.value }
                          }
                        }))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="outbound-to">To Airport</Label>
                      <Input
                        id="outbound-to"
                        placeholder="e.g., CDG"
                        value={tripData.flights.outbound.arrival}
                        onChange={(e) => setTripData(prev => ({
                          ...prev,
                          flights: {
                            ...prev.flights,
                            outbound: { ...prev.flights.outbound, arrival: e.target.value }
                          }
                        }))}
                      />
                    </div>
                  </div>
                </div>

                {/* Return Flight */}
                <div>
                  <h3 className="text-sm font-medium text-gray-600 mb-2">Return Flight</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="return-airline">Airline</Label>
                      <Input
                        id="return-airline"
                        placeholder="e.g., Delta"
                        value={tripData.flights.return.airline}
                        onChange={(e) => setTripData(prev => ({
                          ...prev,
                          flights: {
                            ...prev.flights,
                            return: { ...prev.flights.return, airline: e.target.value }
                          }
                        }))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="return-flight">Flight Number</Label>
                      <Input
                        id="return-flight"
                        placeholder="e.g., DL456"
                        value={tripData.flights.return.flightNumber}
                        onChange={(e) => setTripData(prev => ({
                          ...prev,
                          flights: {
                            ...prev.flights,
                            return: { ...prev.flights.return, flightNumber: e.target.value }
                          }
                        }))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="return-from">From Airport</Label>
                      <Input
                        id="return-from"
                        placeholder="e.g., CDG"
                        value={tripData.flights.return.departure}
                        onChange={(e) => setTripData(prev => ({
                          ...prev,
                          flights: {
                            ...prev.flights,
                            return: { ...prev.flights.return, departure: e.target.value }
                          }
                        }))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="return-to">To Airport</Label>
                      <Input
                        id="return-to"
                        placeholder="e.g., JFK"
                        value={tripData.flights.return.arrival}
                        onChange={(e) => setTripData(prev => ({
                          ...prev,
                          flights: {
                            ...prev.flights,
                            return: { ...prev.flights.return, arrival: e.target.value }
                          }
                        }))}
                      />
                    </div>
                  </div>
                </div>
              </div>
              )}

              {/* Hotel Section */}
              <div>
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Hotel className="h-5 w-5 text-blue-500" />
                  Accommodation
                </h2>
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <Label htmlFor="hotel-name">Hotel Name *</Label>
                    <Input
                      id="hotel-name"
                      placeholder="e.g., Hotel Plaza Athénée"
                      value={tripData.hotel.name}
                      onChange={(e) => setTripData(prev => ({
                        ...prev,
                        hotel: { ...prev.hotel, name: e.target.value }
                      }))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="hotel-address">Hotel Address</Label>
                    <Input
                      id="hotel-address"
                      placeholder="e.g., 25 Avenue Montaigne"
                      value={tripData.hotel.address}
                      onChange={(e) => setTripData(prev => ({
                        ...prev,
                        hotel: { ...prev.hotel, address: e.target.value }
                      }))}
                    />
                  </div>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertDescription className="text-red-800">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              {/* Submit Button */}
              <Button
                onClick={handleSubmit}
                disabled={!isFormValid() || isProcessing}
                size="lg"
                className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Creating Trip...
                  </>
                ) : (
                  <>
                    Create My Itinerary
                    <ArrowRight className="h-5 w-5 ml-2" />
                  </>
                )}
              </Button>
            </div>
          </Card>
        </motion.div>

        {/* Info Box */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-6"
        >
          <Alert className="border-blue-200 bg-blue-50">
            <Info className="h-4 w-4 text-blue-600" />
            <AlertDescription>
              <strong>What happens next?</strong><br />
              We'll use your trip details to find the best restaurants, attractions, and activities
              at your destination, creating a complete day-by-day itinerary tailored to your preferences.
            </AlertDescription>
          </Alert>
        </motion.div>
      </div>
    </div>
  );
}
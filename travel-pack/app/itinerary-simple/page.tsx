"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";

export default function SimpleItineraryPage() {
  const searchParams = useSearchParams();
  const tripId = searchParams.get("tripId");
  
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [rawJson, setRawJson] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!tripId) {
      setError("No trip ID");
      setLoading(false);
      return;
    }

    fetchData();
  }, [tripId]);

  const fetchData = async () => {
    try {
      // Use proxy to avoid hard-coded base URL and CORS
      const response = await fetch(`/api/proxy/itinerary/${tripId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
      console.log("RAW DATA FROM BACKEND:", result);
    } catch (err: any) {
      setError(err.message);
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-4">Loading Trip Data...</h1>
            <p>Fetching from: /api/proxy/itinerary/{tripId}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold text-red-600 mb-4">Error</h1>
          <p>{error}</p>
          <p className="mt-4">Trip ID: {tripId}</p>
        </div>
      </div>
    );
  }

  const itinerary = data?.itinerary || {};
  const recommendations = data?.recommendations || {};
  const tripSummary = itinerary.trip_summary || {};
  const dailySchedule = itinerary.daily_schedule || [];
  const restaurants = itinerary.restaurants || recommendations.restaurants || [];
  const attractions = itinerary.attractions || recommendations.attractions || [];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-4">
                {tripSummary.destination || "Unknown Destination"} Trip
              </h1>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-semibold">Dates:</span> {tripSummary.start_date} to {tripSummary.end_date}
                </div>
                <div>
                  <span className="font-semibold">Duration:</span> {tripSummary.duration}
                </div>
                <div>
                  <span className="font-semibold">Trip ID:</span> {tripId}
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={async () => {
                  try {
                    const response = await fetch(`/api/proxy/trips/${tripId}/save`, {
                      method: 'POST'
                    });
                    if (response.ok) {
                      setSaved(true);
                      setTimeout(() => setSaved(false), 3000);
                    }
                  } catch (err) {
                    console.error('Error saving trip:', err);
                  }
                }}
                className={`px-4 py-2 rounded transition ${
                  saved 
                    ? 'bg-green-500 text-white' 
                    : 'bg-blue-500 text-white hover:bg-blue-600'
                }`}
              >
                {saved ? '✓ Saved' : '💾 Save Trip'}
              </button>
              <a
                href="/trips"
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition"
              >
                📚 My Trips
              </a>
            </div>
          </div>
        </div>

        {/* Debug Toggle */}
        <button
          onClick={() => setRawJson(!rawJson)}
          className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          {rawJson ? "Hide" : "Show"} Raw JSON
        </button>

        {rawJson && (
          <div className="bg-black text-green-400 p-4 rounded-lg mb-6 overflow-auto max-h-96">
            <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>
          </div>
        )}

        {/* Daily Schedule */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">Daily Schedule</h2>
          {dailySchedule.length > 0 ? (
            <div className="space-y-4">
              {dailySchedule.map((day: any, idx: number) => (
                <div key={idx} className="border-l-4 border-blue-500 pl-4">
                  <h3 className="font-bold text-lg">
                    Day {day.day} - {day.day_name} ({day.date})
                  </h3>
                  
                  {/* Show activities if they exist */}
                  {day.activities && day.activities.length > 0 ? (
                    <ul className="mt-2 space-y-1">
                      {day.activities.map((activity: string, actIdx: number) => (
                        <li key={actIdx} className="text-gray-700">
                          • {activity}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500 italic">No activities yet</p>
                  )}

                  {/* Show meals if they exist */}
                  {day.meals && (
                    <div className="mt-2 text-sm text-gray-600">
                      {day.meals.breakfast && <div>🍳 Breakfast: {day.meals.breakfast}</div>}
                      {day.meals.lunch && <div>🍽️ Lunch: {day.meals.lunch}</div>}
                      {day.meals.dinner && <div>🍷 Dinner: {day.meals.dinner}</div>}
                    </div>
                  )}

                  {/* Show any other day properties */}
                  {day.morning && day.morning.length > 0 && (
                    <div className="mt-2">
                      <strong>Morning:</strong>
                      {day.morning.map((item: string, i: number) => (
                        <div key={i}>• {item}</div>
                      ))}
                    </div>
                  )}
                  {day.afternoon && day.afternoon.length > 0 && (
                    <div className="mt-2">
                      <strong>Afternoon:</strong>
                      {day.afternoon.map((item: string, i: number) => (
                        <div key={i}>• {item}</div>
                      ))}
                    </div>
                  )}
                  {day.evening && day.evening.length > 0 && (
                    <div className="mt-2">
                      <strong>Evening:</strong>
                      {day.evening.map((item: string, i: number) => (
                        <div key={i}>• {item}</div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No daily schedule available</p>
          )}
        </div>

        {/* Restaurants */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">
            Restaurants ({restaurants.length})
          </h2>
          {restaurants.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {restaurants.map((restaurant: any, idx: number) => (
                <div key={idx} className="border rounded-lg p-4">
                  <h3 className="font-bold">{restaurant.name || `Restaurant ${idx + 1}`}</h3>
                  {restaurant.address && (
                    <p className="text-sm text-gray-600">📍 {restaurant.address}</p>
                  )}
                  {restaurant.cuisine && (
                    <p className="text-sm">🍴 {restaurant.cuisine}</p>
                  )}
                  {restaurant.price && (
                    <p className="text-sm">💰 {restaurant.price}</p>
                  )}
                  {restaurant.description && (
                    <p className="text-sm mt-2 text-gray-700">{restaurant.description}</p>
                  )}
                  {restaurant.price_range && (
                    <p className="text-sm">Price: {restaurant.price_range}</p>
                  )}
                  {restaurant.rating && (
                    <p className="text-sm">Rating: {restaurant.rating}</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No restaurants loaded</p>
          )}
        </div>

        {/* Attractions */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">
            Attractions ({attractions.length})
          </h2>
          {attractions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {attractions.map((attraction: any, idx: number) => (
                <div key={idx} className="border rounded-lg p-4">
                  <h3 className="font-bold">{attraction.name || `Attraction ${idx + 1}`}</h3>
                  {attraction.address && (
                    <p className="text-sm text-gray-600">📍 {attraction.address}</p>
                  )}
                  {attraction.type && (
                    <p className="text-sm">🎭 {attraction.type}</p>
                  )}
                  {attraction.price && (
                    <p className="text-sm">💰 {attraction.price}</p>
                  )}
                  {attraction.hours && (
                    <p className="text-sm">🕐 {attraction.hours}</p>
                  )}
                  {attraction.description && (
                    <p className="text-sm mt-2 text-gray-700">{attraction.description}</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No attractions loaded</p>
          )}
        </div>

        {/* Raw Itinerary Data */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4">All Itinerary Fields</h2>
          <div className="text-sm">
            {Object.keys(itinerary).map(key => (
              <div key={key} className="mb-2">
                <strong>{key}:</strong>
                <pre className="bg-gray-100 p-2 rounded mt-1 overflow-auto">
                  {JSON.stringify(itinerary[key], null, 2)}
                </pre>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
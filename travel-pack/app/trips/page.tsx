"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface SavedTrip {
  trip_id: string;
  destination: string;
  start_date: string;
  end_date: string;
  duration: string;
  title: string;
  saved_at: string;
  passengers: number;
  flights: number;
  hotels: number;
}

export default function SavedTripsPage() {
  const router = useRouter();
  const [trips, setTrips] = useState<SavedTrip[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredTrips, setFilteredTrips] = useState<SavedTrip[]>([]);

  useEffect(() => {
    loadTrips();
  }, []);

  useEffect(() => {
    // Filter trips based on search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      setFilteredTrips(
        trips.filter(trip => 
          trip.destination.toLowerCase().includes(query) ||
          trip.start_date.includes(query) ||
          trip.title.toLowerCase().includes(query)
        )
      );
    } else {
      setFilteredTrips(trips);
    }
  }, [searchQuery, trips]);

  const loadTrips = async () => {
    try {
      // Use Next.js proxy to avoid CORS and hard-coded base URLs
      const response = await fetch("/api/proxy/trips/saved");
      const data = await response.json();
      setTrips(data.trips || []);
      setFilteredTrips(data.trips || []);
    } catch (error) {
      console.error("Error loading trips:", error);
    } finally {
      setLoading(false);
    }
  };

  const viewTrip = (tripId: string) => {
    router.push(`/itinerary?tripId=${tripId}`);
  };

  const deleteTrip = async (tripId: string) => {
    if (!confirm("Are you sure you want to delete this trip?")) return;

    try {
      const response = await fetch(`/api/proxy/trips/${tripId}`, {
        method: "DELETE"
      });
      
      if (response.ok) {
        // Reload trips
        loadTrips();
      }
    } catch (error) {
      console.error("Error deleting trip:", error);
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  const formatSavedAt = (dateStr: string) => {
    if (!dateStr) return "";
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString() + " " + date.toLocaleTimeString();
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">My Saved Trips</h1>
            <p className="text-gray-600 mt-2">View and manage all your travel plans</p>
          </div>
          <div className="flex gap-4">
            <a
              href="/upload"
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
            >
              + New Trip
            </a>
          </div>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <input
            type="text"
            placeholder="Search trips by destination or date..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Trips Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading your trips...</p>
          </div>
        ) : filteredTrips.length === 0 ? (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <div className="text-6xl mb-4">✈️</div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              {searchQuery ? "No trips found" : "No saved trips yet"}
            </h2>
            <p className="text-gray-600 mb-6">
              {searchQuery 
                ? "Try adjusting your search terms"
                : "Upload your travel documents to get started"
              }
            </p>
            {!searchQuery && (
              <a
                href="/upload"
                className="inline-block px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
              >
                Create Your First Trip
              </a>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTrips.map((trip) => (
              <div
                key={trip.trip_id}
                className="bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow overflow-hidden"
              >
                {/* Trip Header */}
                <div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-4">
                  <h3 className="text-xl font-bold text-white">
                    {trip.destination || "Unknown Destination"}
                  </h3>
                  <p className="text-blue-100 text-sm mt-1">
                    {trip.duration || "Duration not set"}
                  </p>
                </div>

                {/* Trip Details */}
                <div className="p-4">
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Dates:</span>
                      <span className="font-medium">
                        {formatDate(trip.start_date)} - {formatDate(trip.end_date)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Flights:</span>
                      <span className="font-medium">{trip.flights || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Hotels:</span>
                      <span className="font-medium">{trip.hotels || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Passengers:</span>
                      <span className="font-medium">{trip.passengers || 1}</span>
                    </div>
                  </div>

                  {/* Saved At */}
                  <p className="text-xs text-gray-500 mb-4">
                    Saved: {formatSavedAt(trip.saved_at)}
                  </p>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => viewTrip(trip.trip_id)}
                      className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                    >
                      View Trip
                    </button>
                    <button
                      onClick={() => deleteTrip(trip.trip_id)}
                      className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Stats */}
        {trips.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow-md p-6">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-3xl font-bold text-blue-500">{trips.length}</p>
                <p className="text-gray-600">Total Trips</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-green-500">
                  {trips.reduce((acc, trip) => acc + (trip.flights || 0), 0)}
                </p>
                <p className="text-gray-600">Total Flights</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-purple-500">
                  {trips.reduce((acc, trip) => acc + (trip.hotels || 0), 0)}
                </p>
                <p className="text-gray-600">Total Hotels</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
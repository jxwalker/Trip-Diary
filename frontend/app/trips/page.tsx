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
    router.push(`/guide-modern?tripId=${tripId}`);
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

  // Helper function to create sample trip
  const createSampleTrip = async () => {
    try {
      const sampleData = {
        destination: "Paris, France",
        start_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date(Date.now() + 37 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        free_text: "Sample trip to Paris with visits to Eiffel Tower, Louvre Museum, and Seine River cruise"
      };
      
      const response = await fetch("/api/proxy/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sampleData)
      });
      
      if (response.ok) {
        const data = await response.json();
        router.push(`/summary?tripId=${data.trip_id}`);
      }
    } catch (error) {
      console.error("Error creating sample trip:", error);
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
          <div className="space-y-6">
            {/* Enhanced Empty State */}
            <div className="bg-white rounded-lg shadow-lg p-12 text-center">
              <div className="text-6xl mb-4 animate-bounce">✈️</div>
              <h2 className="text-3xl font-bold text-gray-900 mb-3">
                {searchQuery ? "No trips found" : "Start Your Journey"}
              </h2>
              <p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">
                {searchQuery 
                  ? "Try adjusting your search terms or clear the search to see all trips"
                  : "Upload your travel documents and let AI create your perfect itinerary"
                }
              </p>
              {!searchQuery && (
                <div className="flex flex-col items-center gap-4">
                  <a
                    href="/upload"
                    className="px-8 py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-lg font-semibold rounded-xl hover:from-blue-600 hover:to-indigo-700 transition transform hover:scale-105 shadow-lg"
                  >
                    📤 Upload Your First Trip
                  </a>
                  <button
                    onClick={() => createSampleTrip()}
                    className="text-sm text-gray-500 hover:text-gray-700 underline"
                  >
                    or try with sample data
                  </button>
                </div>
              )}
            </div>

            {/* Feature Cards */}
            {!searchQuery && (
              <div className="grid md:grid-cols-3 gap-6 mt-8">
                <div className="bg-white rounded-lg p-6 text-center shadow-md">
                  <div className="text-3xl mb-3">📄</div>
                  <h3 className="font-semibold mb-2">Upload Documents</h3>
                  <p className="text-sm text-gray-600">PDFs, emails, or manual entry</p>
                </div>
                <div className="bg-white rounded-lg p-6 text-center shadow-md">
                  <div className="text-3xl mb-3">🤖</div>
                  <h3 className="font-semibold mb-2">AI Processing</h3>
                  <p className="text-sm text-gray-600">Automatic extraction & organization</p>
                </div>
                <div className="bg-white rounded-lg p-6 text-center shadow-md">
                  <div className="text-3xl mb-3">🗺️</div>
                  <h3 className="font-semibold mb-2">Perfect Itinerary</h3>
                  <p className="text-sm text-gray-600">Personalized recommendations</p>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTrips.map((trip) => (
              <TripCard key={trip.trip_id} trip={trip} onView={viewTrip} onDelete={deleteTrip} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Trip Card Component
function TripCard({ trip, onView, onDelete }: { 
  trip: SavedTrip; 
  onView: (id: string) => void; 
  onDelete: (id: string) => void;
}) {
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
    <div className="bg-white rounded-lg shadow-lg hover:shadow-xl transition p-6">
      <div className="cursor-pointer" onClick={() => onView(trip.trip_id)}>
        <h3 className="text-xl font-bold text-gray-900 mb-2 hover:text-blue-600 transition">
          {trip.destination}
        </h3>
        {trip.title && (
          <p className="text-sm text-gray-600 mb-3">{trip.title}</p>
        )}
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">📅 Dates:</span>
            <span className="font-medium">
              {formatDate(trip.start_date)} - {formatDate(trip.end_date)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">⏱️ Duration:</span>
            <span className="font-medium">{trip.duration || "N/A"}</span>
          </div>
          {trip.passengers > 0 && (
            <div className="flex justify-between">
              <span className="text-gray-500">👥 Travelers:</span>
              <span className="font-medium">{trip.passengers}</span>
            </div>
          )}
          <div className="flex gap-4 mt-3">
            {trip.flights > 0 && (
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                ✈️ {trip.flights} flights
              </span>
            )}
            {trip.hotels > 0 && (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                🏨 {trip.hotels} hotels
              </span>
            )}
          </div>
        </div>
        {trip.saved_at && (
          <p className="text-xs text-gray-400 mt-4">
            Saved: {formatSavedAt(trip.saved_at)}
          </p>
        )}
      </div>
      <div className="flex gap-2 mt-4 pt-4 border-t">
        <button
          onClick={() => onView(trip.trip_id)}
          className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
        >
          View Details
        </button>
        <button
          onClick={() => onDelete(trip.trip_id)}
          className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
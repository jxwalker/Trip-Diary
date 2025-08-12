"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadDemoPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  const handleNYCTrip = async () => {
    setLoading(true);
    setStatus("Creating NYC trip with real content...");

    try {
      // Send the trip data directly as free_text
      const tripText = `
Trip: New York City
Dates: August 9-14, 2025

Flight BA 115 - British Airways
Departure: LHR Sat, Aug 9, 2025 14:40
Arrival: JFK Sat, Aug 9, 2025 17:35
Class: First, Seat: 1A

Flight BA 112 - British Airways  
Departure: JFK Thu, Aug 14, 2025 18:30
Arrival: LHR Fri, Aug 15, 2025 06:30
Class: First, Seat: 1K

Hotel: Luxury Collection Manhattan Midtown
Address: 151 West 54th Street, New York, NY 10019
Check-in: Sat, Aug 9, 2025
Check-out: Thu, Aug 14, 2025
Confirmation: 83313860
      `;

      const formData = new FormData();
      formData.append("free_text", tripText);
      formData.append("use_vision", "false");

      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      const tripId = data.trip_id;
      
      setStatus(`Processing trip ${tripId}...`);
      
      // Wait for processing
      let attempts = 0;
      const maxAttempts = 30;
      
      while (attempts < maxAttempts) {
        const statusResponse = await fetch(`http://localhost:8000/api/status/${tripId}`);
        
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          setStatus(`${statusData.progress}% - ${statusData.message}`);
          
          if (statusData.status === "completed") {
            router.push(`/itinerary-simple?tripId=${tripId}`);
            return;
          } else if (statusData.status === "error") {
            throw new Error(statusData.message);
          }
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        attempts++;
      }
      
      throw new Error("Processing timeout");
      
    } catch (err: any) {
      setStatus(`Error: ${err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Trip Diary - Working Demo
          </h1>
          <p className="text-xl text-gray-600">
            Real content from Perplexity, no placeholders
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold mb-6">Try the NYC Trip Demo</h2>
          
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
            <h3 className="font-bold text-blue-900 mb-2">What this does:</h3>
            <ul className="space-y-2 text-blue-800">
              <li>✅ Extracts trip details (flights, hotels, dates)</li>
              <li>✅ Identifies destination: New York City</li>
              <li>✅ Searches Perplexity for REAL restaurants</li>
              <li>✅ Searches Perplexity for REAL attractions</li>
              <li>✅ Creates daily itinerary with actual venues</li>
            </ul>
          </div>

          <button
            onClick={handleNYCTrip}
            disabled={loading}
            className="w-full py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold rounded-lg hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
          >
            {loading ? "Processing..." : "Generate NYC Trip with Real Content"}
          </button>

          {status && (
            <div className="mt-6 p-4 bg-gray-100 rounded-lg">
              <p className="text-sm font-mono">{status}</p>
            </div>
          )}

          <div className="mt-8 pt-8 border-t">
            <h3 className="font-bold mb-4">Example of what you'll see:</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-semibold text-gray-700">Real Restaurants:</h4>
                <ul className="mt-2 space-y-1 text-gray-600">
                  <li>• Piccola Cucina Estiatorio</li>
                  <li>• Charlie Bird</li>
                  <li>• L'Artusi</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-700">Real Attractions:</h4>
                <ul className="mt-2 space-y-1 text-gray-600">
                  <li>• The Metropolitan Museum</li>
                  <li>• Guggenheim Museum</li>
                  <li>• Museum of Modern Art</li>
                </ul>
              </div>
            </div>
            <p className="mt-4 text-xs text-gray-500">
              All venues include real addresses and details from Perplexity
            </p>
          </div>
        </div>

        <div className="mt-8 text-center text-sm text-gray-600">
          <p>This demo bypasses the broken file upload and sends trip data directly.</p>
          <p>The backend successfully generates real content when it has proper data.</p>
        </div>
      </div>
    </div>
  );
}
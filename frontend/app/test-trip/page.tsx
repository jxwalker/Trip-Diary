"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function TestTripPage() {
  const [status, setStatus] = useState<string>("");
  const [tripId, setTripId] = useState<string>("");
  
  const createTestTrip = async () => {
    setStatus("Creating test trip without flights...");
    
    const tripData = {
      flights: [],  // No flights!
      hotels: [{
        name: "Test Hotel Barcelona",
        city: "Barcelona",
        check_in_date: "2025-12-15",
        check_out_date: "2025-12-20"
      }],
      trip_details: {
        destination: "Barcelona, Spain",
        start_date: "2025-12-15",
        end_date: "2025-12-20",
        transportation_mode: "train"
      }
    };
    
    try {
      const formData = new FormData();
      formData.append("trip_details", JSON.stringify(tripData));
      
      const response = await fetch("/api/proxy/upload", {
        method: "POST",
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        setTripId(data.trip_id);
        setStatus(`✓ Trip created: ${data.trip_id}`);
        
        // Generate guide
        setTimeout(() => generateGuide(data.trip_id), 2000);
      } else {
        setStatus("✗ Failed to create trip");
      }
    } catch (err) {
      setStatus(`✗ Error: ${err}`);
    }
  };
  
  const generateGuide = async (id: string) => {
    setStatus("Generating guide...");
    
    try {
      const response = await fetch(`/api/proxy/generate-guide/${id}`, {
        method: "POST"
      });
      
      if (response.ok) {
        setStatus("✓ Guide generation started! Checking...");
        setTimeout(() => checkGuide(id), 5000);
      } else {
        setStatus("✗ Failed to generate guide");
      }
    } catch (err) {
      setStatus(`✗ Error: ${err}`);
    }
  };
  
  const checkGuide = async (id: string) => {
    try {
      const response = await fetch(`/api/proxy/enhanced-guide/${id}`);
      const data = await response.json();
      
      if (data.guide && !data.guide.error) {
        setStatus(`✓ Guide ready! ${data.guide.restaurants?.length || 0} restaurants, ${data.guide.attractions?.length || 0} attractions`);
      } else {
        setStatus(`✗ Guide error: ${data.guide?.error || "Unknown"}`);
      }
    } catch (err) {
      setStatus(`✗ Error: ${err}`);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <Card className="p-8">
          <h1 className="text-2xl font-bold mb-4">Test Trip Without Flights</h1>
          
          <div className="space-y-4">
            <Button onClick={createTestTrip} size="lg">
              Create Test Trip (Train to Barcelona)
            </Button>
            
            {status && (
              <div className="p-4 bg-gray-100 rounded">
                <pre className="whitespace-pre-wrap">{status}</pre>
              </div>
            )}
            
            {tripId && (
              <div className="space-y-2">
                <p>Trip ID: <code>{tripId}</code></p>
                <a 
                  href={`/guide-modern?tripId=${tripId}`}
                  className="text-blue-500 underline"
                >
                  View Guide
                </a>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
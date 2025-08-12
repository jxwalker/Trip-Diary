"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function SimpleUploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }

    setUploading(true);
    setError("");
    setStatus("Uploading file...");

    try {
      // Upload the file using the single-file endpoint
      const formData = new FormData();
      formData.append("file", file);
      formData.append("use_vision", "false"); // Use text mode for better extraction

      const uploadResponse = await fetch("http://localhost:8000/api/upload-single", {
        method: "POST",
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.status}`);
      }

      const uploadData = await uploadResponse.json();
      const tripId = uploadData.trip_id;
      
      setStatus(`Upload successful! Trip ID: ${tripId}`);
      
      // Poll for processing completion
      setStatus("Processing your trip data...");
      
      let attempts = 0;
      const maxAttempts = 60; // 2 minutes max
      
      const checkStatus = async () => {
        const statusResponse = await fetch(`http://localhost:8000/api/status/${tripId}`);
        
        if (!statusResponse.ok) {
          throw new Error(`Status check failed: ${statusResponse.status}`);
        }
        
        const statusData = await statusResponse.json();
        setStatus(`${statusData.progress}% - ${statusData.message}`);
        
        if (statusData.status === "completed") {
          // Redirect to simple itinerary view
          router.push(`/itinerary-simple?tripId=${tripId}`);
          return true;
        } else if (statusData.status === "error") {
          throw new Error(statusData.message);
        }
        
        return false;
      };
      
      // Poll every 2 seconds
      while (attempts < maxAttempts) {
        const completed = await checkStatus();
        if (completed) break;
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        attempts++;
      }
      
      if (attempts >= maxAttempts) {
        throw new Error("Processing timeout");
      }
      
    } catch (err: any) {
      setError(err.message);
      console.error("Error:", err);
    } finally {
      setUploading(false);
    }
  };

  // Create test NYC trip data
  const createTestTrip = async () => {
    setUploading(true);
    setError("");
    setStatus("Creating test NYC trip...");

    try {
      // Create a fake PDF with NYC trip data
      const tripContent = `
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

      const blob = new Blob([tripContent], { type: 'text/plain' });
      const testFile = new File([blob], "nyc_trip.txt", { type: "text/plain" });
      
      setFile(testFile);
      setStatus("Test file created, uploading...");
      
      // Now upload it using the single-file endpoint
      const formData = new FormData();
      formData.append("file", testFile);
      formData.append("use_vision", "false");

      const uploadResponse = await fetch("http://localhost:8000/api/upload-single", {
        method: "POST",
        body: formData,
      });

      if (!uploadResponse.ok) {
        const errorText = await uploadResponse.text();
        throw new Error(`Upload failed: ${uploadResponse.status} - ${errorText}`);
      }

      const uploadData = await uploadResponse.json();
      const tripId = uploadData.trip_id;
      
      setStatus(`Test trip created! Trip ID: ${tripId}`);
      
      // Wait a bit then redirect
      setTimeout(() => {
        router.push(`/itinerary-simple?tripId=${tripId}`);
      }, 2000);
      
    } catch (err: any) {
      setError(err.message);
      console.error("Error:", err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Simple Trip Upload</h1>
        
        {/* File Upload */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Upload Travel Document</h2>
          
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="mb-4 block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
            disabled={uploading}
          />
          
          {file && (
            <p className="text-sm text-gray-600 mb-4">
              Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
            </p>
          )}
          
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {uploading ? "Processing..." : "Upload and Process"}
          </button>
        </div>

        {/* Test Trip Button */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Quick Test</h2>
          <p className="text-sm text-gray-600 mb-4">
            Create a test NYC trip (Aug 9-14, 2025) to see how the system works
          </p>
          <button
            onClick={createTestTrip}
            disabled={uploading}
            className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Create Test NYC Trip
          </button>
        </div>

        {/* Status Display */}
        {status && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <p className="text-blue-700">{status}</p>
          </div>
        )}
        
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">Error: {error}</p>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-gray-100 rounded-lg p-6">
          <h3 className="font-semibold mb-2">How it works:</h3>
          <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
            <li>Upload your travel PDF or click "Create Test NYC Trip"</li>
            <li>Backend extracts trip details</li>
            <li>System searches for real restaurants and attractions</li>
            <li>View your complete itinerary with real venues</li>
          </ol>
          
          <p className="mt-4 text-sm text-gray-600">
            This simple version shows exactly what the backend returns, with no frontend placeholders.
          </p>
        </div>
      </div>
    </div>
  );
}
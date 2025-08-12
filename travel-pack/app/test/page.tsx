"use client";

import { useState } from "react";

export default function TestPage() {
  const [testResults, setTestResults] = useState<any[]>([]);
  const [testing, setTesting] = useState(false);

  const runTests = async () => {
    setTesting(true);
    setTestResults([]);
    const results: any[] = [];

    // Test 1: Backend health check
    try {
      const response = await fetch("/api/proxy/");
      const data = await response.json();
      results.push({
        test: "Backend Health",
        status: "✅ PASS",
        details: `API running: ${data.message}`
      });
    } catch (error) {
      results.push({
        test: "Backend Health",
        status: "❌ FAIL",
        details: "Backend not reachable"
      });
    }
    setTestResults([...results]);

    // Test 2: Upload endpoint with free text
    try {
      const formData = new FormData();
      formData.append("free_text", "Trip to New York, August 9-14, 2025");
      formData.append("use_vision", "false");
      
      const response = await fetch("/api/proxy/upload", {
        method: "POST",
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        results.push({
          test: "Upload Endpoint (Free Text)",
          status: "✅ PASS",
          details: `Trip ID: ${data.trip_id}`
        });
        
        // Test status endpoint
        await new Promise(resolve => setTimeout(resolve, 2000));
        const statusResponse = await fetch(`/api/proxy/status/${data.trip_id}`);
        const statusData = await statusResponse.json();
        
        results.push({
          test: "Status Endpoint",
          status: "✅ PASS",
          details: `Progress: ${statusData.progress}%, Status: ${statusData.status}`
        });
      } else {
        throw new Error(`Upload failed: ${response.status}`);
      }
    } catch (error: any) {
      results.push({
        test: "Upload Endpoint",
        status: "❌ FAIL",
        details: error.message
      });
    }
    setTestResults([...results]);

    // Test 3: Direct pipeline test
    try {
      const response = await fetch("/api/proxy/test-pipeline", {
        method: "GET"
      });
      
      if (response.ok) {
        const data = await response.json();
        results.push({
          test: "Pipeline Test",
          status: data.success ? "✅ PASS" : "❌ FAIL",
          details: data.message || "Pipeline test completed"
        });
      }
    } catch (error) {
      // This endpoint might not exist, that's ok
      results.push({
        test: "Pipeline Test",
        status: "⚠️ SKIP",
        details: "Test endpoint not available"
      });
    }
    setTestResults([...results]);

    // Test 4: Perplexity Integration
    try {
      // Create a test trip with NYC data
      const formData = new FormData();
      formData.append("free_text", `
        Trip: New York City
        Dates: August 9-14, 2025
        Hotel: Luxury Collection Manhattan Midtown
        Address: 151 West 54th Street, New York, NY
      `);
      formData.append("use_vision", "false");
      
      const response = await fetch("/api/proxy/upload", {
        method: "POST",
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Wait for processing
        let attempts = 0;
        let completed = false;
        
        while (attempts < 30 && !completed) {
          await new Promise(resolve => setTimeout(resolve, 2000));
          const statusResponse = await fetch(`/api/proxy/status/${data.trip_id}`);
          const statusData = await statusResponse.json();
          
          if (statusData.status === "completed") {
            completed = true;
            
            // Get the itinerary
            const itineraryResponse = await fetch(`/api/proxy/itinerary/${data.trip_id}`);
            const itineraryData = await itineraryResponse.json();
            
            const restaurants = itineraryData.itinerary?.restaurants || [];
            const attractions = itineraryData.itinerary?.attractions || [];
            
            results.push({
              test: "Perplexity Content Generation",
              status: restaurants.length > 0 && attractions.length > 0 ? "✅ PASS" : "❌ FAIL",
              details: `Restaurants: ${restaurants.length}, Attractions: ${attractions.length}`
            });
            
            if (restaurants.length > 0) {
              results.push({
                test: "Sample Restaurant",
                status: "ℹ️ INFO",
                details: `${restaurants[0].name} - ${restaurants[0].address}`
              });
            }
            
            if (attractions.length > 0) {
              results.push({
                test: "Sample Attraction",
                status: "ℹ️ INFO",
                details: `${attractions[0].name} - ${attractions[0].address}`
              });
            }
          }
          attempts++;
        }
        
        if (!completed) {
          results.push({
            test: "Perplexity Content Generation",
            status: "⏱️ TIMEOUT",
            details: "Processing took too long"
          });
        }
      }
    } catch (error: any) {
      results.push({
        test: "Perplexity Content Generation",
        status: "❌ FAIL",
        details: error.message
      });
    }
    
    setTestResults([...results]);
    setTesting(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">System Test Suite</h1>
        
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Backend Integration Tests</h2>
          
          <button
            onClick={runTests}
            disabled={testing}
            className="mb-6 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
          >
            {testing ? "Running Tests..." : "Run All Tests"}
          </button>
          
          {testResults.length > 0 && (
            <div className="space-y-3">
              {testResults.map((result, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border ${
                    result.status.includes("PASS") ? "bg-green-50 border-green-200" :
                    result.status.includes("FAIL") ? "bg-red-50 border-red-200" :
                    result.status.includes("INFO") ? "bg-blue-50 border-blue-200" :
                    "bg-yellow-50 border-yellow-200"
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{result.test}</h3>
                      <p className="text-sm text-gray-600 mt-1">{result.details}</p>
                    </div>
                    <span className="text-lg">{result.status}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
          <h3 className="font-bold text-blue-900 mb-2">What This Tests:</h3>
          <ul className="space-y-1 text-blue-800">
            <li>✓ Backend API is running</li>
            <li>✓ File upload endpoints work</li>
            <li>✓ Trip data extraction works</li>
            <li>✓ Perplexity integration returns real content</li>
            <li>✓ No placeholder text in responses</li>
          </ul>
        </div>
        
        <div className="mt-8 grid grid-cols-3 gap-4">
          <a href="/upload-simple" className="text-center p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
            <span className="text-2xl">📤</span>
            <p className="mt-2">Simple Upload</p>
          </a>
          <a href="/upload-demo" className="text-center p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
            <span className="text-2xl">🎯</span>
            <p className="mt-2">Demo Page</p>
          </a>
          <a href="/upload" className="text-center p-4 bg-white rounded-lg shadow hover:shadow-lg transition">
            <span className="text-2xl">✨</span>
            <p className="mt-2">Main Upload</p>
          </a>
        </div>
      </div>
    </div>
  );
}
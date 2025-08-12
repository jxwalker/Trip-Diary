"use client";

export default function SimpleLandingPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Trip Diary - Simple Version</h1>
        
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold mb-6">No Placeholders. Real Data Only.</h2>
          
          <p className="text-gray-700 mb-8">
            This is a simplified version that shows exactly what the backend returns.
            No frontend magic, no placeholders, just raw data from Perplexity searches.
          </p>
          
          <div className="space-y-4">
            <a
              href="/upload-simple"
              className="block w-full px-6 py-3 bg-blue-500 text-white text-center rounded-lg hover:bg-blue-600 transition"
            >
              Upload Trip Document →
            </a>
            
            <div className="text-center text-gray-500 my-4">OR</div>
            
            <div className="bg-gray-100 rounded-lg p-6">
              <h3 className="font-semibold mb-2">Test with existing trip:</h3>
              <p className="text-sm text-gray-600 mb-4">
                If you already have a trip ID, enter it here:
              </p>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.currentTarget);
                  const tripId = formData.get('tripId');
                  if (tripId) {
                    window.location.href = `/itinerary-simple?tripId=${tripId}`;
                  }
                }}
                className="flex gap-2"
              >
                <input
                  name="tripId"
                  type="text"
                  placeholder="Enter trip ID"
                  className="flex-1 px-4 py-2 border rounded-lg"
                />
                <button
                  type="submit"
                  className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                >
                  View Trip
                </button>
              </form>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t">
            <h3 className="font-semibold mb-2">What's different?</h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
              <li>Direct API calls to backend (no proxy)</li>
              <li>Shows exactly what backend returns</li>
              <li>No placeholder text generation</li>
              <li>Raw JSON view available</li>
              <li>All data fields visible</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
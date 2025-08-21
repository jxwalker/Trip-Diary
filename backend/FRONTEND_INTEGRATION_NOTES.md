# Frontend Integration Notes

## Issue: 404 Error on Enhanced Guide Endpoint

### Problem
Frontend receives 404 when trying to fetch enhanced guide at:
```
GET /api/proxy/enhanced-guide/{trip_id}
```

### Root Causes

1. **Incomplete Trip Data**: Uploaded files may not contain all required information:
   - Missing destination
   - Missing start_date  
   - Missing end_date
   
2. **Guide Not Generated**: Guide generation is not automatic after upload

### Solution

## Required Trip Data Structure

For successful guide generation, ensure the trip has:

```json
{
  "trip_details": {
    "destination": "City, Country",  // REQUIRED
    "start_date": "YYYY-MM-DD",     // REQUIRED
    "end_date": "YYYY-MM-DD"        // REQUIRED
  },
  "hotels": [{
    "name": "Hotel Name",
    "city": "City"
  }]
}
```

## API Flow

### 1. Upload Trip
```
POST /api/upload
Content-Type: multipart/form-data

Form Data:
- trip_details: JSON string with trip data
- OR
- files: uploaded PDF/text files
```

### 2. Set Preferences (Optional)
```
POST /api/preferences/{trip_id}
Content-Type: application/json

{
  "dining": {...},
  "interests": {...}
}
```

### 3. Generate Guide (REQUIRED)

**Option A: Streaming Generation (Recommended)**
```
GET /api/generation-stream/{trip_id}
Accept: text/event-stream

Returns Server-Sent Events with progress updates
```

**Option B: Direct Generation**
```
POST /api/generate-guide/{trip_id}

Returns: 
{
  "status": "success",
  "trip_id": "...",
  "has_guide": true
}
```

### 4. Check Generation Status
```
GET /api/generation-status/{trip_id}

Returns:
{
  "status": "completed",
  "progress": 100,
  "has_guide": true
}
```

### 5. Get Enhanced Guide
```
GET /api/enhanced-guide/{trip_id}

Returns:
{
  "status": "success",
  "guide": {
    "summary": "...",
    "restaurants": [...],
    "attractions": [...],
    "daily_itinerary": [...],
    ...
  }
}
```

## Frontend Implementation Checklist

- [ ] Validate trip data has destination and dates before upload
- [ ] Call generation endpoint after successful upload
- [ ] Monitor generation progress using SSE or polling
- [ ] Only fetch enhanced guide after generation completes
- [ ] Handle 404 errors gracefully with retry or user feedback

## Example Frontend Flow

```javascript
// 1. Upload trip
const uploadResponse = await fetch('/api/upload', {
  method: 'POST',
  body: formData
});
const { trip_id } = await uploadResponse.json();

// 2. Set preferences (optional)
await fetch(`/api/preferences/${trip_id}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(preferences)
});

// 3. Generate guide with progress tracking
const eventSource = new EventSource(`/api/generation-stream/${trip_id}`);
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateProgress(data.progress, data.message);
  
  if (data.type === 'complete') {
    eventSource.close();
    // 4. Now fetch the guide
    fetchEnhancedGuide(trip_id);
  }
};

// 5. Fetch enhanced guide
async function fetchEnhancedGuide(tripId) {
  const response = await fetch(`/api/enhanced-guide/${tripId}`);
  if (response.ok) {
    const { guide } = await response.json();
    displayGuide(guide);
  }
}
```

## Testing

Use the test script to verify the flow:
```bash
cd backend
source venv/bin/activate
python tests/test_manual_trip.py
```

This will create a trip with complete data and generate a guide successfully.
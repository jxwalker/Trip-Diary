# Google Places API Setup Guide

## Overview

We've implemented Google Places API as our primary restaurant and attraction data source, replacing the expensive Yelp API. This provides **30x cost savings** while delivering comprehensive data including photos, reviews, opening hours, and booking integration.

## Cost Comparison

| Service | Cost per Request | Free Tier | Annual Cost (10K requests/month) |
|---------|------------------|-----------|-----------------------------------|
| **Yelp Fusion API** | $0.50+ | None | $60,000+ |
| **Google Places API** | $0.017 | $200/month credit | $2,040 |
| **Savings** | **30x cheaper** | **11,700 free requests/month** | **$57,960 saved** |

## Setup Instructions

### 1. Enable Google Places API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services > Library**
4. Search for and enable these APIs:
   - **Places API (New)**
   - **Maps JavaScript API** (for interactive maps)
   - **Maps Static API** (for static map images)

### 2. Configure API Key

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > API Key**
3. Copy your API key
4. **Restrict the API key** (recommended):
   - Application restrictions: HTTP referrers or IP addresses
   - API restrictions: Select only the APIs you enabled

### 3. Environment Configuration

Add your API key to the `.env` file:

```bash
GOOGLE_MAPS_API_KEY=AIzaYourActualAPIKeyHere
```

### 4. Verify Setup

Run the configuration test:

```bash
cd backend
source venv/bin/activate
python -m pytest tests/integration/test_google_places_configuration.py -v
```

## Features Implemented

### Restaurant Data
- ✅ **Real photos** from Google Places (no more placeholders)
- ✅ **Reviews and ratings** from Google users
- ✅ **Opening hours** and business status
- ✅ **Price levels** ($, $$, $$$, $$$$)
- ✅ **Contact information** (phone, website, address)
- ✅ **Cuisine types** and categories
- ✅ **Booking URLs** (OpenTable, Resy, direct websites)

### Attraction Data
- ✅ **Tourist attractions** with photos and reviews
- ✅ **Museums, galleries, parks** with opening hours
- ✅ **Visit duration estimates** (e.g., "2-3 hours")
- ✅ **Best time to visit** recommendations
- ✅ **Coordinates** for mapping and directions

### Search Capabilities
- ✅ **Location-based search** ("restaurants in New York")
- ✅ **Cuisine filtering** ("italian restaurants")
- ✅ **Price range filtering** ($$, $$$, etc.)
- ✅ **Nearby search** by coordinates and radius
- ✅ **Attraction type filtering** (museums, parks, etc.)

### Performance Features
- ✅ **Intelligent caching** to minimize API calls
- ✅ **Batch processing** for multiple requests
- ✅ **Error handling** and fallback mechanisms
- ✅ **Rate limiting** compliance

## API Usage Examples

### Search Restaurants

```python
from services.enhanced_google_places_service import EnhancedGooglePlacesService

service = EnhancedGooglePlacesService()
await service.initialize()

# Basic restaurant search
restaurants = await service.search_restaurants(
    location="New York, NY",
    limit=10
)

# Filtered search
restaurants = await service.search_restaurants(
    location="San Francisco, CA",
    cuisine_type="italian",
    price_range="$$",
    limit=5
)

# Nearby search
nearby = await service.get_nearby_restaurants(
    lat=40.7580,
    lng=-73.9855,
    radius=1000,
    limit=10
)
```

### Get Place Details

```python
# Get detailed information
details = await service.get_place_details(place_id)

# Get photos
photos = await service.get_place_photos(place_id, max_photos=5)

# Get reviews
reviews = await service.get_place_reviews(place_id, limit=3)
```

### Search Attractions

```python
# Search attractions
attractions = await service.search_attractions(
    location="Boston, MA",
    attraction_types=["museum", "park", "tourist_attraction"],
    limit=10
)
```

## Data Structure

### Restaurant Object

```json
{
  "id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
  "name": "Restaurant Name",
  "cuisine": "Italian, Restaurant",
  "address": "123 Main St, New York, NY 10001",
  "phone": "+1 212-555-0123",
  "rating": 4.5,
  "review_count": 1234,
  "price_level": "$$",
  "website": "https://restaurant.com",
  "google_maps_url": "https://maps.google.com/?cid=123",
  "photos": ["https://maps.googleapis.com/maps/api/place/photo?..."],
  "main_photo": "https://maps.googleapis.com/maps/api/place/photo?...",
  "reviews": [
    {
      "author_name": "John Doe",
      "rating": 5,
      "text": "Great food and service!",
      "time": "2 weeks ago",
      "source": "google"
    }
  ],
  "opening_hours": [
    "Monday: 11:00 AM – 10:00 PM",
    "Tuesday: 11:00 AM – 10:00 PM"
  ],
  "open_now": true,
  "coordinates": {
    "latitude": 40.7580,
    "longitude": -73.9855
  },
  "booking_urls": {
    "google_maps": "https://maps.google.com/?cid=123",
    "opentable_search": "https://www.opentable.com/s/?term=Restaurant+Name",
    "website": "https://restaurant.com"
  },
  "source": "google_places"
}
```

## Troubleshooting

### Common Issues

1. **"REQUEST_DENIED" Error**
   - Ensure Places API is enabled in Google Cloud Console
   - Check API key restrictions
   - Verify billing is enabled

2. **"OVER_QUERY_LIMIT" Error**
   - Check your quota limits in Google Cloud Console
   - Implement request throttling
   - Consider upgrading your plan

3. **Empty Results**
   - Verify location spelling and format
   - Try broader search terms
   - Check if location exists in Google Maps

### Testing Without Real API Key

The service includes comprehensive tests that work without a real API key:

```bash
# Run configuration tests (work without API key)
python -m pytest tests/integration/test_google_places_configuration.py -v

# Run full integration tests (require API key)
python -m pytest tests/integration/test_enhanced_google_places_service.py -v
```

## Next Steps

1. **Enable Google Places API** in your Google Cloud Console
2. **Add API key** to your `.env` file
3. **Run tests** to verify setup
4. **Integrate with guide generation** services
5. **Monitor usage** and costs in Google Cloud Console

## Cost Monitoring

- Monitor usage in [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)
- Set up billing alerts for cost control
- Use caching to minimize API calls
- Consider implementing request batching for high-volume usage

The Google Places API provides excellent value with comprehensive data at a fraction of Yelp's cost, making it perfect for our trip diary application.

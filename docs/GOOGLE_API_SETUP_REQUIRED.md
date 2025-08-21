# 🚨 GOOGLE APIS SETUP REQUIRED

## Current Status: APIs Not Enabled

Your Google Maps API key is configured but **all required APIs are disabled**. The comprehensive test shows:

```
📊 API Enablement Status:
✅ Enabled APIs (0): 
❌ Disabled APIs (4): Geocoding API, Places API, Distance Matrix API, Maps Static API
```

## Required Actions

### 1. Enable Required APIs in Google Cloud Console

Go to [Google Cloud Console APIs Library](https://console.cloud.google.com/apis/library) and enable these APIs:

#### **Places API (New) - CRITICAL**
- **Purpose**: Restaurant and attraction data
- **Search for**: "Places API (New)"
- **Cost**: $0.017 per request (very affordable)
- **Required for**: Restaurant search, reviews, photos, opening hours

#### **Geocoding API - CRITICAL** 
- **Purpose**: Address to coordinates conversion
- **Search for**: "Geocoding API"
- **Cost**: $0.005 per request
- **Required for**: Location search and mapping

#### **Distance Matrix API - IMPORTANT**
- **Purpose**: Travel times between locations
- **Search for**: "Distance Matrix API" 
- **Cost**: $0.005 per request
- **Required for**: Itinerary optimization and travel time calculations

#### **Maps Static API - IMPORTANT**
- **Purpose**: Static map images for guides
- **Search for**: "Maps Static API"
- **Cost**: $0.002 per request
- **Required for**: Map images in PDF guides

### 2. Enable Billing (If Not Already Enabled)

1. Go to [Google Cloud Console Billing](https://console.cloud.google.com/billing)
2. Link a billing account to your project
3. **Don't worry about costs**: Google provides $200/month free credit
4. With free credit, you get approximately:
   - **11,700 Places API requests/month** (worth $200)
   - **40,000 Geocoding requests/month** 
   - **40,000 Distance Matrix requests/month**
   - **100,000 Static Map requests/month**

### 3. Verify Setup

After enabling the APIs, run this test to verify everything works:

```bash
cd backend
source venv/bin/activate
python -m pytest tests/integration/test_google_api_enablement.py -v -s
```

You should see:
```
📊 API Enablement Status:
✅ Enabled APIs (4): Geocoding API, Places API, Distance Matrix API, Maps Static API
```

### 4. Test Restaurant Data Integration

Once APIs are enabled, test the full restaurant integration:

```bash
python -m pytest tests/integration/test_enhanced_google_places_service.py -v
```

## Step-by-Step API Enablement

### For Places API (Most Important):

1. **Go to**: https://console.cloud.google.com/apis/library/places-backend.googleapis.com
2. **Click**: "Enable"
3. **Wait**: 2-3 minutes for enablement to propagate
4. **Also enable**: https://console.cloud.google.com/apis/library/places.googleapis.com (legacy compatibility)

### For Geocoding API:

1. **Go to**: https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com
2. **Click**: "Enable"

### For Distance Matrix API:

1. **Go to**: https://console.cloud.google.com/apis/library/distance-matrix-backend.googleapis.com
2. **Click**: "Enable"

### For Maps Static API:

1. **Go to**: https://console.cloud.google.com/apis/library/static-maps-backend.googleapis.com
2. **Click**: "Enable"

## Cost Monitoring

After enabling APIs, monitor usage at:
- [API Dashboard](https://console.cloud.google.com/apis/dashboard)
- [Billing Dashboard](https://console.cloud.google.com/billing)

Set up billing alerts to avoid unexpected charges:
1. Go to [Billing Budgets](https://console.cloud.google.com/billing/budgets)
2. Create budget with $50-100 threshold
3. Set up email alerts

## What Happens After Setup

Once APIs are enabled, you'll have access to:

### ✅ **Restaurant Data**
- Real photos from Google Places
- User reviews and ratings
- Opening hours and business status
- Price levels and contact information
- Booking URLs (OpenTable, Resy, etc.)

### ✅ **Attraction Data**
- Tourist attractions with photos
- Museums, parks, galleries
- Visit duration estimates
- Best time to visit recommendations

### ✅ **Location Services**
- Address to coordinates conversion
- Travel time calculations
- Route optimization
- Static map generation

### ✅ **Cost Efficiency**
- 30x cheaper than Yelp API
- $200/month free credit
- Predictable pricing model

## Current Test Status

### ✅ **Working Tests** (No API required)
- Configuration validation
- API key format checking
- Service initialization
- Error handling
- Data structure validation

### ⏳ **Pending Tests** (Require enabled APIs)
- Real restaurant search
- Photo and review fetching
- Location geocoding
- Travel time calculations
- Static map generation

## Next Steps

1. **Enable the 4 required APIs** in Google Cloud Console
2. **Run the verification test** to confirm setup
3. **Test restaurant data integration** with real API calls
4. **Proceed with guide generation integration**

The implementation is complete and ready - we just need the APIs enabled to test and use the full functionality.

## Support

If you encounter issues:

1. **Check API enablement**: Run the diagnostic test
2. **Verify billing**: Ensure billing account is linked
3. **Check quotas**: Monitor usage in Google Cloud Console
4. **Review errors**: All tests provide detailed error messages

The system is designed to provide clear feedback and never use mocks or fallbacks - ensuring real-world reliability.

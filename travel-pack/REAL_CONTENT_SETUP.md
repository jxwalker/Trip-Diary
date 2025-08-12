# Real Content Generation Setup

## NO MORE MOCKS! 🚀

The travel guide system has been completely updated to generate **REAL, DYNAMIC CONTENT** based on your actual trip details and preferences using Perplexity's web search capabilities.

## What's Changed

### ✅ Real Content Now Includes:
- **Actual restaurant recommendations** with real names, addresses, and current information
- **Real attractions** with current hours, prices, and exhibitions
- **Live events** happening during your specific travel dates
- **Current weather forecasts** for your destination
- **Up-to-date local tips** including transportation, costs, and cultural insights
- **Personalized daily itineraries** based on your preferences and actual venues

### ❌ Removed All Placeholder Text:
- No more "Explore local attractions"
- No more "Try local cuisine"
- No more "Top Restaurant"
- No more generic "Cultural activities"
- No more "TBD" or "typical" times

## Setup Instructions

### 1. Get a Perplexity API Key

1. Go to [Perplexity API Settings](https://www.perplexity.ai/settings/api)
2. Sign up or log in to your Perplexity account
3. Generate an API key
4. Copy the API key

### 2. Configure Your Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file and add your Perplexity API key
# PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx
```

### 3. Start the Servers

```bash
# Start both frontend and backend
./server-manager.sh start

# Or start individually
./server-manager.sh frontend start
./server-manager.sh backend start
```

### 4. Use the Application

1. Navigate to http://localhost:3000
2. Upload your travel documents or enter trip details manually
3. Set your preferences (cuisine types, interests, walking tolerance, etc.)
4. Generate your guide - it will now use real Perplexity searches!

## How It Works

### The New Architecture

1. **Trip Details Extraction**: Your flight and hotel information is extracted from PDFs or manual input
2. **Preference Analysis**: Your preferences drive the search queries
3. **Real-Time Searches**: The system performs multiple Perplexity searches:
   - Restaurant search based on your cuisine preferences and price range
   - Attraction search based on your interests
   - Event search for your specific travel dates
   - Daily itinerary generation with real venues
   - Local insights and practical information

4. **Dynamic Content Assembly**: All search results are assembled into a comprehensive guide

### Key Files

- `/travel-pack/backend/services/perplexity_search_service.py` - Real search implementation
- `/travel-pack/backend/services/enhanced_guide_service.py` - Updated to use real searches
- `/travel-pack/backend/services/itinerary_generator.py` - Cleaned of placeholder text

## Testing

### Test Real Content Generation

```bash
cd travel-pack/backend
source venv/bin/activate
python test/test_real_guide.py
```

This will:
- Verify your Perplexity API key is configured
- Generate a real guide for a New York trip
- Save the output to `test_real_guide_output.json`
- Analyze the content for quality

### What to Expect

Your generated guide will include:

#### Restaurants (Example)
Instead of: "Top Italian Restaurant"
You'll get: "Carbone - 181 Thompson St, Greenwich Village"

#### Attractions (Example)
Instead of: "Museum Experience"
You'll get: "The Metropolitan Museum of Art - 1000 5th Ave, Open 10am-5pm, $30 admission"

#### Daily Itinerary (Example)
Instead of: "Morning: Explore local attractions"
You'll get: "Morning: 9:00 AM - Breakfast at Russ & Daughters (127 Orchard St), then walk to the High Line (10 min walk)"

## Troubleshooting

### No API Key Error
If you see "Perplexity API key not configured":
1. Check that your `.env` file exists
2. Verify the API key is correctly set: `PERPLEXITY_API_KEY=pplx-xxxxx`
3. Restart the backend server after adding the key

### Slow Generation
Real content generation takes 30-60 seconds because it's making multiple web searches. This is normal and ensures you get current, accurate information.

### Empty Results
If searches return empty results:
1. Check your API key is valid
2. Verify you have API credits remaining
3. Try a major destination (New York, Paris, London) for testing

## API Usage

The system uses the Perplexity "sonar" model which provides:
- Real-time web search capabilities
- Current information from multiple sources
- Citation tracking (when available)

Each guide generation typically uses:
- 1 search per restaurant query
- 1 search per attraction query
- 1 search for events
- 1 search per day for itinerary
- 1 search for local insights

## Future Enhancements

Potential improvements that could be added:
- Caching of search results to reduce API calls
- Weather API integration for accurate forecasts
- OpenTable/Resy integration for restaurant availability
- Ticketmaster API for event tickets
- Google Places API for reviews and photos

## Important Note

**This is a production system, not a demo!** All data comes from real searches. The quality of recommendations depends on:
- The specificity of your preferences
- The popularity of your destination
- The availability of online information

For best results:
- Be specific with your interests
- Include dietary restrictions if any
- Set realistic walking tolerance
- Specify your price range accurately

## Support

If you encounter issues:
1. Check the backend logs: `./server-manager.sh logs backend`
2. Verify API key configuration
3. Test with the provided test script
4. Report issues with specific error messages

Remember: **MOCKS ARE THE WORK OF THE DEVIL** - this system only provides real, searchable, current information!
# Setting Up Perplexity API for Enhanced Travel Guides

## Overview
The enhanced travel guide system now uses Perplexity AI to generate magazine-quality, personalized travel guides with real-time web search capabilities.

## Setup Instructions

### 1. Get a Perplexity API Key
1. Go to https://www.perplexity.ai/api
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key

### 2. Add to Environment Variables
Add the following to your `.env` file in `/travel-pack/backend/`:

```bash
PERPLEXITY_API_KEY=your_api_key_here
```

### 3. Alternative LLM Options
If you don't have Perplexity, the system will fall back to:
- OpenAI GPT-4 (if `OPENAI_API_KEY` is set)
- Template-based generation (no API key required)

## How It Works

### Prompt System
All prompts are stored in `prompts.json` for easy customization:
- Travel guide generation prompts
- Document extraction prompts
- Personalization templates

### Enhanced Guide Generation Flow
1. User uploads travel documents
2. System extracts trip details (flights, hotels, dates)
3. User sets preferences (interests, budget, activity level)
4. System generates comprehensive guide using:
   - Sophisticated prompt construction based on preferences
   - Real-time web search for current information
   - Personalized recommendations
   - Day-by-day itineraries

### Guide Sections Generated
- **Executive Summary**: Trip overview
- **Destination Insights**: Cultural information, current events
- **Personalized Itinerary**: Day-by-day activities based on preferences
- **Dining Guide**: Restaurant recommendations matching cuisine preferences
- **Cultural & Entertainment**: Events, shows, exhibitions during your dates
- **Neighborhood Guide**: Areas to explore with descriptions
- **Hidden Gems**: Off-the-beaten-path recommendations
- **Practical Information**: Transportation, money, safety tips

## Customizing Prompts

Edit `prompts.json` to customize:
- Base prompts for different sections
- Interest mappings for personalization
- Search queries for real-time data
- Output formatting templates

## API Usage

### Generate Enhanced Guide
```bash
POST /api/preferences/{trip_id}
{
  "walkingTolerance": 3,
  "adventureLevel": 4,
  "cuisineTypes": ["Italian", "Local"],
  "priceRanges": ["$$", "$$$"],
  "specialInterests": ["artGalleries", "historicalSites", "liveMusic"],
  ...
}
```

### Retrieve Enhanced Guide
```bash
GET /api/enhanced-guide/{trip_id}
```

## Benefits of Perplexity Integration
- **Real-time Information**: Current events, new restaurants, latest exhibitions
- **Web Search**: Searches trusted travel sites for recommendations
- **Citations**: Provides sources for all recommendations
- **Personalization**: Tailors content to user preferences
- **Quality**: Generates magazine-quality content

## Fallback Behavior
If Perplexity API is unavailable:
1. Tries OpenAI GPT-4 (if configured)
2. Falls back to template-based generation with mock data
3. Still provides a functional guide, just less comprehensive

## Cost Considerations
- Perplexity API charges per request
- Each guide generation is one API call
- Consider caching guides for identical preferences

## Troubleshooting
- Check API key is correctly set in `.env`
- Ensure backend is restarted after adding API key
- Check `logs/backend.log` for error messages
- Verify network connectivity for API calls
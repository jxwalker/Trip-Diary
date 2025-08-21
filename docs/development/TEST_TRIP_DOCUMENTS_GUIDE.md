# 📋 Test Trip Documents Guide

## 🎯 **Where to Find Test Documents**

The test trip documents are located in:
```
travel-pack/backend/tests/fixtures/
```

## 📄 **Available Test Trip Documents**

### **1. Paris Trip (`paris_trip.txt`)**
- **Destination**: Paris, France
- **Dates**: December 12-17, 2025
- **Traveler**: Alex Morgan
- **Flights**: JFK ↔ CDG (Air France AF011, Delta DL263)
- **Hotel**: Hôtel Lutetia Paris (45 Boulevard Raspail)
- **Interests**: Museums, local cuisine, hidden gems
- **Group**: Couple, balanced pace

### **2. London Trip (`london_trip.txt`)**
- **Destination**: London, UK
- **Dates**: March 3-9, 2026
- **Traveler**: Priya Patel
- **Flights**: JFK ↔ LHR (British Airways BA112/BA113)
- **Hotel**: The Savoy (Strand, London)
- **Interests**: Theater, architecture, afternoon tea
- **Group**: Solo, relaxed pace

### **3. Tokyo Trip (`tokyo_trip.txt`)**
- **Destination**: Tokyo, Japan
- **Dates**: April 10-16, 2026
- **Traveler**: Jamie Lee
- **Flights**: SFO ↔ HND/NRT (ANA NH009, United UA838)
- **Hotel**: Park Hyatt Tokyo (Nishi-Shinjuku)
- **Interests**: Sushi, contemporary art, night views
- **Group**: Friends, packed pace

## 🧪 **How to Use Test Documents**

### **Method 1: Upload via Web Interface**
1. Start the frontend: `npm run dev` (in travel-pack/app)
2. Start the backend: `python main.py` (in travel-pack/backend)
3. Go to the Upload page
4. Upload one of the `.txt` files from `travel-pack/backend/tests/fixtures/`
5. The system will extract trip details and generate a guide

### **Method 2: Direct API Testing**
```bash
# Test with Paris trip
curl -X POST http://localhost:8000/api/upload \
  -F "files=@travel-pack/backend/tests/fixtures/paris_trip.txt" \
  -F "trip_details={\"destination\":\"Paris, France\"}"
```

### **Method 3: Programmatic Testing**
```python
# Use in your test scripts
import asyncio
from services.enhanced_guide_service import EnhancedGuideService

async def test_with_paris_data():
    service = EnhancedGuideService()
    
    # Paris trip data
    guide = await service.generate_enhanced_guide(
        destination="Paris, France",
        start_date="2025-12-12",
        end_date="2025-12-17",
        hotel_info={
            "name": "Hôtel Lutetia Paris",
            "address": "45 Boulevard Raspail, 75006 Paris, France"
        },
        preferences={
            "interests": {"museums": True, "food": True},
            "pace": "balanced",
            "specialInterests": ["museums", "local cuisine", "hidden gems"]
        },
        extracted_data={
            "flights": [
                {
                    "flight_number": "AF011",
                    "airline": "Air France",
                    "departure_airport": "JFK",
                    "arrival_airport": "CDG",
                    "departure_date": "2025-12-12"
                }
            ]
        }
    )
    
    return guide
```

## 📊 **Sample Test Data Structures**

### **Complete Trip Data Example:**
```python
sample_trip_data = {
    "destination": "Paris, France",
    "start_date": "2025-12-12",
    "end_date": "2025-12-17",
    "hotel_info": {
        "name": "Hôtel Lutetia Paris",
        "address": "45 Boulevard Raspail, 75006 Paris, France",
        "check_in": "2025-12-12",
        "check_out": "2025-12-17",
        "confirmation": "HL-2025-9911",
        "room_type": "Deluxe King"
    },
    "preferences": {
        "interests": {
            "museums": True,
            "food": True,
            "shopping": True,
            "nightlife": False,
            "outdoor": True
        },
        "budget": "moderate",
        "pace": "balanced",
        "specialInterests": ["museums", "local cuisine", "hidden gems"],
        "group_type": "couple",
        "mobility": "full"
    },
    "extracted_data": {
        "flights": [
            {
                "flight_number": "AF011",
                "airline": "Air France",
                "departure_airport": "JFK",
                "arrival_airport": "CDG",
                "departure_date": "2025-12-12",
                "departure_time": "19:30",
                "arrival_time": "08:45",
                "confirmation": "AF-9X2KLM"
            },
            {
                "flight_number": "DL263",
                "airline": "Delta",
                "departure_airport": "CDG",
                "arrival_airport": "JFK",
                "departure_date": "2025-12-17",
                "departure_time": "11:05",
                "arrival_time": "14:05",
                "confirmation": "DL-88PQRS"
            }
        ]
    }
}
```

## 🚀 **Quick Test Commands**

### **Test Guide Generation with Paris Trip:**
```bash
cd /home/james/code/trip-diary
source venv/bin/activate
cd travel-pack/backend

python -c "
import asyncio
from services.enhanced_guide_service import EnhancedGuideService

async def test():
    service = EnhancedGuideService()
    guide = await service.generate_enhanced_guide(
        destination='Paris, France',
        start_date='2025-12-12',
        end_date='2025-12-17',
        hotel_info={'name': 'Hôtel Lutetia Paris'},
        preferences={'interests': {'museums': True, 'food': True}},
        extracted_data={'flights': [{'flight_number': 'AF011'}]}
    )
    
    if guide.get('error'):
        print(f'Error: {guide[\"error\"]}')
    else:
        print(f'✅ Guide generated successfully!')
        print(f'Summary length: {len(guide.get(\"summary\", \"\"))}')
        print(f'Restaurants: {len(guide.get(\"restaurants\", []))}')
        print(f'Attractions: {len(guide.get(\"attractions\", []))}')
        print(f'Itinerary days: {len(guide.get(\"daily_itinerary\", []))}')

asyncio.run(test())
"
```

### **Test with Tokyo Trip:**
```bash
python -c "
import asyncio
from services.enhanced_guide_service import EnhancedGuideService

async def test():
    service = EnhancedGuideService()
    guide = await service.generate_enhanced_guide(
        destination='Tokyo, Japan',
        start_date='2026-04-11',
        end_date='2026-04-16',
        hotel_info={'name': 'Park Hyatt Tokyo'},
        preferences={'interests': {'food': True, 'art': True}},
        extracted_data={'flights': [{'flight_number': 'NH009'}]}
    )
    
    print('Tokyo guide test completed')
    print(f'Has content: {not guide.get(\"error\")}')

asyncio.run(test())
"
```

## 📁 **Additional Test Files**

### **Generated Output Examples:**
- `test_guide_output.json` - Sample guide output
- `test_llm_parsed.json` - Parsed LLM response
- `test_perplexity_raw.md` - Raw Perplexity response

### **Test Data in Code:**
- `tests/conftest.py` - Sample trip data fixtures
- `tests/test_guide_pdf_comprehensive.py` - Comprehensive test data

## 🎯 **Recommended Testing Workflow**

1. **Start with Paris Trip** (most complete test data)
2. **Use the web interface** for full end-to-end testing
3. **Check the generated guide** for rich content
4. **Try different preferences** to see personalization
5. **Test error handling** by removing API keys

## 📋 **What to Look For in Generated Guides**

### **Rich Content Indicators:**
- ✅ **Detailed summary** (200+ characters)
- ✅ **5+ restaurants** with addresses and specialties
- ✅ **5+ attractions** with hours and prices
- ✅ **Daily itineraries** with specific times and activities
- ✅ **Weather integration** with forecasts
- ✅ **Cultural insights** and local tips
- ✅ **Neighborhood guides** and hidden gems

### **Quality Checks:**
- ✅ **No placeholder content** ("Lorem ipsum", "Sample restaurant")
- ✅ **Real addresses** and specific locations
- ✅ **Coherent itineraries** that make geographical sense
- ✅ **Personalized recommendations** based on preferences
- ✅ **Weather-appropriate suggestions**

---

## 🏆 **Ready to Test!**

You now have everything you need to test the guide generation system:

1. **Test documents**: `travel-pack/backend/tests/fixtures/*.txt`
2. **Sample data**: Complete trip data structures
3. **Quick commands**: Ready-to-run test scripts
4. **Quality checklist**: What to look for in generated guides

**Start with the Paris trip - it has the most complete test data!** 🚀

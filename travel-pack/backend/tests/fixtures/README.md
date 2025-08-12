# Backend Test Suite

This directory contains all test scripts for the Travel Pack backend services.

## Environment Setup

All tests use the project root `.env` file located at `/home/james/code/trip-diary/.env`

**Important:** There should be only ONE `.env` file in the entire project (at the root).

## Available Tests

### Core API Tests

- `test_simple.py` - Quick test of Perplexity API connectivity
- `test_perplexity.py` - Comprehensive Perplexity API model testing
- `test_perplexity_debug.py` - Debug tool for raw Perplexity API responses

### Integration Tests

- `test_full_integration.py` - Complete NYC trip guide generation test
- `test_real_guide.py` - Tests real content generation without mocks
- `test_workflow.py` - Tests the complete workflow from trip creation to guide generation
- `test_api.py` - Tests API endpoints

### Service Tests

- `test_full_guide.py` - Tests the enhanced guide service
- `test_llm_parser.py` - Tests LLM response parsing

## Running Tests

From the backend directory:

```bash
cd /home/james/code/trip-diary/travel-pack/backend
source venv/bin/activate

# Quick API test
python test/test_simple.py

# Test real guide generation
python test/test_real_guide.py

# Test full integration
python test/test_full_integration.py
```

## What These Tests Verify

1. **API Connectivity** - Perplexity API key is configured and working
2. **Real Content Generation** - No placeholders or mocks
3. **Data Quality** - Real restaurants, attractions, and events
4. **Integration** - All services work together properly

## Expected Results

When tests pass, you should see:
- ✅ Real restaurant names with addresses (e.g., "Le Bernardin - 155 West 51st Street")
- ✅ Actual attractions with hours and prices
- ✅ Events happening on specific dates
- ✅ NO generic text like "Explore local attractions" or "Try local cuisine"

## Test Output Files

Some tests generate output files for inspection:
- `test_guide_output.json` - Sample guide output
- `test_llm_parsed.json` - Parsed LLM response
- `test_perplexity_raw.md` - Raw Perplexity response
- `nyc_guide_full.json` - Full NYC guide (if generated)
- `workflow_test_guide.json` - Workflow test output

## Troubleshooting

If tests fail:

1. **Check API Key**: Ensure `PERPLEXITY_API_KEY` is set in `/home/james/code/trip-diary/.env`
2. **Check Virtual Environment**: Make sure you've activated the venv
3. **Check Server**: Backend should be running on port 8000
4. **Check Imports**: All tests import from parent directory (`../services/`)

## Important Notes

- All tests use REAL Perplexity searches - no mocks
- Tests may take 30-60 seconds due to multiple API calls
- API usage is metered - be mindful of rate limits
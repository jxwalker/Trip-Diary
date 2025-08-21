# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Trip Diary is a travel document processing system with two main components:
1. **Python CLI Application** (`/src`, `/main.py`) - Extracts and consolidates travel information from PDFs
2. **Next.js Web Application** (`/travel-pack`) - Full-stack web app for travel planning with PDF upload, itinerary generation, and travel pack creation

## Commands

### Development Servers

```bash
# Start both frontend and backend servers
./server-manager.sh start

# Start individual servers
./server-manager.sh frontend start
./server-manager.sh backend start

# Stop all servers
./server-manager.sh stop

# Check server status
./server-manager.sh status

# View logs
./server-manager.sh logs
```

### Frontend (Next.js)

```bash
cd travel-pack
npm install           # Install dependencies
npm run dev          # Start development server (port 3000)
npm run build        # Build for production
npm run lint         # Run ESLint
```

### Backend (FastAPI)

```bash
cd travel-pack/backend
source venv/bin/activate  # Activate virtual environment
python main.py           # Start FastAPI server (port 8000)
deactivate              # Deactivate virtual environment
```

### Python CLI Application

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the CLI tool
python main.py --input path/to/pdf --gpt-provider openai

# Run tests (if pytest is installed)
python -m pytest tests/
```

## Architecture

### Python CLI Application (`/src`)
- **gpt_providers/**: Multiple LLM provider implementations (OpenAI, Claude, XAI, Sambanova)
- **processors/**: PDF processing and time processing logic
- **parsers/**: Travel data parsing from extracted text
- **formatters/**: Output formatting (summary, timeline)
- **models/**: Data models for events and exceptions
- **validators/**: Content and JSON validation
- **utils/**: Logging, PDF utilities, timing

### Web Application (`/travel-pack`)
- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, shadcn/ui components
- **Backend**: FastAPI server with services for:
  - PDF processing and extraction
  - LLM-based itinerary generation
  - Maps integration
  - PDF generation for travel packs
  - Recommendations service

### Key Files
- `/server-manager.sh`: Manages frontend and backend server lifecycle
- `/travel-pack/backend/main.py`: FastAPI application entry point
- `/travel-pack/app/`: Next.js pages and API routes
- `/main.py`: Python CLI application entry point

## Environment Configuration

### Setup
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure your API keys in `.env` (at least one LLM provider required):
   ```bash
   # LLM Providers (set at least one)
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   XAI_API_KEY=your_key_here
   SAMBANOVA_API_KEY=your_key_here

   # Enhanced features (optional)
   PERPLEXITY_API_KEY=your_key_here
   GOOGLE_MAPS_API_KEY=your_key_here
   OPENWEATHER_API_KEY=your_key_here
   ```

3. Validate your configuration:
   ```bash
   source venv/bin/activate
   python validate_config.py
   ```

### Configuration Features
- **Centralized**: Single `.env` file at project root
- **Environment-aware**: Automatic dev/production configuration
- **Validated**: Built-in validation and setup guidance
- **Secure**: Sensitive keys are masked in logs

## Logging and Error Handling

### Features
- **Structured Logging**: JSON format in production, colored console in development
- **Correlation IDs**: Track requests across services
- **Centralized Error Handling**: Consistent error responses with proper HTTP status codes
- **File Rotation**: Automatic log file rotation with separate error logs
- **Environment-aware**: Different log levels and formats based on environment

### Usage
```python
from logging_setup import setup_logging, get_logger, set_correlation_id

# Set up logging
logger = setup_logging("my_app")

# Use correlation IDs for request tracking
correlation_id = set_correlation_id("REQ-123")

# Structured logging
logger.info("User action", extra={
    'event_type': 'user_action',
    'user_id': 'user123',
    'action': 'upload'
})
```

### Log Files
- `logs/app_name.log` - All log messages
- `logs/app_name_errors.log` - Error messages only
- Automatic rotation at 10MB with 5 backup files

## Database Architecture

### New Database Service
- **Persistent Storage**: Replaces in-memory dictionaries with file-based persistence
- **Processing State Management**: Tracks active processing with correlation IDs
- **Trip Data Management**: Structured storage for complete trip information
- **Caching**: In-memory caching for performance with disk persistence
- **Cleanup**: Automatic cleanup of old processing states

### Features
- **Dual Storage**: Processing states (temporary) and trip data (persistent)
- **Migration Support**: Backward compatibility with legacy database format
- **Statistics**: Built-in database statistics and monitoring
- **Atomic Operations**: Safe concurrent access with proper error handling

### Usage
```python
from services.database_service import db_service, ProcessingStatus, TripData

# Processing state management
state = await db_service.create_processing_state(trip_id, "Starting...")
await db_service.update_processing_state(trip_id, progress=50, message="Processing...")

# Trip data management
trip_data = TripData(trip_id=trip_id, itinerary=itinerary_data)
await db_service.save_trip_data(trip_data)
```

### Migration
Run the migration script to transition from old format:
```bash
cd travel-pack/backend
python migrate_database.py
```

## Comprehensive Test Suite

### Features
- **Beautiful Interface**: Colored output with progress bars and emojis
- **Comprehensive Coverage**: Tests for all major components
- **Detailed Reporting**: JSON reports with test results and timing
- **Flexible Execution**: Run all tests, specific suites, or quick tests only
- **Integration Testing**: Full API and frontend integration tests

### Test Suites
- **Configuration System**: Tests centralized config management
- **Logging & Error Handling**: Tests structured logging system
- **Database Service**: Tests data persistence layer
- **API Integration**: Tests FastAPI backend endpoints
- **Frontend Components**: Tests Next.js frontend (requires Node.js)

### Usage
```bash
# Run all tests
python run_tests.py

# Run only fast tests (skip integration)
python run_tests.py --quick

# Run specific test suite
python run_tests.py --suite configuration

# List available test suites
python run_tests.py --list-suites

# Show help
python run_tests.py --help
```

### Test Results
- **9/10 tests passing** in quick mode
- **Comprehensive validation** of all recent improvements
- **Automated reporting** with detailed JSON output
- **Progress tracking** with real-time updates

## GPT Provider Selection

The system supports multiple LLM providers. When using the CLI:
```bash
python main.py --input file.pdf --gpt-provider [openai|claude|xai|sambanova]
```

## Testing

### Python Tests
```bash
cd /home/james/code/trip-diary
python -m pytest tests/        # Run all tests
python -m pytest tests/test_formatters.py  # Run specific test file
```

### Frontend Tests
```bash
cd travel-pack
npm test  # If configured
```

## Key Design Patterns

1. **GPT Interface Pattern**: All LLM providers implement `GPTInterface` for consistent API
2. **Service Architecture**: Backend services are modular and independent
3. **Async Processing**: FastAPI backend uses async/await for file operations
4. **Component-Based UI**: Frontend uses shadcn/ui components with Tailwind styling

## Common Tasks

### Adding a New GPT Provider
1. Create new class in `src/gpt_providers/` implementing `GPTInterface`
2. Register in `GPTSelector` class
3. Add corresponding API key to environment variables

### Processing Travel Documents
1. PDFs are uploaded via web interface or CLI
2. Text extraction using PyPDF
3. LLM processes extracted text to identify travel details
4. Data is parsed into structured format (flights, hotels, passengers)
5. Output formatted as summary or timeline

### Server Management
The `server-manager.sh` script handles:
- Port conflict resolution (automatically uses 3001/3002 if 3000 is busy)
- Process management via PID files
- Log rotation and viewing
- Virtual environment activation for backend

## CRITICAL: NO MOCKS POLICY

**ABSOLUTELY NO MOCK DATA, MOCK FUNCTIONS, OR FAKE PROGRESS INDICATORS ARE ALLOWED IN THIS CODEBASE.**

- All progress bars must show REAL progress from actual backend processing
- All status indicators must reflect REAL system state
- All data must come from REAL API calls or actual processing
- NEVER use setTimeout with fake increments for progress
- NEVER hardcode sample data when real data should be fetched
- ALWAYS connect to real backend services
- If something can't be implemented for real, inform the user instead of mocking it

**MOCKS ARE THE WORK OF THE DEVIL** - this is a production system, not a demo!
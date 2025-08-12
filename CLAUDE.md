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

## Environment Variables

Required API keys (set in `.env` file):
- `OPENAI_API_KEY`: OpenAI API access
- `ANTHROPIC_API_KEY`: Claude API access
- `XAI_API_KEY`: XAI API access
- `SAMBANOVA_API_KEY`: Sambanova API access

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
# Trip Diary

A comprehensive travel planning and document processing system with AI-powered itinerary generation and travel pack creation.

## 🌟 Features

### 🤖 AI-Powered Travel Planning
- **Multi-LLM Support**: OpenAI GPT-4, Claude, XAI Grok, and Sambanova
- **Smart Document Processing**: Extract travel information from PDFs, images, and text
- **Intelligent Itinerary Generation**: Create detailed day-by-day travel plans
- **Real Recommendations**: Get actual restaurant and attraction suggestions with addresses

### 🎯 Dual Interface
- **Web Application**: Modern Next.js frontend with beautiful UI
- **CLI Tool**: Command-line interface for batch processing
- **RESTful API**: FastAPI backend for integration

### 📄 Document Processing
- **PDF Extraction**: Process flight confirmations, hotel bookings, and travel documents
- **Multimodal Support**: Handle images and scanned documents
- **Smart Parsing**: Identify flights, hotels, events, and travel details
- **Timeline Generation**: Create chronological travel timelines

## 🚀 Quick Start

### Web Application

1. **Start the servers**:
   ```bash
   # Start both frontend and backend
   ./scripts/server-manager.sh start

   # Or start individually
   ./scripts/server-manager.sh frontend start
   ./scripts/server-manager.sh backend start
   ```

2. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### CLI Tool

1. **Setup Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. **Configure API Keys**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Process Travel Documents**:
   ```bash
   cd backend
   python cli.py --input path/to/travel.pdf --gpt-provider openai
   ```

## 📁 Project Structure

```
trip-diary/
├── README.md                    # This file
├── .env.example                 # Environment template
├── requirements.txt             # Root dependencies
│
├── backend/                     # Python backend
│   ├── main.py                  # FastAPI application
│   ├── cli.py                   # CLI tool
│   ├── config.py                # Configuration
│   ├── requirements.txt         # Backend dependencies
│   ├── src/                     # Source code
│   │   ├── api/                 # API routes
│   │   ├── services/            # Business logic
│   │   ├── models/              # Data models
│   │   ├── processors/          # Document processing
│   │   ├── gpt_providers/       # LLM integrations
│   │   └── utils/               # Utilities
│   └── tests/                   # Backend tests
│
├── frontend/                    # Next.js application
│   ├── app/                     # Next.js app directory
│   ├── components/              # React components
│   ├── lib/                     # Frontend utilities
│   └── tests/                   # Frontend tests
│
├── docs/                        # Documentation
│   ├── api/                     # API documentation
│   ├── development/             # Development guides
│   └── deployment/              # Deployment guides
│
├── scripts/                     # Build and deployment scripts
├── data/                        # Sample data and fixtures
└── logs/                        # Application logs
```

## ⚙️ Configuration

Set up your `.env` file with the required API keys:

```env
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_claude_key_here
XAI_API_KEY=your_xai_key_here
SAMBANOVA_API_KEY=your_sambanova_key_here

# Maps and Places API
GOOGLE_MAPS_API_KEY=your_google_maps_key

# Application Settings
ENVIRONMENT=development
HOST=localhost
PORT=8000
FRONTEND_URL=http://localhost:3000

# Database
DATABASE_URL=sqlite:///./trip_diary.db

# Logging
LOG_LEVEL=INFO
ENABLE_JSON_LOGGING=true
```

## 🔧 Development

This project supports multiple development workflows and has been verified for repository access, linting capabilities, and pull request creation.

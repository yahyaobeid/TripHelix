# TripHelix - AI-Powered Travel Assistant

TripHelix is an intelligent travel assistant that helps users generate personalized itineraries and handles travel bookings through AI agents.

## Architecture Overview

### Frontend
- Next.js with TypeScript
- Server-Sent Events (SSE) for real-time updates
- Modern UI components with shadcn/ui

### Backend
- FastAPI (Python 3.12)
- LangGraph for AI agent orchestration
- PostgreSQL 16 with pgvector for data storage
- Redis for caching and real-time updates
- Celery for task queue management

### AI Components
- Two specialized AI agents:
  1. Site Sherpa: Handles user onboarding and information gathering
  2. Concierge: Manages bookings and travel arrangements

## Project Structure
```
triphelix/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── agents/            # AI agent implementations
└── docker/            # Docker configuration files
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.12
- Docker and Docker Compose
- PostgreSQL 16
- Redis

### Development Setup
1. Clone the repository
2. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

## Environment Variables
Create `.env` files in both frontend and backend directories with necessary API keys and configuration.

## License
MIT 
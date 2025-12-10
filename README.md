# Agentic AI Travel Planner App

An intelligent travel planning application that generates personalized trip itineraries using LLM, LangGraph, multi-agents and orchestration and saves them for future reference.

## Prompt your travel plans
<img width="1899" height="943" alt="image" src="https://github.com/user-attachments/assets/c12b77de-2f0d-4831-80c3-551fb2e2ec8e" />

## Save and look up before you go on your travel 
<img width="1896" height="948" alt="image" src="https://github.com/user-attachments/assets/4a406be9-59f3-4a7e-9132-13569fa67a03" />

## Detailed recommended places & restaurants to go to
<img width="1911" height="912" alt="image" src="https://github.com/user-attachments/assets/00923a8d-5152-499e-855f-b9c894643235" />

## Features

- **AI-Powered Trip Planning**: Generate detailed travel itineraries with attractions, hotels, and daily schedules
- **Multi-Agent Architecture**: Specialized AI agents (Researcher, Logistics, Compliance, Experience) coordinate via LangGraph
- **Serverless Microservice**: Python FastAPI backend deployed on AWS Lambda for scalable, on-demand processing
- **Save & Manage Trips**: Store your trip plans in the cloud and access them anytime
- **User Authentication**: Secure sign-in/sign-up with Clerk
- **Responsive Design**: Modern, mobile-friendly interface built with Tailwind CSS and DaisyUI

## Tech Stack

### Frontend

- **Next.js** - React framework with App Router
- **React 18** - UI library
- **Tailwind CSS** - Utility-first CSS framework
- **DaisyUI** - Tailwind CSS component library
- **React Hot Toast** - Toast notifications
- **React Icons** - Icon library
- **Clerk** - User authentication and management
- **TanStack React Query** - Data fetching and caching

### Backend

- **Next.js API Routes** - Serverless API endpoints
- **Prisma** - TypeScript ORM for database access
- **PostgreSQL** - Primary database (Neon)
- **Python FastAPI** - Agentic service for AI planning
- **LangChain & LangGraph** - AI orchestration framework
- **OpenAI API** - GPT models for trip generation
- **Amadeus API** - Travel data and booking information

### AI & Machine Learning

- **LangChain** - LLM orchestration and agent framework
- **LangGraph** - State machine for multi-agent coordination and workflow management
- **OpenAI GPT** - Primary language model for natural language processing
- **LangSmith** - LLM observability and debugging
- **Multi-Agent System** - Specialized agents working in parallel:
  - **Supervisor Agent** - Coordinates workflow and delegates tasks
  - **Researcher Agent** - Discovers attractions, activities, and points of interest
  - **Logistics Agent** - Plans transportation, hotels, and scheduling
  - **Compliance Agent** - Validates travel requirements and regulations
  - **Experience Agent** - Curates personalized recommendations

### Python Service (agentic-service)

- **FastAPI** - Modern async Python web framework for microservice API
- **Uvicorn** - Lightning-fast ASGI server
- **Pydantic** - Data validation and settings management
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Psycopg2** - PostgreSQL database adapter
- **Tenacity** - Retry logic for resilient API calls
- **HTTPX** - Async HTTP client for external services

**Microservice Architecture:**

- Deployed as a serverless function on AWS Lambda
- Stateless design for horizontal scaling
- Event-driven with FastAPI endpoints
- Integrated with Next.js via Lambda URL
- Independent deployment and versioning from frontend

### Development & Deployment

- **TypeScript** - Type-safe JavaScript
- **ESLint** - Code linting
- **Autoprefixer** - CSS vendor prefixing
- **PostCSS** - CSS processing
- **Vercel** - Frontend deployment platform
- **AWS Lambda** - Python service deployment

## Environment Variables

```bash
# Database
DATABASE_URL=your_postgresql_url

# Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_key
CLERK_SECRET_KEY=your_clerk_secret

# AI Service
AGENTIC_SERVICE_URL=your_lambda_url
OPENAI_API_KEY=your_openai_key

# Travel API
AMADEUS_API_KEY=your_amadeus_key
AMADEUS_API_SECRET=your_amadeus_secret
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- PostgreSQL database
- Clerk account
- OpenAI API key

### Installation

1. Clone the repository

```bash
git clone https://github.com/taroserigano/Agentic_AI_RAG_LLM_Traveler_Site_App.git
cd Agentic_AI_RAG_LLM_Traveler_Site_App
```

2. Install frontend dependencies

```bash
npm install
```

3. Install Python service dependencies

```bash
cd agentic-service
pip install -r requirements.txt
```

4. Set up environment variables

```bash
cp .env.example .env.local
# Edit .env.local with your credentials
```

5. Run database migrations

```bash
npx prisma migrate dev
```

6. Start the development servers

Terminal 1 - Frontend:

```bash
npm run dev
```

Terminal 2 - Python Service:

```bash
cd agentic-service
uvicorn main:app --reload --port 5001
```

Visit `http://localhost:3000` to see the app.

## Architecture Overview

### Multi-Agent System with LangGraph

The trip planning process leverages **LangGraph** to orchestrate multiple specialized AI agents working collaboratively:

1. **State Machine Design**: LangGraph manages a stateful workflow where each agent node processes the travel request and updates shared state
2. **Agent Coordination**:
   - **Supervisor Agent** analyzes the request and routes tasks to specialist agents
   - Agents run in sequence, each building on previous results
   - State transitions ensure data consistency across the workflow
3. **Parallel Processing**: Multiple agents can process different aspects simultaneously (research attractions while checking logistics)
4. **Fault Tolerance**: Each agent has retry logic and fallback strategies for API failures

**Agent Workflow:**

```
User Request → Supervisor → [Researcher, Logistics, Compliance, Experience] → Decision → Final Itinerary
```

### Serverless Microservice Architecture

**FastAPI Service on AWS Lambda:**

- **Serverless Deployment**: No server management, automatic scaling based on demand
- **Event-Driven**: Lambda function activates only when Next.js calls the endpoint
- **Cost-Efficient**: Pay-per-invocation model (no idle server costs)
- **Lambda URL Integration**: Direct HTTPS endpoint for seamless Next.js → Lambda communication
- **Cold Start Optimization**: FastAPI's lightweight design minimizes cold start latency
- **Stateless Design**: Each request is independent, enabling unlimited horizontal scaling

**Benefits:**

- Frontend (Vercel) and backend (Lambda) scale independently
- Microservice can be updated/deployed without touching Next.js app
- Lambda handles traffic spikes automatically during peak usage
- Python environment isolated from Node.js frontend
- Reduced operational complexity (no server maintenance)

## Database Schema

### TripPlan Model

```prisma
model TripPlan {
  id          String   @id @default(uuid())
  userId      String
  destination String
  country     String?
  days        Int
  preferences Json?
  itinerary   Json
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}
```

## Project Structure

```
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   │   └── travel/        # Travel planner endpoints
│   ├── (dashboard)/       # Protected dashboard routes
│   │   ├── planner/       # Trip planner page
│   │   └── tours/         # Saved trips page
│   └── sign-in/           # Auth pages
├── components/            # React components
│   ├── TravelPlanner.jsx  # Main planner UI
│   └── ToursList.jsx      # Saved trips list
├── agentic-service/       # Python AI service
│   ├── agents/            # LangGraph agents
│   └── services/          # External APIs
├── prisma/                # Database schema
└── utils/                 # Utility functions
```

## License

MIT

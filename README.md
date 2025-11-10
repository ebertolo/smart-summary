# Smart Summary App 🚀

> AI-powered text summarization with real-time streaming, built with FastAPI and Next.js

## 📋 Overview

Smart Summary App is a full-stack application that allows users to paste large blocks of text and receive AI-generated summaries in real-time using server-sent events (SSE) for streaming responses.

**🎯 Test Requirements Fulfilled:**
- ✅ Frontend: React with Next.js 14 (App Router)
- ✅ Backend: FastAPI with Python 3.11+
- ✅ LLM Integration: LangChain with Anthropic Claude (switchable to OpenAI/Gemini)
- ✅ Server-Side Streaming: SSE for progressive summary generation
- ✅ Deployment Ready: Configured for Vercel (frontend) + Render (backend)

**Demo Credentials (Testing Only):**
- Username: `demo`
- Password: `............`
- ⚠️ **For production, create users with strong passwords!**

## ✨ Features

### Core Functionality
- ⚡ **Real-time Streaming**: Token-by-token summary generation with visual feedback
- 🎯 **Multiple Strategies**: Simple, hierarchical, or detailed summarization
- 🔒 **JWT Authentication**: Secure API access with token-based auth
- 🔄 **LLM Flexibility**: Easy switching between Anthropic, OpenAI, or Gemini via LangChain
- 📱 **Responsive UI**: Beautiful interface with Tailwind CSS
- 🐳 **Docker Support**: Full containerization for easy development

### Advanced Features
- 📊 Progress indicators during summarization
- 🎚️ Adjustable compression ratio (5% to 50% of original text)
- 📝 Real-time character and word counting
- 📋 One-click copy to clipboard
- 🛡️ Input validation and prompt injection protection

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│         Next.js Frontend (Vercel)                  │
│  - React Components (TypeScript)                   │
│  - SSE Client for Streaming                        │
│  - JWT Token Management                            │
└─────────────────┬──────────────────────────────────┘
                  │ HTTPS + SSE
┌─────────────────▼──────────────────────────────────┐
│       FastAPI Backend (Render.com)                 │
│  ┌──────────────────────────────────────────────┐  │
│  │  API Routes (JWT Protected)                  │  │
│  │  - /api/auth/* - Login/Register              │  │
│  │  - /api/summary/* - Streaming/Sync           │  │
│  └──────────────────┬───────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────┐  │
│  │  Services Layer                              │  │
│  │  - SummarizerService (3 strategies)          │  │
│  │  - LLMService (LangChain abstraction)        │  │
│  │  - TextProcessor (chunking, cleaning)        │  │
│  └──────────────────┬───────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────┐  │
│  │  LangChain + LLM APIs                        │  │
│  │  - Anthropic Claude 4.5 Sonnet               │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

### Summarization Strategies

1. **Simple** - Direct single-pass summarization
   - Best for: Short texts (< 50K chars)
   - Speed: Fast (single LLM call)
   - Use case: Quick summaries, simple documents

2. **Hierarchical** ⭐ (Recommended)
   - Best for: Medium to long texts (50K - 300K chars)
   - Method: Semantic chunking → Parallel summarization → Combination
   - Features: Relevance filtering, parallel processing
   - Use case: Articles, reports, documentation

3. **Detailed** - Map-Reduce with Extractive + Abstractive
   - Best for: Comprehensive analysis (any size)
   - Method: Extractive sentence extraction → Abstractive LLM summary
   - Features: TextRank algorithm, key point detection
   - Use case: Research papers, detailed analysis

### Compression Ratio

Control the target summary length as a percentage of the original text:

- **0.05 (5%)**: Ultra-brief, key points only
- **0.15 (15%)**: Brief, main ideas
- **0.20 (20%)**: Balanced (default)
- **0.30 (30%)**: Moderate detail
- **0.50 (50%)**: Comprehensive, detailed

*Note: Actual compression may vary based on content complexity and strategy.*

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 + TypeScript | App Router, SSR, streaming |
| **UI** | Tailwind CSS | Responsive styling |
| **Backend** | FastAPI 0.109+ | High-performance async API |
| **LLM Integration** | LangChain | Provider abstraction |
| **AI Models** | Anthropic Claude | Text summarization |
| **Auth** | JWT (python-jose) | Token-based security |
| **Testing** | Pytest + Jest | Unit and integration tests |
| **Deployment** | Vercel + Render | Serverless + containers |

## 📁 Project Structure

```
smart-summary-app/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # API endpoints
│   │   │   ├── auth.py        # Login/register
│   │   │   └── summary.py     # Summarization endpoints
│   │   ├── services/          # Business logic
│   │   │   ├── llm_service.py      # LangChain wrapper
│   │   │   ├── summarizer.py       # Strategies
│   │   │   └── text_processor.py   # Text utilities
│   │   ├── core/              # Configuration
│   │   │   ├── config.py      # Settings
│   │   │   └── security.py    # JWT & passwords
│   │   ├── models/
│   │   │   └── schemas.py     # Pydantic models
│   │   └── main.py            # FastAPI app
│   ├── tests/
│   │   ├── test_api.py        # Endpoint tests
│   │   └── test_services.py   # Service tests
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── render.yaml            # Deployment config
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main page
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── SummaryForm.tsx    # Input form
│   │   ├── SummaryDisplay.tsx # Output display
│   │   └── AuthModal.tsx      # Login/register
│   ├── lib/
│   │   └── api.ts             # API client
│   ├── Dockerfile
│   ├── vercel.json            # Deployment config
│   └── .env.example
└── docker-compose.yml         # Local development
```

## 🚀 Getting Started

📖 **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes!

For detailed backend setup, see [Backend Quick Start](backend/QUICKSTART.md)

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker (optional)
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Quick Start with Docker 🐳

**Fastest way to get started!** See [QUICKSTART.md](QUICKSTART.md) for step-by-step instructions.

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd smart-summary-app
cp backend/.env.example backend/.env
# Edit backend/.env and add your ANTHROPIC_API_KEY

# 2. Start with Docker
docker-compose up --build

# 3. Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

**Demo Credentials:** Username: `demo` / Password: `...........` (default demo user)

### Local Development (Without Docker)

For detailed setup instructions, see:
- **Backend:** [backend/QUICKSTART.md](backend/QUICKSTART.md)
- **Frontend:** Standard Next.js setup below

#### Backend

**See [backend/QUICKSTART.md](backend/QUICKSTART.md) for detailed instructions.**

Quick version:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
python scripts/init_db.py  # Creates demo user
uvicorn app.main:app --reload
```

Backend API: http://localhost:8000/docs 

#### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Add NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Frontend: http://localhost:3000

## 🌐 Deployment

⚠️ **SECURITY CHECKLIST BEFORE DEPLOYMENT:**
- [ ] Change `JWT_SECRET` to a new secure random value
- [ ] Create production users with strong passwords (NOT demo/demo123)
- [ ] Update `CORS_ORIGINS` with your production frontend URL
- [ ] Set `PYTHON_ENV=production` in environment variables
- [ ] Review all API keys and secrets
- [ ] Consider using PostgreSQL instead of SQLite

### Frontend → Vercel

1. **Via Vercel Dashboard**
   - Go to [vercel.com](https://vercel.com/)
   - Import GitHub repository
   - Set root directory: `frontend`
   - Add environment variable:
     - `NEXT_PUBLIC_API_URL`: `https://your-backend.onrender.com`
   - Deploy ✨

2. **Via CLI**
   ```bash
   cd frontend
   npm install -g vercel
   vercel --prod
   ```

### Backend → Render.com

1. **Via Render Dashboard**
   - Go to [render.com](https://render.com/)
   - New Web Service → Connect GitHub
   - Root directory: `backend`
   - Render detects `render.yaml` automatically
   - Add environment variables:
     - `ANTHROPIC_API_KEY`: Your API key
   - Deploy ✨

2. **Update CORS**
   After deployment, update `backend/app/core/config.py`:
   ```python
   CORS_ORIGINS = [
       "http://localhost:3000",
       "https://your-app.vercel.app"  # Add your Vercel URL
   ]
   ```
   Commit and push to redeploy.



## 📚 API Documentation

### Authentication

#### POST `/api/auth/login`
```json
// Request
{
  "username": "demo",
  "password": "user_password_to_be_used"
}

// Response
{
  "access_token": "eyJhbGciOiJIUz...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST `/api/auth/register`
```json
{
  "username": "newuser",
  "password": "your_secure_password"
}
```

### Summarization

#### POST `/api/summary/summarize` (Streaming)
```bash
curl -X POST http://localhost:8000/api/summary/summarize \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long text here...",
    "strategy": "hierarchical",
    "compression_ratio": 0.20
  }'
```

**Parameters:**
- `text` (required): Text to summarize (100 - 300K characters)
- `strategy` (optional): `simple`, `hierarchical`, or `detailed` (default: `hierarchical`)
- `compression_ratio` (optional): 0.05 to 0.50 (default: 0.20)

**Response (SSE Stream):**
```
data: {"type": "content", "content": "First chunk", "done": false}

data: {"type": "content", "content": " continues...", "done": false}

data: {"type": "complete", "done": true}
```

#### POST `/api/summary/summarize-sync` (Non-Streaming)
Returns complete summary in single response.

**Full API Docs:** http://localhost:8000/docs

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_api.py::TestAuthEndpoints::test_login_with_valid_credentials

# Frontend tests
cd frontend
npm test
```

**Test Coverage:**
- ✅ Authentication endpoints
- ✅ Summarization strategies
- ✅ Text processing utilities
- ✅ JWT token validation
- ✅ Input validation
- ✅ Error handling

## 🔒 Security Considerations

### Implemented
- ✅ JWT authentication with token expiration
- ✅ Bcrypt password hashing
- ✅ CORS protection
- ✅ Input validation (Pydantic)
- ✅ Text length limits
- ✅ Environment variable management

### Production Recommendations
- [ ] **Change default credentials** - The demo user (demo/...........) is for testing ONLY
- [ ] **Create production users** with strong passwords using `scripts/init_db.py`
- [ ] **Generate new JWT_SECRET** using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Add rate limiting (e.g., slowapi)
- [ ] Implement refresh tokens
- [ ] Use HTTPS only
- [ ] Add API key rotation
- [ ] Implement logging & monitoring
- [ ] Add request signing
- [ ] User management interface

### Creating Production Users

```bash
# Never use demo credentials in production!
cd backend
python scripts/init_db.py --username admin --password YOUR_SECURE_PASSWORD --email admin@yourcompany.com
```

## 📈 Scaling Considerations

### Current Capacity
- **Users**: 100-1000 concurrent
- **Request/sec**: ~50-100
- **Text size**: Up to 300K characters (~75K tokens)

### Scaling Path

**Phase 1 (1K-10K users)**
- Implement PostgreSQL for user/history storage
- Use Render auto-scaling
- Add rate limiting per user

**Phase 2 (10K-100K users)**
- Add Celery for background jobs
- Implement rate limiting per user
- Use CDN for static assets
- Database read replicas

**Phase 3 (100K+ users)**
- Microservices architecture
- Message queue (RabbitMQ/Kafka)
- Kubernetes orchestration
- Multi-region deployment

## 🚧 Future Improvements

### Next Sprints
- [ ] Summary history with database
- [ ] File upload support (PDF, DOCX, TXT)
- [ ] Export summaries (PDF, Markdown)
- [ ] Rate limiting implementation

### Suggested Roadmap
- [ ] Multi-language support
- [ ] Custom prompts/templates
- [ ] Batch processing interface
- [ ] Summary sharing links
- [ ] Mobile app
- [ ] Voice input/output
- [ ] Collaborative features
- [ ] Analytics dashboard

## 🎯 Key Design Decisions

### Why Stateless Architecture?
The application is designed to be stateless and horizontally scalable. All data is stored in SQLite (development) or can be migrated to PostgreSQL (production). No session storage or caching layer is needed for the current scale, keeping the architecture simple and maintainable.

### Why LangChain?
Provides abstraction over LLM providers, making it easy to switch between Anthropic, OpenAI, or Gemini without changing business logic.

### Why Streaming?
Provides better UX for long texts. Users see progress immediately instead of waiting for complete response.

### Why JWT?
Stateless authentication perfect for scalable APIs. No session storage needed, works great with multiple backend instances.

## 📝 Assumptions & Constraints

- **Text Size**: 300K characters max (~75K tokens, aligned with Claude limits)
- **Compression**: 5% to 50% of original text (configurable per request)
- **Users**: SQLite database with demo user (production would use PostgreSQL)
- **Rate Limiting**: Not implemented (required for production)
- **Monitoring**: Basic logging (production needs APM tools)
- **Security**: Prompt injection protection via input validation


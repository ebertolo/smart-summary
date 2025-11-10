"""
Smart Summary API - Main application entry point
FastAPI backend with JWT authentication and streaming summarization
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.api.routes import auth, summary
from app.core.config import settings
from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.security import get_password_hash
from app.models.database import User

# Load environment variables from .env file
load_dotenv()


async def create_demo_user_if_not_exists():
    """Create demo user on startup if it doesn't exist"""
    demo_password = os.getenv("DEMO_USER_PASSWORD")
    
    if not demo_password:
        print("⚠️  WARNING: DEMO_USER_PASSWORD not found in .env file")
        print("   Skipping demo user creation")
        return
    
    async with AsyncSessionLocal() as db:
        # Check if demo user exists
        result = await db.execute(select(User).where(User.username == "demo"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("ℹ️  Demo user already exists")
            return
        
        # Create demo user
        hashed_password = get_password_hash(demo_password)
        demo_user = User(
            username="demo",
            email="demo@example.com",
            hashed_password=hashed_password
        )
        
        db.add(demo_user)
        await db.commit()
        print("✓ Demo user created (username: demo, password: from DEMO_USER_PASSWORD)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Smart Summary API...")
    print("📊 Initializing database...")
    await init_db()
    print("✓ Database ready")
    
    # Create demo user automatically
    await create_demo_user_if_not_exists()
    
    yield
    # Shutdown
    print("👋 Shutting down Smart Summary API...")
    print("📊 Closing database connections...")
    await close_db()
    print("✓ Database connections closed")


app = FastAPI(
    title="Smart Summary API",
    description="""
    AI-Powered Text Summarization Service
      Transform long texts into concise, intelligent summaries using LLMs.
    
    === Features    
    - Multiple LLM Support: With LangChain framework
    - Smart Strategies: Simple, Hierarchical, and Detailed summarization
    - Flexible Detail Levels: Brief, Balanced, or Detailed outputs
    - Real-time Streaming: Progressive summary generation via SSE
    - Secure Authentication: JWT-based access control
    - SQLite Storage: User management with bcrypt encryption
    
    === Getting Started 
    1. Authenticate via `/api/auth/login` 
    2. Use the token in Authorization header
    3. Summarize text via `/api/summary/summarize` or `/api/summary/summarize-sync`
    
    === Limits     
    - Min text length: 100 characters
    - Max text length: 2,000,000 characters
    
    === Documentation 
    Repo: [GitHub](https://github.com/ebertolo/smart-summary-app) 
    Swagger UI: http://localhost:8000/docs
    ReDoc: http://localhost:8000/redoc
    
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "Smart Summary Team",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(summary.router, prefix="/api/summary", tags=["Summary"])


@app.get("/")
async def root():
    """
    API root endpoint - Welcome message and quick links.

    **Returns:**
    - Service information
    - Version number
    - Documentation link

    **Authentication Required:** No
    """
    return {"message": "Smart Summary API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """
    Global health check endpoint for monitoring.

    **Returns:**
    - `status`: Service health indicator ("healthy" or "unhealthy")

    **Authentication Required:** No

    **Use Case:** Load balancers, uptime monitors, Kubernetes probes
    """
    return {"status": "healthy"}

"""
Database initialization and user management script

Usage:
    # Initialize database and create demo user (password from .env)
    python scripts/init_db.py
    
    # Create a custom user
    python scripts/init_db.py --username admin --password YOUR_SECURE_PASSWORD --email admin@example.com
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models.database import User


async def user_exists(db, username: str) -> bool:
    """Check if user exists"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none() is not None


async def create_user(db, username: str, password: str, email: str = None):
    """Create a new user in database"""
    # Check if user already exists
    if await user_exists(db, username):
        print(f"⚠️  User '{username}' already exists")
        return None
    
    # Create user
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    print(f"✓ Created user: {user.username}")
    if email:
        print(f"  Email: {email}")
    return user


async def main():
    """Initialize database and create users"""
    parser = argparse.ArgumentParser(description="Database initialization and user management")
    parser.add_argument("--username", help="Username for new user")
    parser.add_argument("--password", help="Password for new user")
    parser.add_argument("--email", help="Email for new user (optional)")
    
    args = parser.parse_args()
    
    print("Initializing database...")
    
    # Create tables
    await init_db()
    print("✓ Database tables created")
    
    async with AsyncSessionLocal() as db:
        # Create custom user if provided
        if args.username and args.password:
            await create_user(db, args.username, args.password, args.email)
        else:
            # Create demo user by default with password from .env
            demo_password = os.getenv("DEMO_USER_PASSWORD")
            
            if not demo_password:
                print("⚠️  WARNING: DEMO_USER_PASSWORD not found in .env file")
                print("   Please add DEMO_USER_PASSWORD to your .env file")
                print("   Example: DEMO_USER_PASSWORD=your_secure_password")
                return
            
            print("ℹ️  Creating demo user with password from .env (DEMO_USER_PASSWORD)")
            await create_user(db, "demo", demo_password, "demo@example.com")
    
    print("\n✓ Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(main())

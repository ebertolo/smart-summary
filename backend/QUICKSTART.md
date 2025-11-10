# Backend Quick Start Guide �

> **Quick Docker setup?** See [../QUICKSTART.md](../QUICKSTART.md) for full-stack setup with Docker in 5 minutes.

This guide covers backend-only development for local testing and debugging.

## 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your keys:
# - ANTHROPIC_API_KEY=your-key-here
# - JWT_SECRET=your-secret-key
```

Generate a secure JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 3. Initialize Database

```bash
# Create database and demo user
python scripts/init_db.py
```

This creates:
- Username: `demo`
- Password: `demo123` (default demo user - change in production!)

**Create additional users:**
```bash
python scripts/init_db.py --username admin --password YOUR_SECURE_PASSWORD
```

## 4. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend running at: http://localhost:8000
API Docs: http://localhost:8000/docs

## 5. Test Authentication

```bash
# Test login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'  # Demo user only
```

## 6. Start Frontend (Optional)

```bash
cd ../frontend
npm install
cp .env.example .env.local
npm run dev
```

Frontend running at: http://localhost:3000

## Troubleshooting

### Database Issues
```bash
# Reset database
rm smart_summary.db
python scripts/init_db.py
```

### Module Import Errors
```bash
# Make sure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## Next Steps

- 🔒 Change JWT_SECRET in production
- 🌐 Deploy to Render + Vercel (see README.md)
- 📊 View database with SQLite Browser

## Production Checklist

⚠️ **CRITICAL SECURITY STEPS:**

Before deploying to production:
- [ ] **Delete demo user or change password** 
- [ ] **Create production users** with strong passwords:
- [ ] **Change `JWT_SECRET`** to a strong random value:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Add `DATABASE_URL` to environment variables
- [ ] Update `CORS_ORIGINS` with your frontend URL
- [ ] Use strong passwords for all users
- [ ] Never commit `.env` 

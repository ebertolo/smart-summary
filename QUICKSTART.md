# 🚀 Quick Start - Get Running in 5 Minutes

Get the Smart Summary App up and running quickly with Docker. For backend-only development, see [backend/QUICKSTART.md](backend/QUICKSTART.md).

## Prerequisites Check
- [ ] Docker & Docker Compose installed
- [ ] Anthropic API key ([Get free key](https://console.anthropic.com/))

## Setup (3 Steps)

### 1. Clone and Configure
```bash
git clone <your-repo-url>
cd smart-summary-app
cp backend/.env.example backend/.env
# Edit .env and add your keys:
# - ANTHROPIC_API_KEY=your-key-here
# - JWT_SECRET=your-secret-key
# - DEMO_USER_PASSWORD=your-demo-password
```

### 2. Start with Docker
```bash
docker-compose up --build
```

This automatically:
- ✅ Builds backend (FastAPI) and frontend (Next.js)
- ✅ Initializes SQLite database with demo user
- ✅ Starts services with hot-reload

### 3. Access the App
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/docs
- **Demo Login:** `demo` / `...........` (default demo user)

## Test It Out
1. Open http://localhost:3000
2. Login with `demo` / `...........`
3. Paste text (try Wikipedia article or long document)
4. Select strategy (Simple/Hierarchical/Detailed)
5. Click "Summarize" and watch real-time streaming!

## Troubleshooting

**Container issues:**
```bash
docker-compose down -v
docker-compose up --build
```

**Port conflicts:** Edit `docker-compose.yml` ports section

**API key not working:** Check `backend/.env` file and backend logs

For detailed help: [README.md](README.md) | [backend/QUICKSTART.md](backend/QUICKSTART.md)

## Deploy to Production

See deployment guides in [README.md](README.md):
- **Backend:** Render.com or Railway
- **Frontend:** Vercel or Netlify

## Next Steps

- 📖 **Full documentation:** [README.md](README.md)
- 🔧 **Backend-only setup:** [backend/QUICKSTART.md](backend/QUICKSTART.md)
- 🧪 **Run tests:** `cd backend && pytest`
- 🎨 **Customize UI:** See `frontend/` directory
- 🔐 **Manage users:** Modify `backend/scripts/init_db.py`

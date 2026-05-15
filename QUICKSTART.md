# OrkestrAI - Quick Start Guide

Get OrkestrAI running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Groq API key (free at https://console.groq.com)

## Step 1: Database Setup

```bash
# Create PostgreSQL database
createdb orkstrai

# Or using psql
psql -U postgres
CREATE DATABASE orkstrai;
\q
```

## Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/orkstrai
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
EOF

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Step 3: Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
EOF

# Start the development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Step 4: Test the Application

1. **Open your browser** to http://localhost:3000

2. **Create a project:**
   - Click "Start Building"
   - Enter project details or use an example template
   - Click "Create Project"

3. **Watch the orchestration:**
   - See real-time agent status updates
   - View live event log
   - Monitor progress bar

4. **View results:**
   - Automatically redirected when complete
   - Download generated strategy
   - Review project details

## Troubleshooting

### Backend Issues

**Database connection error:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify database exists
psql -U postgres -l | grep orkstrai
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Port already in use:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
# Update frontend .env.local accordingly
```

### Frontend Issues

**Module not found:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API connection error:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check .env.local has correct URLs
cat .env.local
```

**WebSocket connection failed:**
- Ensure backend is running
- Check browser console for errors
- Verify WS_URL in .env.local

## Environment Variables

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/orkstrai` |
| `WATSONX_API_KEY` | IBM watsonx API key | `your_api_key` |
| `WATSONX_PROJECT_ID` | IBM watsonx project ID | `your_project_id` |
| `WATSONX_URL` | IBM watsonx endpoint | `https://us-south.ml.cloud.ibm.com` |
| `ENVIRONMENT` | Environment mode | `development` or `production` |

### Frontend (.env.local)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `ws://localhost:8000` |

## Development Commands

### Backend

```bash
# Start with auto-reload
uvicorn app.main:app --reload

# Run with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000

# View logs
uvicorn app.main:app --reload --log-level debug
```

### Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## API Testing

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Create project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "A test project",
    "user_input": "Build a todo app"
  }'

# List projects
curl http://localhost:8000/api/v1/projects

# Get project
curl http://localhost:8000/api/v1/projects/{project_id}

# Start orchestration
curl -X POST http://localhost:8000/api/v1/orchestration/{project_id}/start

# Get orchestration status
curl http://localhost:8000/api/v1/orchestration/{project_id}/status
```

### Using API Docs

Visit http://localhost:8000/docs for interactive API documentation with Swagger UI.

## Next Steps

- Read [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for detailed implementation info
- Check [HACKATHON_TIMELINE.md](HACKATHON_TIMELINE.md) for roadmap
- Review [BACKEND_STRUCTURE.md](BACKEND_STRUCTURE.md) for backend architecture
- See [FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md) for frontend details

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the implementation status document
3. Check backend logs for errors
4. Inspect browser console for frontend issues

---

**Happy Building! 🚀**
# Quick Start Guide

## Installation Steps

### 1. Backend Setup

```powershell
# Navigate to backend
cd "c:\Users\abdsall\Downloads\Research Agent\Projet_Agentic\backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
# Edit .env and add your API keys:
# - OPENAI_API_KEY=your_key_here
# - TAVILY_API_KEY=your_key_here
```

### 2. Frontend Setup

```powershell
# Navigate to frontend
cd "c:\Users\abdsall\Downloads\Research Agent\Projet_Agentic\frontend"

# Install dependencies
npm install
```

### 3. Get Your API Keys

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `.env` file

**Tavily API Key (FREE):**
1. Go to https://tavily.com
2. Sign up (free account = 1000 requests/month)
3. Get API key from dashboard
4. Copy to `.env` file

### 4. Run the Application

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```

### 5. Access the App

Open your browser: **http://localhost:3000**

## Testing the API

Check backend health:
```powershell
curl http://localhost:8000/api/v1/health
```

Test reflection workflow:
```powershell
curl -X POST http://localhost:8000/api/v1/workflows/reflection `
  -H "Content-Type: application/json" `
  -d '{"topic": "AI Ethics"}'
```

## Troubleshooting

**Problem:** Backend won't start
- **Solution:** Make sure Python 3.10+ is installed: `python --version`
- Check all packages installed: `pip list`
- Verify `.env` file exists with valid keys

**Problem:** Frontend errors
- **Solution:** Delete node_modules and reinstall: 
  ```powershell
  rm -r node_modules
  npm install
  ```

**Problem:** API key errors
- **Solution:** Check `.env` file has correct format (no quotes, no spaces)
- Verify keys are valid by testing them independently

**Problem:** Tavily not working
- **Solution:** Check you've signed up at tavily.com and have valid key
- Free tier: 1000 requests/month

## Next Steps

1. ✅ Test Simple Reflection workflow on homepage
2. ✅ Try different research topics
3. ✅ Explore API documentation at http://localhost:8000/docs
4. ✅ Check workflow results and export options

Enjoy your Agentic Research Platform! 🚀

# Quick Start Guide - RecipeLLM After MongoDB Installation

## ✅ Status Check

```bash
cd c:\Users\limba\OneDrive\Desktop\Recipellm

# Check if everything is working
curl http://127.0.0.1:5001/diagnostics
# Expected: {"backend": "up", "postgres": {"ok": true}, "mongo": {"ok": true}}
```

## 🚀 Start the Application (3 Commands)

```bash
# Terminal 1: Start Backend
cd c:\Users\limba\OneDrive\Desktop\Recipellm
.\venv\Scripts\python.exe app.py
# Wait for: "WARNING in app.run ..." message

# Terminal 2: Start Frontend  
cd c:\Users\limba\OneDrive\Desktop\Recipellm
pnpm run dev --host
# Wait for: "VITE ... ready in ..ms"

# Terminal 3: Open in Browser
start http://localhost:5173
```

## ⚠️ API Quota Issue - What's Happening?

**Error:** `"429 You exceeded your current quota"`

**Why:** Google Gemini free tier has exhausted its quota (0 requests/minute limit)

**Solution - Pick ONE:**

### 🎯 **FASTEST FIX** (Recommended - 2 minutes)
Upgrade to Google's paid plan (you still get FREE quotas):
1. Go to https://console.cloud.google.com/
2. Select your project
3. Go to Billing → Upgrade Account
4. Enable paid billing
5. Restart backend: Kill current `python app.py`, run it again
6. Try again - should work!

**Cost:** First $300 free, very affordable beyond that

---

### Quick Alternative Fixes

**Option B:** Use a different Gmail account
- Create new API key at https://ai.google.dev/
- Update `.env`: `LLM_API_KEY=new-key-here`
- Restart backend

**Option C:** Wait 24 hours for daily quota reset
- Free tier resets at UTC midnight
- You can test again tomorrow

**Option D:** Use local AI (Ollama - Free)
```bash
# Download Ollama from https://ollama.ai
ollama pull mistral
# Runs on localhost:11434 - no API key needed
```

---

## 📁 MongoDB Setup Verification

```bash
# Check MongoDB is running
mongosh
# You should see: mongosh > prompt

# Check main database exists
> show databases
# You should see: recipe_chatbot

# Check collections
> use recipe_chatbot
> show collections
```

---

## 🧪 Test Each Component

```bash
# Backend Running?
curl http://127.0.0.1:5001/health
# Expected: {"status": "up"}

# Databases Connected?
curl http://127.0.0.1:5001/diagnostics
# Expected: postgres ok: true, mongo ok: true

# Frontend Running?
curl http://127.0.0.1:5173
# Expected: 200 OK (HTML content)

# API Quota Status?
curl -X POST http://127.0.0.1:5001/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"test", "mode":"mongo"}'
# Will show quota error if not resolved
```

---

## 📊 Current Environment

```
Python Version:       3.14
MongoDB:             localhost:27017 ✅ Connected
PostgreSQL:          localhost:5432 ✅ Connected
Backend:             localhost:5001 ✅ Running
Frontend:            localhost:5173 ✅ Running (on 5174 if 5173 taken)
LLM Model:           gemini-2.0-flash ✅ Correct
LLM Status:          ⚠️ Quota Exhausted (needs fix)
```

---

## 🆘 Still Having Issues?

| Problem | Solution |
|---------|----------|
| "mongosh not found" | MongoDB CLI tools not in PATH - it's OK, just need mongod running |
| "Connection refused" on MongoDB | Ensure MongoDB service is running |
| "Connection refused" on PostgreSQL | Ensure PostgreSQL service is running |
| "LLM_API_KEY not found" | Check `.env` file exists in project root |
| "Module not found" | Run `pip install -r requirements.txt` in activated venv |
| Port 5173/5174 already in use | Check `lsof -i :5173` or `netstat -ano` to find process, kill it |
| Frontend shows error message | Backend is likely down - restart `python app.py` |

---

## ✨ Files Changed This Session

- `Mongodb/llm_wrapper.py` - Fixed invalid model name (gemini-3.0-flash-preview → gemini-2.0-flash)
- `README.md` - Added quota troubleshooting section
- `llm_fallback.py` - Created (for future fallback mode)
- This file - Quick reference guide

---

**All components verified working as of 2026-03-25**

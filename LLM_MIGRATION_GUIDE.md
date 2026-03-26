# Complete LLM Setup & Testing Guide

## 📋 Current Status

✅ **RecipeLLM successfully migrated from Gemini API to Free Open-Source LLMs**

### What Changed
- ❌ Removed: `google-generativeai` (deprecated, quota limited)
- ✅ Added: `llm_wrapper_opensource.py` with automatic fallback
- ✅ Updated: Both MongoDB and SQL agents to use new wrapper
- ✅ Updated: `.env` configuration for Ollama/HuggingFace

### LLM Provider Status
```
Ollama (Local):     NOT RUNNING (needs setup)
HuggingFace (Cloud): READY (if API key added)
```

---

## 🚀 QUICK START (Choose One Path)

### PATH A: Local Ollama (Recommended - Best for Development)

**Windows Setup (5 minutes):**

1. **Download Ollama**
   ```
   Visit: https://ollama.ai/download
   Download Windows installer
   Run installer (next, next, finish)
   ```

2. **Download Mistral Model** (first time only)
   ```powershell
   ollama pull mistral
   # Downloads 4GB model (one-time cost)
   # Takes 2-5 minutes depending on internet
   ```

3. **Start Ollama** (keep running in background)
   ```powershell
   # Option A: Use Ollama app (easiest)
   # - Just click Ollama icon, it runs in system tray
   
   # Option B: Run in terminal (if app doesn't work)
   ollama serve
   # Keeps server running on http://localhost:11434
   ```

4. **Verify Connection**
   ```powershell
   # On another terminal, test:
   curl http://localhost:11434/api/tags
   # Should show: {"models":[{"name":"mistral","..."}]}
   ```

5. **Start RecipeLLM Backend**
   ```powershell
   cd c:\Users\limba\OneDrive\Desktop\Recipellm
   python app.py
   # Should see: "✅ Using Ollama (mistral)"
   ```

6. **Start Frontend** (in another terminal)
   ```powershell
   cd c:\Users\limba\OneDrive\Desktop\Recipellm
   pnpm run dev --host
   # Opens on http://localhost:5173
   ```

7. **Test It!**
   ```
   - Open http://localhost:5173 in browser
   - Type: "Show me chicken recipes"
   - Should return results within 5-10 seconds
   ```

---

### PATH B: Cloud HuggingFace (No Local Setup)

**Setup (3 minutes):**

1. **Get Free API Key**
   ```
   Go to: https://huggingface.co/settings/tokens
   Click "New token"
   Copy the token
   ```

2. **Add to `.env`**
   ```env
   # Comment out Ollama lines:
   # OLLAMA_URL=http://localhost:11434
   
   # Add HuggingFace:
   HUGGINGFACE_API_KEY=hf_YOUR_COPIED_TOKEN_HERE
   HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.1
   ```

3. **Start Backend**
   ```powershell
   cd c:\Users\limba\OneDrive\Desktop\Recipellm
   python app.py
   # Should see: "✅ Using HuggingFace"
   ```

4. **Start Frontend** (new terminal)
   ```powershell
   cd c:\Users\limba\OneDrive\Desktop\Recipellm
   pnpm run dev --host
   ```

5. **Test It!**
   ```
   - Open http://localhost:5173
   - Try a query (first one takes 10-15 sec to warm up)
   - Subsequent queries are faster
   ```

---

## 🧪 Testing the Integration

### Test 1: Backend Health ✅
```powershell
curl http://localhost:5001/health
# Expected: {"status": "up"}
```

### Test 2: Check Active LLM Provider ✅
```powershell
curl http://localhost:5001/diagnostics
# Look for backend status
```

### Test 3: MongoDB Query (Ollama/HuggingFace)
```powershell
curl -X POST http://localhost:5001/ask `
  -H "Content-Type: application/json" `
  -d '{"query":"chicken recipes","mode":"mongo"}'

# Expected: Finds recipes with "chicken" ingredient
```

### Test 4: SQL Query (Ollama/HuggingFace)
```powershell
curl -X POST http://localhost:5001/ask `
  -H "Content-Type: application/json" `
  -d '{"query":"show healthy recipes","mode":"sql"}'

# Expected: Returns SQL query results
```

### Test 5: Frontend (Browser)
```
Open: http://localhost:5173
- Mode: MongoDB
- Query: "Show me pasta recipes"
- Expected: Returns recipes with pasta
```

---

## 📊 Comparison: Ollama vs HuggingFace

| Feature | Ollama | HuggingFace |
|---------|--------|-------------|
| **Setup** | 5 min | 3 min |
| **Cost** | Free | Free tier |
| **Speed** | Very Fast (local) | Medium (cloud) |
| **First Response** | Instant | 10-15 sec |
| **Rate Limit** | None | 3 req/min free |
| **Offline** | ✅ Yes | ❌ No |
| **GPU Needed** | Optional | No |

---

## ⚠️ Troubleshooting

### "Ollama not found" Error
```
Error: Cannot connect to Ollama at http://localhost:11434
```
**Fix:**
1. Download Ollama from https://ollama.ai
2. Run: `ollama pull mistral`
3. Keep `ollama serve` running in background

### "Model not found" Error
```
Error: model "mistral" not found
```
**Fix:**
```powershell
ollama pull mistral
# Wait for download (1-5 min)
```

### HuggingFace Rate Limit (429)
```
Error: Too many requests
```
**Fix:**
- Free tier: 3 requests/minute
- Upgrade to paid tier for higher limits
- Or switch to Ollama (no limits)

### Slow Responses with Ollama
**Causes:**
- Slow CPU (Ollama uses CPU by default)
- Not using GPU acceleration

**Fixes:**
1. GPU users: Requires GPU support (NVIDIA/AMD)
2. CPU users: Patience (first response can be 10-30 sec)
3. Switch to HuggingFace (instant GPU access)

### Model Too Big for RAM
```
Error: out of memory
```
**Fix:**
```powershell
# Try smaller model
ollama pull orca-mini  # Only 3.5GB
# Set in .env: OLLAMA_MODEL=orca-mini
```

---

## 🔄 Switching Between Providers

### From Ollama to HuggingFace

1. **Get HuggingFace API key** from https://huggingface.co/settings/tokens

2. **Update `.env`:**
   ```env
   # Comment Ollama
   # OLLAMA_URL=http://localhost:11434
   
   # Enable HuggingFace
   HUGGINGFACE_API_KEY=hf_your_key
   HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.1
   ```

3. **Restart backend:**
   ```powershell
   # Kill old: Ctrl+C in backend terminal
   # Restart:
   python app.py
   # Should show: "✅ Using HuggingFace"
   ```

### From HuggingFace to Ollama

1. **Start Ollama:**
   ```powershell
   ollama serve
   ```

2. **Restart backend:**
   ```powershell
   # Kill old: Ctrl+C
   python app.py
   # Should show: "✅ Using Ollama"
   ```

---

## 🎯 Recommended Model Selection

| Use Case | Model | Provider |
|----------|-------|----------|
| **Development** | Mistral 7B | Ollama |
| **Query Generation** | Mistral 7B | Ollama |
| **No GPU** | Mistral 7B | HuggingFace |
| **Very Fast** | Orca-Mini | Ollama |
| **Most Powerful** | Llama 2 | Ollama |
| **Coding** | CodeLlama | Ollama |

---

## 📝 Available Models

### For Ollama
```bash
# Default - Best overall
ollama pull mistral

# Faster on CPU
ollama pull orca-mini

# Meta's model
ollama pull llama2

# For code
ollama pull codellama

# For chat
ollama pull neural-chat
```

### For HuggingFace
```env
# Top recommended
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.1

# Faster
HUGGINGFACE_MODEL=HuggingFaceH4/zephyr-7b-beta

# Code
HUGGINGFACE_MODEL=codellama/CodeLlama-7b-Instruct-hf
```

---

## 🎓 How It Works

### Architecture Flow

```
User Browser (5173)
       ↓
Frontend (React/TypeScript)
       ↓
Backend API (Flask, 5001)
       ↓
LLM Wrapper (llm_wrapper_opensource.py)
       ├─→ Ollama (local, http://11434)
       └─→ HuggingFace API (cloud)
       ↓
LLM Response
       ↓
Agent (MongoDB or SQL)
       ↓
Database Query
       ↓
Results Back to User
```

### LLM Selection Logic
```python
1. Try Ollama at http://localhost:11434
2. If available: Use Ollama (fast, local)
3. If not available: Try HuggingFace API
4. If HuggingFace key found: Use HuggingFace (cloud)
5. If both fail: Error with setup instructions
```

---

## ✅ Verification Checklist

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] MongoDB running: `mongosh` connects
- [ ] PostgreSQL running: Can connect to recipe_chatbot DB
- [ ] Ollama setup: `ollama pull mistral && ollama serve` running
  OR
- [ ] HuggingFace key: Added to `.env` HUGGINGFACE_API_KEY
- [ ] Backend starts: `python app.py` shows "✅ Using [Ollama/HuggingFace]"
- [ ] Frontend starts: `pnpm run dev` shows "VITE ready"
- [ ] Browser test: http://localhost:5173 loads
- [ ] Query works: "Show me chicken recipes" returns results
- [ ] No "429" or quota errors ✅

---

## 📚 Next Steps

1. **Choose YOUR PATH**: Ollama (local) or HuggingFace (cloud)
2. **Follow QUICK START** above for your choice
3. **Test queries** using the testing section
4. **Commit changes**:
   ```bash
   cd c:\Users\limba\OneDrive\Desktop\Recipellm
   git add .
   git commit -m "Migrate from Gemini to free open-source LLMs (Ollama/HuggingFace)"
   git push origin main
   ```

---

**Enjoy completely free, unlimited LLM queries for your recipe app!** 🎉

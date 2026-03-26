# Free Open-Source LLM Setup Guide

Replace Gemini API with **Ollama** (local, free) or **HuggingFace API** (cloud, free)

---

## ⚡ QUICK START (5 minutes)

### Option 1: Ollama (Recommended - Fastest, No API Key)

**Windows:**
1. Download: https://ollama.ai/download
2. Install and run Ollama application
3. Open PowerShell in project root:
   ```powersh
   cd c:\Users\limba\OneDrive\Desktop\Recipellm
   
   # Test Ollama is running
   curl http://localhost:11434/api/tags
   # Should see: {"models":[...]}
   
   # Start backend
   .\venv\Scripts\python.exe app.py
   
   # Start frontend (in another terminal)
   pnpm run dev --host
   ```

That's it! Backend now uses Mistral 7B via Ollama.

---

### Option 2: HuggingFace (No local setup, requires free API key)

1. Get free API key: https://huggingface.co/settings/tokens
2. Update `.env`:
   ```env
   # Comment out Ollama
   # OLLAMA_URL=http://localhost:11434
   
   # Uncomment HuggingFace
   HUGGINGFACE_API_KEY=hf_your_api_key_here
   HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.1
   ```
3. Start backend:
   ```bash
   python app.py
   ```

---

## 📖 DETAILED SETUP GUIDE

### Ollama Setup (Recommended)

**Why Ollama?**
- ✅ Completely free - no API key needed
- ✅ Runs locally - fast responses (GPU accelerated if available)
- ✅ Privacy - queries never leave your computer
- ✅ Offline mode - works without internet
- ✅ Best for development and testing

#### Step 1: Download & Install

Download from: https://ollama.ai/download

**Windows:**
- Download `.exe` installer
- Run installer
- Ollama will start automatically

**Mac:**
- Download `.dmg` file
- Drag to Applications folder
- Launch from Applications

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

#### Step 2: Download a Model

Open terminal/PowerShell and run:

```bash
# Download Mistral 7B (recommended - best balance)
ollama pull mistral

# Or alternative models:
ollama pull neural-chat    # Optimized for instructions/chat
ollama pull llama2          # Meta's Llama 2
ollama pull orca-mini       # Smaller, faster
```

**Typical download size:** 4-5 GB (one-time)

#### Step 3: Keep Ollama Running

Ollama needs to run in background. Choose one:

**Option A: Keep GUI running**
- Ollama is running if icon appears in system tray
- Pin to taskbar for quick access

**Option B: Run as service**
```bash
# Windows - run in PowerShell as Admin
ollama serve
# This starts the API server on http://localhost:11434
```

**Option C: Check if running**
```bash
# Should return model list
curl http://localhost:11434/api/tags
```

#### Step 4: Configure Project

Update `.env` (should already be set):
```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

#### Step 5: Test Connection

```bash
cd c:\Users\limba\OneDrive\Desktop\Recipellm

# Test with curl
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"mistral","prompt":"What is 2+2?","stream":false}'

# Should return: {"response":"2 + 2 = 4..."}
```

---

### HuggingFace Setup (Alternative)

**Why HuggingFace?**
- ✅ Cloud-based - no local setup needed
- ✅ Free tier available
- ✅ Works on any machine (even without GPU)
- ⚠️ Requires API key
- ⚠️ Need internet connection

#### Step 1: Create Free Account

1. Go to: https://huggingface.co/signup
2. Sign up with email/GitHub
3. Verify email

#### Step 2: Generate API Key

1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "recipellm"
4. Role: "read"
5. Click "Generate"
6. Copy the token

#### Step 3: Add to .env

```env
# Comment out Ollama
# LLM_PROVIDER=ollama
# OLLAMA_URL=...

# Enable HuggingFace
LLM_PROVIDER=huggingface
HUGGINGFACE_API_KEY=hf_yourcopyedtokenhere
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.1
```

#### Step 4: Test Connection

```bash
cd c:\Users\limba\OneDrive\Desktop\Recipellm

# Install/update dependencies
pip install -r requirements.txt

# Test - run Python interactively
python
>>> from llm_wrapper_opensource import HuggingFaceLLM
>>> llm = HuggingFaceLLM()
>>> print(llm.ask_ai("What is MongoDB?"))
# Should return response from Mistral model
```

#### Step 5: Check Free Tier Limits

Free tier on HuggingFace:
- **Requests per minute:** 3
- **Tokens per minute:** 1000
- **Max request size:** 1MB

For higher limits, upgrade to Inference Endpoints (paid, starting $0.06/hour)

---

## 🧪 Testing the Integration

### Test 1: Backend Health Check

```bash
curl http://localhost:5001/health
# Expected: {"status": "up"}
```

### Test 2: Chat with MongoDB

```bash
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"Show me chicken recipes","mode":"mongo"}'

# Should return: MongoDB query result with recipes
```

### Test 3: Chat with SQL

```bash
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"Show me recipes with pasta","mode":"sql"}'

# Should return: SQL query result
```

### Test 4: Frontend

Open: http://localhost:5173

Type: "Show me healthy recipes"

Should work immediately without quota errors!

---

## 🔄 Troubleshooting

### Ollama Not Running

```
Error: Cannot connect to Ollama at http://localhost:11434
```

**Fix:**
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. If not, start it: `ollama serve`
3. If it crashes, check logs in Ollama app

### Model Not Downloaded

```
Error: model "mistral" not found
```

**Fix:**
```bash
ollama pull mistral
# Wait for download to complete
```

### HuggingFace Rate Limited

```
Error: 429 - Too many requests
```

**Fix:**
- Free tier: 3 requests/minute
- Wait and retry
- Or upgrade to paid tier for higher limits

### API Response Timeout

```
Error: Timeout error
```

**Fix - for Ollama:**
- Your computer might be too slow
- Try shorter prompts
- Consider using HuggingFace (cloud)

**Fix - for HuggingFace:**
- May need to wake up model (first request slow)
- Try again in a few seconds

### Memory Issues with Ollama

If getting OOM (out of memory) errors:
1. Try smaller model: `ollama pull orca-mini` (3.5GB)
2. Or use HuggingFace instead (no local memory needed)

---

## ⚙️ Advanced Configuration

### Use Different Ollama Models

Edit `.env`:
```env
# Smaller, faster
OLLAMA_MODEL=orca-mini

# Larger, better quality  
OLLAMA_MODEL=neural-chat

# Meta's model
OLLAMA_MODEL=llama2
```

Then restart backend.

### Use Different HuggingFace Models

Edit `.env`:
```env
# Code expert
HUGGINGFACE_MODEL=codellama/CodeLlama-7b-Instruct-hf

# Smaller, faster
HUGGINGFACE_MODEL=HuggingFaceH4/zephyr-7b-beta

# Chinese expert
HUGGINGFACE_MODEL=baichuan-inc/Baichuan2-7B-Chat
```

### Custom Ollama Server Address

If Ollama runs on different machine:
```env
OLLAMA_URL=http://192.168.1.100:11434
```

### Enable Debug Logging

```bash
# Set env var before running
$env:DEBUG=true
python app.py
```

---

## 📊 Performance Comparison

| Feature | Ollama | HuggingFace |
|---------|--------|-------------|
| Setup time | 10 minutes | 2 minutes |
| Cost | Free | Free tier |
| Speed | Very fast (local) | Fast (cloud) |
| Offline mode | ✅ Yes | ❌ No |
| GPU acceleration | ✅ Yes (if GPU) | ✅ Always |
| First response time | Instant | 5-10 sec (warm up) |
| Rate limits | None | 3 req/min free |
| Privacy | ✅ All local | ❌ Sent to H.F. |

---

## 🎯 Recommendation

**For Development:** Use **Ollama**
- No limits, fastest responses
- Works offline
- No API keys to manage

**For Production:** Use **HuggingFace** (paid tier)
- Scalable in cloud
- No local resources needed
- Better uptime guarantees

**For Testing:** Start with **Ollama**, switch to **HuggingFace** if issues

---

## 📞 Support

**Ollama not found?** Download from https://ollama.ai

**HuggingFace API key?** Get it at https://huggingface.co/settings/tokens

**Model too slow?** Try `ollama pull orca-mini` for faster model

**Need help?** Check backend logs: `python app.py` shows real-time errors

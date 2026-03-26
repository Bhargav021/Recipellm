# RecipeLLM - AI Recipe & Nutrition Assistant

An interactive AI-powered chatbot that lets you query recipe and nutrition data using natural language, with support for MongoDB and PostgreSQL backends.

## Canonical Project Root

Use only this folder as the project root:

`Recipellm/`

Do not run the app from nested copies or parent directories. Run every command from this root.

## 🛠️ Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.9+**
- **Node.js (v18+)**
- **pnpm** (`npm install -g pnpm`)
- **MongoDB** and **PostgreSQL** running locally
- **Git** for version control

## 📁 Project Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Recipellm
```

### 2. Setup LLM (Choose One Option)

This project now uses **free, open-source LLMs** instead of Gemini API:

**Option A: Ollama** (Recommended - Local, No API Key)
- Download from https://ollama.ai
- Run: `ollama pull mistral && ollama serve`
- `OLLAMA_URL=http://localhost:11434` (already set in .env)

**Option B: HuggingFace API** (Cloud, Requires Free API Key)
- Get key at https://huggingface.co/settings/tokens
- Uncomment in `.env`: `HUGGINGFACE_API_KEY=your_key`

See [SETUP_OPENSOURCE_LLM.md](SETUP_OPENSOURCE_LLM.md) for detailed instructions.

### 3. Create/Update `.env` File

The `.env` file is pre-configured for Ollama. For HuggingFace, update:

```env
# Ollama (default - recommended)
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=recipe_chatbot
DB_USER=postgres
DB_PASSWORD=admin123
DB_HOST=localhost
DB_PORT=5432
```

For HuggingFace setup, see [SETUP_OPENSOURCE_LLM.md](SETUP_OPENSOURCE_LLM.md).
> ⚠️ **Do not commit `.env` to GitHub** — it's listed in `.gitignore`.

## ⚙️ Backend Setup (Flask + Mongo + PostgreSQL)

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize PostgreSQL Database and Tables

This project includes an idempotent initializer:

```bash
python scripts/init_postgres.py
```

This creates the target database from `.env` (default `recipe_chatbot`) and required tables if missing.

### 5. Run the Flask Backend

```bash
python app.py
```

> The backend server will be available at: `http://localhost:5001`

## 🌐 Frontend Setup (React + TailwindCSS)

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Start Development Server

```bash
pnpm run dev
```

> The frontend will run at: `http://localhost:5173`

## 🍲 Import Sample Data to MongoDB (Optional)

If you have CSV data and `import_csv_to_mongodb.py`:

```bash
python import_csv_to_mongodb.py
```

Note: this script expects `sample_food_com_recipes.csv` to exist in the project root.

## ✅ Run Order (Recommended)

1. Start MongoDB service (`mongod` must be reachable at `localhost:27017`).
2. Ensure PostgreSQL service is running.
3. Run `python scripts/init_postgres.py`.
4. Start backend: `python app.py`.
5. Start frontend: `pnpm run dev`.

## 🧪 Testing the Application

1. Ensure **MongoDB**, **PostgreSQL**, and both servers (frontend + backend) are running.
2. Visit: `http://localhost:5173`
3. Try example queries like:
   - “Show me recipes with chicken”
   - “What’s the nutritional value of spinach?”
   - “Insert a new food price entry”

## 🧱 Architecture Overview

- **Frontend**: React + TypeScript + TailwindCSS
- **Backend**: Flask API (Python)
- **Databases**: MongoDB and PostgreSQL
- **LLM**: Google Generative AI via `google-generativeai`

## 📦 File Structure

### Backend

| File | Description |
|------|-------------|
| `app.py` | Flask backend entrypoint |
| `Mongodb/agent3.py` | MongoDB LLM agent |
| `SQL/agent3_sql_final.py` | PostgreSQL LLM agent |
| `mongo_utils.py`, `db_utils.py` | Database connection helpers |
| `llm_wrapper.py` | Google GenAI integration |
| `log_utils.py`, `utils.py` | Logging and shared logic |
| `requirements.txt` | Python dependencies |
| `.env` | API keys and DB settings |
| `scripts/init_postgres.py` | Creates DB and required SQL tables |

### Frontend (in `src/`)

- `App.tsx`, `main.tsx` – React app entrypoints
- `components/Chat.tsx`, `ChatMessage.tsx`, `ChatHistory.tsx` – Chat interface
- `services/api.ts` – API handler for sending queries to backend

## ✅ Version Control Tips

```bash
git add .
git commit -m "🔧 Set up .env, updated backend and frontend configs"
git push origin main
```

> Ensure `.env`, `venv/`, `__pycache__/`, and `.DS_Store` are ignored via `.gitignore`.

## 🧹 Troubleshooting

### Common Issues

| Issue | Fix |
|-------|-----|
| MongoDB not responding | Run `mongod` in terminal or start MongoDB service |
| PostgreSQL database missing | Run `python scripts/init_postgres.py` |
| PostgreSQL auth errors | Check `DB_USER`/`DB_PASSWORD` in `.env` |
| LLM key error | Verify `LLM_API_KEY` is set and not expired |
| React errors | Try `pnpm install` again and restart `pnpm run dev` |

### ⚠️ Gemini API Quota Exceeded (429 Error)

This occurs when the free tier quota limit is hit. The free tier has strict rate limits:
- **0 requests per minute** (free tier limit)
- **15,000 requests per day per project** (free tier limit)  
- **1 million input tokens per month** (free tier limit)

**Solutions:**

#### Option 1: Upgrade to Paid Plan (Recommended)
1. Go to [Google AI Studio](https://ai.google.dev/)
2. Click on your project
3. Go to "Billing" and upgrade to a paid plan
4. You'll get higher quotas immediately
5. The app will work as expected with paid tier rates

#### Option 2: Use Multiple API Keys / Google Accounts
If you have access to other Google Cloud accounts:
1. Create a new API key on a different account
2. Update `.env` with the new `LLM_API_KEY`
3. Restart the backend (`python app.py`)

#### Option 3: Wait for Quota Reset
- Free tier quotas reset daily at UTC midnight
- Check remaining quota at [AI Studio Monitoring](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com)

#### Option 4: Use Local LLM Alternative (Advanced)
Replace Google Generative AI with a local model like:
- **Ollama** (https://ollama.ai) - Download and run models locally
- **LM Studio** (https://lmstudio.ai) - Local inference server

To use Ollama:
1. Install Ollama and download a model: `ollama pull mistral` or `ollama pull neural-chat`
2. Update `Mongodb/llm_wrapper.py` and `SQL/llm_wrapper.py` to use Ollama API
3. Restart the backend

#### Option 5: Fallback Mode (Available)
The project includes a fallback mechanism (`llm_fallback.py`) that provides:
- Cached template-based responses for common queries
- Direct MongoDB/SQL queries without LLM translation
- Allows basic functionality when quota is exhausted

To enable fallback mode, modify `/ask` endpoint in `app.py` to catch quota errors and use fallback responses.

### MongoDB Version

Current MongoDB connection: **localhost:27017**

To check your installed MongoDB version:
```bash
mongosh --version   # For mongosh CLI
# or check MongoDB Compass: Help > About MongoDB
```

## 📄 License

MIT

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
cd recipellm-demo
```

### 2. Create a `.env` File

Create a `.env` file in the root directory with the following content:

```env
LLM_API_KEY=your-google-genai-api-key
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=recipe_chatbot
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432
```

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

### 3. Initialize PostgreSQL Database and Tables

This project includes an idempotent initializer:

```bash
python scripts/init_postgres.py
```

This creates the target database from `.env` (default `recipe_chatbot`) and required tables if missing.

### 4. Run the Flask Backend

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

| Issue | Fix |
|-------|-----|
| MongoDB not responding | Run `mongod` in terminal |
| PostgreSQL database missing | Run `python scripts/init_postgres.py` |
| PostgreSQL auth errors | Check `DB_USER`/`DB_PASSWORD` in `.env` |
| LLM key error | Verify `LLM_API_KEY` is set and not expired |
| Gemini quota errors (429) | Check API quota/billing at ai.google.dev and retry after cooldown |
| React errors | Try `pnpm install` again and restart `pnpm run dev` |

## 📄 License

MIT

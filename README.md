# AI-Powered Resume Intelligence & Ranking System (PageIndex + Agentic RAG)

An enterprise-grade, structure-aware recruitment intelligence system that replaces naive flat-vector chunking RAG with **PageIndex-style hierarchical vectorless retrieval** and **multi-step Agentic RAG reasoning** for grounded candidate screening, scoring, comparison, and ranking.

---

## Key Features

1. **PageIndex Vectorless Retrieval**:
   - Parses PDF, DOCX, and text resumes into hierarchical, reasoning-friendly trees (`DocumentNode` $\rightarrow$ `SectionNode` $\rightarrow$ `EntryNode` $\rightarrow$ `SubEntryNode`).
   - LLM navigates semantic summaries rather than searching flat embedding spaces, preventing confusion between claimed skills and verified work experience.
2. **Grounded 4D Scoring Rubric**:
   - **Core Technical Skills (30%)**
   - **Domain & Role Depth (35%)**
   - **Project & System Impact (20%)**
   - **Education & Baseline Fit (15%)**
   - Every point and deduction is strictly grounded in exact page numbers and character offsets.
3. **Agentic RAG Multi-Hop Reasoning**:
   - Cross-candidate comparison and ranking.
   - Deconstructs queries into traversal plans with visible reasoning steps.
4. **Modern Interactive Dashboard**:
   - **Ranked Leaderboard**: 1-click batch evaluation with radar & bar comparisons.
   - **PageIndex Tree Visualizer**: Expandable node tree with entity tags and citation anchors.
   - **Grounded Scorecard Modal**: Deep-dive into candidates with verified resume excerpts.
   - **Recruiter AI Chat**: Natural-language Q&A with live reasoning traces.
5. **Flexible Multi-Provider Gateway**:
   - Built-in **Local Structure-Aware Heuristic Engine** (runs immediately out-of-the-box with no API key needed).
   - Live integration with **Google Gemini, OpenAI, Anthropic Claude, and Groq**.

---

## Quick Start

### 1. Launch the Application
Run the startup script:
```bash
./start.sh
```
Or start manually:
- Backend: `./venv/bin/python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000`
- Frontend: `cd frontend && npm run dev`

Visit: **`http://localhost:5173`**

### 2. Run Backend Automated Tests
```bash
./venv/bin/pytest backend/tests/test_backend.py -v
```

---

## 🚀 Deploying to Vercel

This project is ready for 1-click deployment on [Vercel](https://vercel.com) supporting both the React frontend and the Python Serverless API.

### Deploy Steps:
1. Push your repository to GitHub.
2. In your [Vercel Dashboard](https://vercel.com/new), click **Import Project** and select `Chetan11223/AI-recruitment-assistance`.
3. Vercel will automatically detect `vercel.json`:
   - **Framework Preset**: Vite / Other
   - **Build Command**: `cd frontend && npm install --legacy-peer-deps && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Serverless API**: `api/index.py` handles all `/api/*` routes.
4. Click **Deploy**.

---

## 🐳 Deploying with Docker

You can build and run the entire full-stack application as a single Docker container anywhere (Render, AWS, GCP, Fly.io, Railway, DigitalOcean):

```bash
# 1. Build Docker Image
docker build -t resume-intelligence:latest .

# 2. Run Container
docker run -p 8000:8000 -e LLM_PROVIDER=mock resume-intelligence:latest
```

Visit: `http://localhost:8000`

---

## 🚀 Deploying to Render

This project is configured for seamless deployment on [Render](https://render.com).

### Method 1: Render Blueprint (Recommended)
1. In your Render Dashboard, click **New +** $\rightarrow$ **Blueprint**.
2. Connect your GitHub repository `https://github.com/Chetan11223/AI-recruitment-assistance`.
3. Render will automatically detect `render.yaml` and configure both the backend web service and the frontend static site.
4. Click **Apply**.

### Method 2: Docker Web Service on Render
1. Click **New +** $\rightarrow$ **Web Service**.
2. Select your repository.
3. Choose **Docker** as the environment (it will use the multi-stage `Dockerfile`).
4. Click **Create Web Service**.

---

## Architecture

```
resume/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & lifespan
│   │   ├── config.py                # App configuration & LLM settings
│   │   ├── index/
│   │   │   ├── schema.py            # Pydantic schemas (PageIndexNode, CitationSpan, Scorecard)
│   │   │   └── store.py             # Disk & in-memory candidate / JD store
│   │   ├── parser/
│   │   │   ├── document_loader.py   # PDF (PyMuPDF), DOCX, TXT loader with offset tracking
│   │   │   ├── segmenter.py         # Semantic section boundary detector
│   │   │   └── tree_builder.py      # Hierarchical PageIndex tree builder
│   │   ├── scorer/
│   │   │   └── rubric_engine.py     # 4-dimensional grounded rubric scoring
│   │   ├── agent/
│   │   │   ├── tools.py             # PageIndex tree navigation & lookup tools
│   │   │   └── orchestrator.py      # Agentic RAG multi-step query & ranking engine
│   │   ├── llm/
│   │   │   └── client.py            # Multi-provider LLM gateway (Gemini, OpenAI, Anthropic, Groq, Local)
│   │   ├── api/
│   │   │   ├── routes_resumes.py    # Resume upload & management
│   │   │   ├── routes_jobs.py       # Job description creation & management
│   │   │   ├── routes_agent.py      # Chat, ranking, and scorecard endpoints
│   │   │   └── routes_settings.py   # Live provider configuration
│   │   └── sample_data/
│   │       └── generator.py         # Pre-loaded realistic tech resumes and JDs
│   ├── tests/
│   │   └── test_backend.py          # Pytest suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx           # Top navigation & provider status
│   │   │   ├── Leaderboard.jsx      # Ranked leaderboard & comparative charts
│   │   │   ├── PageIndexTreeVisualizer.jsx # Interactive hierarchical tree explorer
│   │   │   ├── ScorecardModal.jsx   # 4D rubric modal with verified citations
│   │   │   ├── RecruiterChat.jsx    # Conversational agent with reasoning trace
│   │   │   ├── ManageData.jsx       # Resume uploader & JD manager
│   │   │   └── SettingsModal.jsx    # Live LLM provider & API key settings
│   │   ├── api/
│   │   │   └── client.js            # Axios client
│   │   ├── App.jsx                  # Main application orchestrator
│   │   └── index.css                # Dark theme & styling
│   └── package.json
└── start.sh
```

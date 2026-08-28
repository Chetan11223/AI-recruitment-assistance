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

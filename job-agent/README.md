# Job Application Intelligence Agent — Scaffold

## Setup

### Backend
```
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY=your_key
export TAVILY_API_KEY=your_key
mkdir -p exports uploads
uvicorn api.main:app --reload
```

### Frontend
```
cd frontend
npm create vite@latest . -- --template react-ts   # if not already scaffolded
npm install
npm run dev
```

## What's stubbed vs. what needs work
- All nodes have working logic (not just stubs) but are untested against real Groq
  API responses — expect to iterate on the JSON-schema prompts once you see real output.
- `draft_generation_node`'s no-fabrication guard is a prompt-level control, not a
  hard constraint. Consider adding a validation pass that diffs draft bullets against
  the original resume text before showing them to the user.
- No auth, no multi-user support — this is scoped as a personal tool per the original ask.
- Frontend has no styling and no loading/error states yet — functional skeleton only.

## Build order (from the architecture doc)
1. `ingest_and_parse_node` — test on your own real resume + a few JDs first
2. `fit_score_node` + `gap_analysis_node`
3. `company_research_node` (needs TAVILY_API_KEY)
4. `interview_prep_node` + `draft_generation_node` — scrutinize hardest for fabrication
5. Full graph + approval gate + FastAPI/React wiring (already connected above — test end to end)

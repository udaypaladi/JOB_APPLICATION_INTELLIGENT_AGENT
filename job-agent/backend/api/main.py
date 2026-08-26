"""
Three endpoints is all the frontend needs:
  POST /sessions            -> start a run (uploads resume + JD, streams progress)
  GET  /sessions/{id}       -> poll current state (useful on reconnect)
  POST /sessions/{id}/decide -> resume after the approval interrupt
"""
import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command

from graph.workflow import compiled_graph

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server default
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/sessions")
async def start_session(resume: UploadFile, jd_text: str = Form(...)):
    session_id = str(uuid.uuid4())
    resume_path = os.path.join(UPLOAD_DIR, f"{session_id}_{resume.filename}")
    with open(resume_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    config = {"configurable": {"thread_id": session_id}}
    initial_state = {
        "session_id": session_id,
        "resume_file_path": resume_path,
        "jd_text": jd_text,
        "errors": [],
    }

    # runs until it hits the approval interrupt() and stops there
    result = compiled_graph.invoke(initial_state, config=config)
    return {"session_id": session_id, "state": result}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    snapshot = compiled_graph.get_state(config)
    return {"state": snapshot.values, "next": snapshot.next}


@app.post("/sessions/{session_id}/decide")
async def decide(session_id: str, status: str = Form(...), edits: str = Form(None)):
    """
    status: "approved" | "edited" | "rejected"
    edits: optional JSON string of {drafts field: new value} when status == "edited"
    """
    import json
    config = {"configurable": {"thread_id": session_id}}
    decision = {"status": status, "edits": json.loads(edits) if edits else None}

    result = compiled_graph.invoke(Command(resume=decision), config=config)
    return {"session_id": session_id, "state": result}

"""
The approval gate is the whole point of your original spec: "auto-fill,
then pause for review, never auto-submit." interrupt() is what makes the
pause real — execution stops here until resumed with a Command(resume=...)
call from the API layer, triggered by the user clicking approve/edit in React.
"""
from langgraph.types import interrupt
from graph.state import ApplicationState
from tools.export import export_resume_docx, export_cover_letter_docx


def approval_gate_node(state: ApplicationState) -> dict:
    decision = interrupt({
        "drafts": state["drafts"],
        "fit_score": state["fit_score"],
        "gap_analysis": state["gap_analysis"],
        "message": "Review the tailored resume, cover letter, and interview prep. "
                   "Approve, edit, or reject before export.",
    })
    # `decision` is whatever the frontend sends back via Command(resume=decision)
    # expected shape: {"status": "approved" | "edited" | "rejected", "edits": {...}}
    drafts = dict(state["drafts"])
    if decision.get("status") == "edited" and decision.get("edits"):
        drafts.update(decision["edits"])

    return {"drafts": drafts, "approval_status": decision.get("status")}


def export_node(state: ApplicationState) -> dict:
    if state.get("approval_status") != "approved" and state.get("approval_status") != "edited":
        return {"errors": state.get("errors", []) + ["Export blocked: not approved"]}

    session_id = state["session_id"]
    resume_path = f"./exports/{session_id}_resume.docx"
    cover_letter_path = f"./exports/{session_id}_cover_letter.docx"

    export_resume_docx(
        state["parsed_resume"]["name"],
        state["drafts"]["tailored_resume_bullets"],
        resume_path,
    )
    export_cover_letter_docx(state["drafts"]["cover_letter"], cover_letter_path)

    return {"exported_files": [resume_path, cover_letter_path]}

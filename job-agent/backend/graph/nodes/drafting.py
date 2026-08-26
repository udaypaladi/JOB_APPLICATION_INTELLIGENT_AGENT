"""
Build order step 4: highest hallucination risk in the whole pipeline.
The system prompt below is intentionally blunt about not fabricating
experience — test this node the hardest before trusting its output.
"""
import json
from groq import Groq
from graph.state import ApplicationState

client = Groq()
MODEL = "openai/gpt-oss-120b"

NO_FABRICATION_SYSTEM_PROMPT = """You are a resume/cover-letter assistant. You must NEVER invent
skills, employers, dates, metrics, or accomplishments that are not present in the candidate's
original resume text. You may only REWORD, REORDER, and RE-EMPHASIZE existing content to better
match the job description's language. If a requirement genuinely isn't covered by the resume,
leave it out rather than fabricating coverage."""

INTERVIEW_PREP_PROMPT = """Based on this job description and company research, generate 8 likely
interview questions (mix of behavioral and technical/role-specific). Return ONLY valid JSON:
{"questions": [{"question": string, "category": "behavioral" | "technical", "why_asked": string}]}

Role: {role}
Responsibilities: {responsibilities}
Company culture notes: {culture}
Known gaps in candidate profile: {gaps}
"""

DRAFT_PROMPT = """Using ONLY the candidate's existing resume content below, produce:
1. tailored_resume_bullets: existing bullets reworded/reordered per section to better match the JD
   (do not add anything not already present)
2. cover_letter: a 3-paragraph cover letter grounded only in real resume content and the JD

Return ONLY valid JSON: {"tailored_resume_bullets": {<section>: [string]}, "cover_letter": string}

Candidate resume (source of truth — do not go beyond this): {resume}
Job description: {jd}
Gap analysis (for what to naturally emphasize instead of gaps): {gaps}
"""


def interview_prep_node(state: ApplicationState) -> dict:
    jd = state["parsed_jd"]
    research = state.get("company_research") or {}
    gaps = state.get("gap_analysis") or {}

    prompt = (INTERVIEW_PREP_PROMPT
              .replace("{role}", jd["role_title"])
              .replace("{responsibilities}", json.dumps(jd["responsibilities"]))
              .replace("{culture}", json.dumps(research.get("culture_notes", [])))
              .replace("{gaps}", json.dumps(gaps.get("missing_skills", []))))

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content)

    drafts = dict(state.get("drafts") or {})
    drafts["interview_questions"] = result["questions"]
    return {"drafts": drafts}


def draft_generation_node(state: ApplicationState) -> dict:
    prompt = (DRAFT_PROMPT
              .replace("{resume}", json.dumps(state["parsed_resume"]))
              .replace("{jd}", json.dumps(state["parsed_jd"]))
              .replace("{gaps}", json.dumps(state.get("gap_analysis") or {})))

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": NO_FABRICATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    result = json.loads(resp.choices[0].message.content)

    drafts = dict(state.get("drafts") or {})
    drafts["tailored_resume_bullets"] = result["tailored_resume_bullets"]
    drafts["cover_letter"] = result["cover_letter"]
    return {"drafts": drafts, "approval_status": "pending"}

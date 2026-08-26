"""
Build order step 2: these only depend on parsed_resume/parsed_jd, so they
can be built and tested before company research or drafting exist.
"""
import json
from groq import Groq
from graph.state import ApplicationState

client = Groq()
MODEL = "openai/gpt-oss-120b"

FIT_SCORE_PROMPT = """Compare this candidate's resume against the job requirements.
Return ONLY valid JSON matching this schema:
{
  "overall_score": number (0-100),
  "skill_match_score": number (0-100),
  "breakdown": {"<requirement>": "match" | "partial" | "missing", ...},
  "explanation": string (2-3 sentences, be honest, not encouraging for its own sake)
}

Candidate skills: {skills}
Candidate experience: {experience}

Required skills: {required}
Preferred skills: {preferred}
Responsibilities: {responsibilities}
"""

GAP_ANALYSIS_PROMPT = """Given this fit score breakdown, identify:
1. missing_skills: skills genuinely absent from the candidate's background (don't invent partial credit)
2. reframe_suggestions: existing experience that could be repositioned to better match the JD language,
   WITHOUT fabricating anything not already in the resume

Return ONLY valid JSON: {"missing_skills": [string], "reframe_suggestions": [string]}

Fit breakdown: {breakdown}
Candidate experience: {experience}
"""


def fit_score_node(state: ApplicationState) -> dict:
    resume = state["parsed_resume"]
    jd = state["parsed_jd"]

    prompt = (FIT_SCORE_PROMPT
              .replace("{skills}", json.dumps(resume["skills"]))
              .replace("{experience}", json.dumps(resume["experience"]))
              .replace("{required}", json.dumps(jd["required_skills"]))
              .replace("{preferred}", json.dumps(jd["preferred_skills"]))
              .replace("{responsibilities}", json.dumps(jd["responsibilities"])))

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    fit_score = json.loads(resp.choices[0].message.content)
    return {"fit_score": fit_score}


def gap_analysis_node(state: ApplicationState) -> dict:
    prompt = (GAP_ANALYSIS_PROMPT
              .replace("{breakdown}", json.dumps(state["fit_score"]["breakdown"]))
              .replace("{experience}", json.dumps(state["parsed_resume"]["experience"])))

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    gap_analysis = json.loads(resp.choices[0].message.content)
    return {"gap_analysis": gap_analysis}

"""
Shared state object that flows through every node in the graph.
Keep this the single source of truth for what each node reads/writes —
it's also what gets persisted by the LangGraph checkpointer, so a user
can close the tab mid-flow and resume later.
"""
from typing import TypedDict, Optional, List, Dict, Any


class ParsedResume(TypedDict):
    raw_text: str
    name: str
    skills: List[str]
    experience: List[Dict[str, Any]]  # [{title, company, dates, bullets}]
    education: List[Dict[str, Any]]


class ParsedJD(TypedDict):
    raw_text: str
    company: str
    role_title: str
    required_skills: List[str]
    preferred_skills: List[str]
    responsibilities: List[str]


class CompanyResearch(TypedDict):
    summary: str
    recent_news: List[str]
    tech_stack: List[str]
    culture_notes: List[str]
    sources: List[str]


class FitScore(TypedDict):
    overall_score: float  # 0-100
    skill_match_score: float
    breakdown: Dict[str, str]  # requirement -> "match"/"partial"/"missing"
    explanation: str


class GapAnalysis(TypedDict):
    missing_skills: List[str]
    reframe_suggestions: List[str]  # existing experience that can be repositioned


class Drafts(TypedDict):
    tailored_resume_bullets: Dict[str, List[str]]  # section -> bullets
    cover_letter: str
    interview_questions: List[Dict[str, str]]  # [{question, category, why_asked}]


class ApplicationState(TypedDict, total=False):
    session_id: str

    # inputs
    resume_file_path: str
    jd_text: str

    # pipeline outputs, filled in as nodes run
    parsed_resume: Optional[ParsedResume]
    parsed_jd: Optional[ParsedJD]
    company_research: Optional[CompanyResearch]
    fit_score: Optional[FitScore]
    gap_analysis: Optional[GapAnalysis]
    drafts: Optional[Drafts]

    # human-in-the-loop
    approval_status: Optional[str]  # "pending" | "approved" | "rejected" | "edited"
    user_edits: Optional[Dict[str, Any]]

    # error tracking
    errors: List[str]

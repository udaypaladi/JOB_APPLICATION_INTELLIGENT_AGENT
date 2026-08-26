"""
Extracts raw text from uploaded files, then uses Groq (Llama model) with a
strict JSON-schema prompt to turn that text into structured data.
"""
import json
import pdfplumber
from docx import Document as DocxDocument
from groq import Groq

client = Groq()  # reads GROQ_API_KEY from env
MODEL = "openai/gpt-oss-120b"


def extract_text_from_file(path: str) -> str:
    if path.lower().endswith(".pdf"):
        text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    elif path.lower().endswith(".docx"):
        doc = DocxDocument(path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


RESUME_SCHEMA_PROMPT = """You are a strict JSON extraction engine. Extract structured fields
from the resume text below. Return ONLY valid JSON, no markdown fences, no commentary.

Schema:
{
  "name": string,
  "skills": [string],
  "experience": [{"title": string, "company": string, "dates": string, "bullets": [string]}],
  "education": [{"degree": string, "institution": string, "dates": string}]
}

Resume text:
---
{text}
---
"""

JD_SCHEMA_PROMPT = """You are a strict JSON extraction engine. Extract structured fields
from the job description below. Return ONLY valid JSON, no markdown fences, no commentary.

Schema:
{
  "company": string,
  "role_title": string,
  "required_skills": [string],
  "preferred_skills": [string],
  "responsibilities": [string]
}

Job description text:
---
{text}
---
"""


def _call_groq_json(prompt: str) -> dict:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


def parse_resume(raw_text: str) -> dict:
    data = _call_groq_json(RESUME_SCHEMA_PROMPT.replace("{text}", raw_text))
    data["raw_text"] = raw_text
    return data


def parse_jd(raw_text: str) -> dict:
    data = _call_groq_json(JD_SCHEMA_PROMPT.replace("{text}", raw_text))
    data["raw_text"] = raw_text
    return data

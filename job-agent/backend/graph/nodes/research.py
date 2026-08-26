"""
Build order step 3: add this once fit scoring works standalone.
"""
import json
from groq import Groq
from graph.state import ApplicationState
from tools.search import search_company
from vectorstore.chroma_client import index_research_chunks, query_research

client = Groq()
MODEL = "openai/gpt-oss-120b"

SYNTHESIZE_PROMPT = """Summarize what's relevant to a job applicant from these research
snippets about {company}. Return ONLY valid JSON:
{
  "summary": string,
  "recent_news": [string],
  "tech_stack": [string],
  "culture_notes": [string]
}

Snippets:
{snippets}
"""


def company_research_node(state: ApplicationState) -> dict:
    company = state["parsed_jd"]["company"]
    session_id = state["session_id"]

    raw_chunks = search_company(company)
    index_research_chunks(session_id, raw_chunks)

    relevant = query_research(session_id, f"{company} news culture tech stack funding", n_results=8)

    prompt = (SYNTHESIZE_PROMPT
              .replace("{company}", company)
              .replace("{snippets}", "\n---\n".join(relevant)))

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    parsed = json.loads(resp.choices[0].message.content)
    parsed["sources"] = list({c["url"] for c in raw_chunks if c["url"]})

    return {"company_research": parsed}

from graph.state import ApplicationState
from tools.parsing import extract_text_from_file, parse_resume, parse_jd


def ingest_and_parse_node(state: ApplicationState) -> dict:
    """
    Single node covering ingest + parse (build order step 1 from the
    architecture doc — get this solid on its own before anything downstream).
    """
    errors = []

    try:
        resume_text = extract_text_from_file(state["resume_file_path"])
        parsed_resume = parse_resume(resume_text)
    except Exception as e:
        errors.append(f"Resume parsing failed: {e}")
        parsed_resume = None

    try:
        parsed_jd = parse_jd(state["jd_text"])
    except Exception as e:
        errors.append(f"JD parsing failed: {e}")
        parsed_jd = None

    return {
        "parsed_resume": parsed_resume,
        "parsed_jd": parsed_jd,
        "errors": state.get("errors", []) + errors,
    }

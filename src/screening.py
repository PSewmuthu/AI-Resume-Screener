"""
screening.py
------------
Core "Generative AI" logic for the Resume Screening & Fit Summary
use case: given a job description and a resume, ask the LLM to
produce a structured fit assessment.
"""

from .llm_client import call_llm

SYSTEM_PROMPT = """You are an experienced technical recruiter assistant.
You will be given a JOB DESCRIPTION and a CANDIDATE RESUME.

Compare them carefully and respond with ONLY a valid JSON object
(no markdown, no commentary, no extra text) with exactly this shape:

{
  "fit_score": <integer 0-100>,
  "verdict": "<Strong Fit | Moderate Fit | Weak Fit>",
  "summary": "<2-3 sentence overview of how well the candidate matches>",
  "matching_skills": ["<skill or experience that matches the JD>", "..."],
  "gaps": ["<skill or requirement the candidate is missing or weak on>", "..."],
  "interview_questions": ["<a targeted interview question for this candidate>", "..."]
}

Guidelines:
- Base fit_score purely on how well the resume matches the job description's
  requirements (skills, experience level, domain).
- List 3-6 matching_skills and 2-4 gaps where possible.
- Write 3 interview_questions that probe the specific gaps or claims found
  in this resume, not generic questions.
- Be concise and specific. Do not invent information not present in the resume.
"""


def screen_resume(jd_text: str, resume_text: str, candidate_name: str, model: str = None) -> dict:
    """
    Screen a single resume against a job description using the LLM.

    Returns a dict with fit_score, verdict, summary, matching_skills,
    gaps, and interview_questions - plus the candidate_name for display.
    """

    user_prompt = f"""JOB DESCRIPTION:
{jd_text}

CANDIDATE RESUME ({candidate_name}):
{resume_text}
    """

    result = call_llm(SYSTEM_PROMPT, user_prompt, model=model)
    result["candidate_name"] = candidate_name
    return result


def screen_multiple(jd_text: str, resumes: dict, model: str = None) -> list:
    """
    Screen multiple resumes and return results sorted by fit_score (desc).

    Parameters
    ----------
    jd_text : str
        The job description text to screen against.
    resumes : dict
        Mapping of candidate_name -> resume_text
    model : str, optional
        The model to use for the LLM call.
    """
    results = []
    for name, text in resumes.items():
        try:
            results.append(screen_resume(jd_text, text, name, model=model))
        except Exception as e:
            results.append({
                "candidate_name": name,
                "fit_score": None,
                "verdict": "Error",
                "summary": f"Could not screen this resume: {str(e)}",
                "matching_skills": [],
                "gaps": [],
                "interview_questions": []
            })

    results.sort(key=lambda r: (
        r["fit_score"] is None, -(r["fit_score"] or 0)))
    return results

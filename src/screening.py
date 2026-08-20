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

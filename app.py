"""
app.py
------
Streamlit demo app for "AI Resume Screening & Fit Summary".

Business use case: Recruitment
A recruiter pastes a job description and adds a batch of resumes.
The app uses a free LLM (via the Groq API) to generate, for each
candidate:
  - a Fit Score (0-100)
  - a verdict (Strong / Moderate / Weak Fit)
  - a short summary of the match
  - matching skills and gaps
  - tailored interview questions

Run with:
    streamlit run app.py
"""

from src.resume_parser import parse_resume
from src.screening import screen_multiple
from pathlib import Path
import streamlit as st
import pandas as pd
import json

DATA_DIR = Path(__file__).parent / "data"
JD_DIR = DATA_DIR / "job_descriptions"
SAMPLE_RESUME_DIR = DATA_DIR / "sample_resumes"

st.set_page_config(page_title="AI Resume Screener",
                   page_icon="🧑‍💼", layout="wide")

st.title("🧑‍💼 AI Resume Screening & Fit Summary")
st.caption(
    "Recruitment use case · Paste a job description, add resumes, and get an "
    "AI-generated fit score, summary, and interview questions for each candidate."
)

with st.sidebar:
    st.header("About this demo")
    st.markdown(
        """
        This tool helps a recruiter quickly triage a batch of resumes
        against one job description.

        **How it works**
        1. A job description and a resume are sent to a free LLM (Groq).
        2. The model returns a structured fit assessment as JSON.
        3. Candidates are ranked so the strongest matches surface first.

        **Model:** set via `GROQ_MODEL` in `.env`
        (default: `openai/gpt-oss-120b`, Groq free tier)
        """
    )
    st.divider()
    st.markdown(
        "Need a free API key? Get one at "
        "[console.groq.com/keys](https://console.groq.com/keys) — "
        "no credit card required."
    )

# Job description input
st.subheader("Job description")

sample_jds = sorted(JD_DIR.glob("*.txt")) if JD_DIR.exists() else []
jd_choice = st.selectbox(
    "Load a sample job description (optional)",
    ["-- None, I'll paste my own --"] + [f.stem for f in sample_jds],
)

default_jd_text = ""
if jd_choice != "-- None, I'll paste my own --":
    default_jd_text = (JD_DIR / f"{jd_choice}.txt").read_text(encoding="utf-8")

jd_text = st.text_area("Job description text",
                       value=default_jd_text, height=220)

# Candidate resumes input
st.subheader("Candidate resumes")

use_samples = st.checkbox(
    "Use the 4 bundled sample resumes (for a quick demo)")

uploaded_files = None
if not use_samples:
    uploaded_files = st.file_uploader(
        "Upload resumes (.txt, .pdf, .docx) - you can select multiple files",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True,
    )

model_override = st.text_input(
    "Model override (optional)",
    value="",
    placeholder="e.g. openai/gpt-oss-20b (leave blank for default)",
)

run = st.button("🔍 Screen candidates", type="primary")

# Run screening
if run:
    if not jd_text.strip():
        st.error("Please provide a job description first.")
        st.stop()

    resumes = {}
    if use_samples:
        for path in sorted(SAMPLE_RESUME_DIR.glob("*.txt")):
            name = path.stem.replace("_", " ").title()
            resumes[name] = path.read_text(encoding="utf-8")
    else:
        if not uploaded_files:
            st.error(
                "Please upload at least one resume, or check 'use sample resumes'.")
            st.stop()
        for f in uploaded_files:
            text = parse_resume(f.name, f.getvalue())
            name = Path(f.name).stem.replace("_", " ").title()
            resumes[name] = text

    with st.spinner(f"Screening {len(resumes)} candidate(s) against the job description..."):
        try:
            results = screen_multiple(
                jd_text, resumes, model=model_override or None)
        except RuntimeError as e:
            st.error(str(e))
            st.stop()

    st.session_state["results"] = results

# Results display
if "results" in st.session_state:
    results = st.session_state["results"]

    st.subheader("Results")

    summary_rows = [
        {
            "Candidate": r["candidate_name"],
            "Fit Score": r["fit_score"],
            "Verdict": r["verdict"],
        }
        for r in results
    ]
    df = pd.DataFrame(summary_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download full results as JSON",
        data=json.dumps(results, indent=2),
        file_name="screening_results.json",
        mime="application/json",
    )

    st.divider()

    for r in results:
        score = r["fit_score"]
        badge = "🟢" if (score or 0) >= 75 else "🟡" if (
            score or 0) >= 50 else "🔴"
        label = f"{score}/100" if score is not None else "N/A"
        with st.expander(f"{badge} {r['candidate_name']} - {label} ({r['verdict']})"):
            st.markdown(f"**Summary:** {r['summary']}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Matching skills**")
                for s in r["matching_skills"]:
                    st.markdown(f"- {s}")
            with col2:
                st.markdown("**⚠️ Gaps**")
                for g in r["gaps"]:
                    st.markdown(f"- {g}")

            st.markdown("**❓ Suggested interview questions**")
            for q in r["interview_questions"]:
                st.markdown(f"- {q}")

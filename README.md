# AI Resume Screening & Fit Summary

A Generative AI application for the **Recruitment** business use case.
A recruiter pastes a job description, adds a batch of candidate resumes,
and the app uses a free LLM API to generate - for every candidate - a
fit score, a plain-language summary, matching skills, gaps, and
tailored interview questions.

Built entirely with **free tools**: Streamlit (UI), the Groq API free
tier (LLM), and open-source Python libraries for file parsing.

---

## 1. Business use case

Recruiters often have to skim dozens of resumes per job opening and
manually judge how well each one matches the requirements. This is
slow, inconsistent between reviewers, and easy to get wrong under time
pressure.

This app automates the first-pass screening step: for each resume, an
LLM compares it against the job description and returns a structured,
explainable assessment (not just a score) so a recruiter can quickly
decide who to shortlist and what to ask them in an interview.

## 2. How it works (architecture)

```
                    ┌────────────────────┐
  Job description   │                    │
  (pasted text)     │                    │
                    │   Streamlit UI     │
  Resume files ───▶│     (app.py)       │
  (.txt/.pdf/.docx) │                    │
                    └─────────┬──────────┘
                              │
                              ▼
                 ┌────────────────────┐
                 │  resume_parser.py  │  extracts plain text from
                 │                    │  .txt / .pdf / .docx files
                 └──────────┬─────────┘
                            │ resume text
                            ▼
                 ┌────────────────────┐
                 │   screening.py     │  builds the recruiter-style
                 │                    │  prompt for each candidate
                 └──────────┬─────────┘
                            │ system + user prompt
                            ▼
                 ┌────────────────────┐
                 │   llm_client.py    │  calls the Groq API (free
                 │                    │  tier) and parses JSON back
                 └──────────┬─────────┘
                            │ fit_score, verdict, summary,
                            │ matching_skills, gaps, questions
                            ▼
                 ┌────────────────────┐
                 │  Results table +   │  ranked by fit_score,
                 │  per-candidate     │  downloadable as JSON
                 │  expanders (UI)    │
                 └────────────────────┘
```

## 3. Project structure

```
AI-Resume-Screener/
├── app.py                        # Streamlit app (entry point)
├── src/
│   ├── resume_parser.py          # .txt/.pdf/.docx -> plain text
│   ├── llm_client.py             # Groq API wrapper + JSON parsing
│   └── screening.py              # Prompt design + ranking logic
├── data/
│   ├── job_descriptions/
│   │   └── data_analyst.txt      # Sample job description
│   └── sample_resumes/
│       ├── amara_de_silva.txt    # Strong fit example
│       ├── ruwan_jayasuriya.txt  # Strong fit (alternate profile)
│       ├── kasun_perera.txt      # Moderate fit example
│       └── nadeesha_fernando.txt # Weak fit example
├── requirements.txt
├── .env.example
└── README.md                     # This file
```

## 4. Setup (all free - no credit card needed anywhere)

### 4.1 Create a virtual environment and install dependencies

```bash
cd AI-Resume-Screener
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4.2 Get a free Groq API key

1. Go to [console.groq.com](https://console.groq.com) and sign in with
   email, Google, or GitHub - no credit card required.
2. Open **API Keys** in the left sidebar and click **Create API Key**.
3. Copy the key (starts with `gsk_...`).

### 4.3 Configure your API key

```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```

Open `.env` and paste your key:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

### 4.4 Run the app

```bash
streamlit run app.py
```

This opens the app in your browser (usually `http://localhost:8501`).

## 5. Using the app (demo walkthrough)

1. **Job description** - either select the bundled sample
   (`data_analyst`) from the dropdown, or paste your own.
2. **Candidate resumes** - check "Use the 4 bundled sample resumes"
   for a one-click demo, or uncheck it and upload your own `.txt`,
   `.pdf`, or `.docx` resumes.
3. Click **Screen candidates**.
4. The app shows a ranked table (Candidate, Fit Score, Verdict), plus
   an expandable card per candidate with the summary, matching
   skills, gaps, and suggested interview questions.
5. Use **Download full results as JSON** to export the results.

## 6. Explanation of the sample output

`outputs/sample_screening_results.json` is a pre-generated example
run of the app against the bundled job description and the 4 sample
resumes (included so the output can be reviewed without needing to
run the live API first). It shows the intended behavior:

- **Amara De Silva (88/100, Strong Fit)** - has direct recruitment
  analytics experience (Python, SQL, Power BI, some NLP), so she
  scores highest and the interview questions probe the depth of that
  experience.
- **Ruwan Jayasuriya (88/100, Strong Fit)** - strong SQL/Power BI and
  some forecasting, but weaker Python and no resume-parsing exposure,
  so the questions focus on those gaps.
- **Kasun Perera (35/100, Weak Fit)** - solid general Python but
  no dashboarding or recruitment-domain background, reflected in a
  low-range score.
- **Nadeesha Fernando (30/100, Weak Fit)** - strong Excel/communication
  skills but no professional Python/SQL/dashboarding experience,
  reflected in a low score with gap-focused questions.

This demonstrates that the LLM isn't just producing a single number -
it explains _why_ a candidate got that score and generates follow-up
questions grounded in the specific resume, which is the useful part
for a recruiter.

## 7. Notes on cost and limits

- Everything in this project is free: Streamlit, the Python libraries,
  and the Groq API free tier (no credit card required).
- The default model, `openai/gpt-oss-120b`, allows roughly 1,000
  requests/day and 8,000 tokens/minute on Groq's free tier as of
  August 2026 - more than enough for a demo. If you hit a rate limit,
  set `GROQ_MODEL=openai/gpt-oss-20b` in `.env` for a smaller, faster
  model with higher free-tier limits.
- Groq's free tier and rate limits can change over time - check
  [console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits)
  for the current numbers.

## 8. Limitations

- Screening quality depends on resume/JD text quality; scanned or
  image-only PDFs won't extract text (would need OCR, out of scope).
- The LLM's fit score is an assistive signal, not a hiring decision -
  it should support, not replace, human judgment.
- No persistent database; results exist only for the current session
  unless exported.

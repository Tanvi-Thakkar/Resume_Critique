import streamlit as st
import PyPDF2
import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import json
from ast import literal_eval

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Custom CSS
custom_css = """
<style>
body {
    background: linear-gradient(135deg, #f4f4f4, #eaeaea);
    font-family: 'Segoe UI', sans-serif;
}
#MainMenu, header, footer {
    visibility: hidden;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Page config
st.set_page_config(page_title="AI Resume Tool", page_icon="🧠")
st.title("🧠 AI Resume Analyzer")


# Function: Extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception:
        return ""


# Function: Analyze resume via GPT
def analyze_resume(content, job_role, include_feedback=True):
    feedback_section = (
        """,
        "strengths": ["..."],
        "weaknesses": ["..."],
        "resources": ["..."],
        "summary": "..."
        """
        if include_feedback
        else ""
    )

    prompt = f"""
You are a structured resume reviewer. Analyze the resume for the job role '{job_role}'.
Return JSON like this:
{{
    "relevance_score": 78,
    "skills": {{"Python": 90, "SQL": 70, "React": 40, "Teamwork": 85, "DSA": 75}},
    "project_fit": 65,
    "salary_estimate": "₹10–15 LPA"
    {feedback_section}
}}
Resume: {content}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Be structured and return clean JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    reply = response.choices[0].message.content.strip()
    try:
        return json.loads(reply)
    except:
        return literal_eval(reply)


# Role selector
col1, col2 = st.columns(2)
user_type = None
with col1:
    if st.button("👤 I'm a Job Applicant"):
        user_type = "applicant"
with col2:
    if st.button("🧑‍💼 I'm a Recruiter / HR"):
        user_type = "hr"

# === Applicant Mode ===
if user_type == "applicant":
    st.subheader("📄 Upload Resume for AI Feedback")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
    job_role = st.text_input("🎯 Target Job Role", placeholder="e.g. Software Engineer")

    if st.button("🚀 Analyze Resume") and uploaded_file:
        content = extract_text_from_pdf(uploaded_file)
        if content.strip():
            result = analyze_resume(content, job_role, include_feedback=True)
            st.markdown("## 📊 Resume Insights")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔍 Relevance", f"{result['relevance_score']}%")
                st.metric("💰 Salary Estimate", result["salary_estimate"])
            with col2:
                st.progress(result["relevance_score"], text="Match %")

            st.markdown("### 🧠 Skill Alignment")
            for skill, score in result["skills"].items():
                st.progress(score, text=f"{skill}: {score}%")

            st.markdown("### 🛠 Project Relevance")
            st.progress(result["project_fit"], text=f"{result['project_fit']}%")

            st.markdown("### ✅ Strengths")
            for s in result["strengths"]:
                st.markdown(f"- {s}")

            st.markdown("### ❌ Weaknesses")
            for w in result["weaknesses"]:
                st.markdown(f"- {w}")

            st.markdown("### 📚 Suggested Resources")
            for r in result["resources"]:
                st.markdown(f"- [{r}]({r})")

            st.markdown("### 📝 Summary")
            st.info(result["summary"])
        else:
            st.error("Empty or unreadable resume.")

# === Recruiter Mode ===
if user_type == "hr":
    st.subheader("📥 Upload Multiple Resumes for Screening")
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF)", type="pdf", accept_multiple_files=True
    )
    job_role = st.text_input("🎯 Job Role to Match", placeholder="e.g. Backend Developer")
    threshold = st.slider("📊 Minimum Relevance Score", 0, 100, 70)

    if st.button("📊 Analyze All Resumes") and uploaded_files:
        results = []
        for file in uploaded_files:
            content = extract_text_from_pdf(file)
            if not content.strip():
                continue
            result = analyze_resume(content, job_role, include_feedback=False)
            if result["relevance_score"] >= threshold:
                results.append(
                    {
                        "Candidate": file.name,
                        "Relevance": result["relevance_score"],
                        "Project Fit": result["project_fit"],
                        "Salary": result["salary_estimate"],
                    }
                )

        if results:
            df = pd.DataFrame(results)
            st.markdown("## ✅ Shortlisted Candidates")
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "📤 Download Shortlist",
                df.to_csv(index=False),
                "shortlist.csv",
                "text/csv",
            )
        else:
            st.warning("No resumes met the threshold.")

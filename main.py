import streamlit as st
import PyPDF2
import pandas as pd
import random
import json

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
st.title("🧠 Resume Critique")

# Extract text from PDF
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

# Dummy analyzer to simulate AI output
def analyze_resume(content, job_role, include_feedback=True):
    skills_list = ["Python", "SQL", "React", "Teamwork", "DSA", "Java", "Node.js", "Docker", "MongoDB"]
    skill_scores = {skill: random.randint(50, 95) for skill in random.sample(skills_list, 5)}

    return {
        "relevance_score": random.randint(60, 95),
        "skills": skill_scores,
        "project_fit": random.randint(50, 90),
        "salary_estimate": "₹8–12 LPA",
        "strengths": ["Well-structured resume", "Good technical stack", "Teamwork skills"],
        "weaknesses": ["Missing certifications", "Limited backend experience"],
        "resources": [
            "https://www.geeksforgeeks.org/data-structures",
            "https://roadmap.sh/backend",
            "https://reactjs.org/docs/getting-started.html"
        ],
        "summary": f"The resume aligns well with a {job_role} role, with potential to improve in backend development and certifications."
    }

# Role selector
if "user_type" not in st.session_state:
    st.session_state.user_type = None

col1, col2 = st.columns(2)
with col1:
    if st.button("👤 I'm a Job Applicant"):
        st.session_state.user_type = "applicant"
with col2:
    if st.button("🧑‍💼 I'm a Recruiter / HR"):
        st.session_state.user_type = "hr"

user_type = st.session_state.user_type

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
                st.metric("💰 Salary Estimate", result['salary_estimate'])
            with col2:
                st.progress(result['relevance_score'], text="Match %")

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
    uploaded_files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)
    job_role = st.text_input("🎯 Job Role to Match", placeholder="e.g. Backend Developer")
    threshold = st.slider("📊 Minimum Relevance Score", 0, 100, 70)

    if st.button("📊 Analyze All Resumes") and uploaded_files:
        results = []
        for file in uploaded_files:
            content = extract_text_from_pdf(file)
            if not content.strip():
                continue
            result = analyze_resume(content, job_role, include_feedback=False)
            if result and result.get("relevance_score", 0) >= threshold:
                results.append({
                    "Candidate": file.name,
                    "Relevance": result["relevance_score"],
                    "Project Fit": result["project_fit"],
                    "Salary": result["salary_estimate"]
                })

        if results:
            df = pd.DataFrame(results)
            st.markdown("## ✅ Shortlisted Candidates")
            st.dataframe(df, use_container_width=True)
            st.download_button("📤 Download Shortlist", df.to_csv(index=False), "shortlist.csv", "text/csv")
        else:
            st.warning("No resumes met the threshold.")

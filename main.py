import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Page config
st.set_page_config(page_title="AI Resume Critique", page_icon=":receipt:")
st.title("🧠 AI Resume Critique")
st.markdown("Upload your resume and get **AI-powered, job-specific feedback**, including estimated salary and skill match.")

# File uploader and job role input
uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type="pdf")
job_role = st.text_input("🎯 Target Job Role", placeholder="e.g. Software Engineer, Data Scientist")
analyze = st.button("🚀 Analyze Resume")

# Function to extract PDF text
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""

if analyze and uploaded_file:
    file_content = extract_text_from_pdf(uploaded_file)

    if not file_content.strip():
        st.error("The uploaded PDF file is empty or could not be read.")
        st.stop()

    # Build the prompt
    prompt = f"""
You are an expert resume reviewer. Analyze the following resume for the job role '{job_role if job_role else 'general job applications'}':\n\n{file_content}\n\n
1. Rate the resume's overall relevance to the job (as a percentage).
2. Identify top 5 key skills and rate their alignment with the job (as percentages).
3. Review listed projects and rate their fit for the job.
4. Estimate a reasonable salary range based on the resume and job role (in INR).
5. List 3-5 suggestions for improvement.
Format your response in JSON like this:
{{
  "relevance_score": 78,
  "skills": {{"Python": 90, "React": 60, "SQL": 70, "Teamwork": 85, "ML": 75}},
  "project_fit": 65,
  "salary_estimate": "₹10–15 LPA",
  "improvements": ["Add more recent projects", "Quantify achievements", "Include system design experience"]
}}
"""

    try:
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful and structured resume reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        import json
        from ast import literal_eval

        # Parse GPT output
        content = response.choices[0].message.content.strip()
        try:
            data = json.loads(content)
        except:
            data = literal_eval(content)  # fallback

        # Display Dashboard
        st.markdown("## 📊 Resume Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("🔎 Relevance Score", f"{data['relevance_score']}%")
            st.metric("💰 Estimated Salary", data['salary_estimate'])

        with col2:
            st.progress(data['relevance_score'], text="Overall Match")

        st.markdown("### 🧠 Skill Alignment")
        for skill, score in data["skills"].items():
            st.progress(score, text=f"{skill}: {score}%")

        st.markdown("### 🛠 Project Relevance")
        st.progress(data["project_fit"], text=f"{data['project_fit']}% Match with Role")

        st.markdown("### 📉 Suggestions to Improve")
        for item in data["improvements"]:
            st.markdown(f"- {item}")

    except Exception as e:
        st.error(f"An error occurred while processing the resume: {e}")

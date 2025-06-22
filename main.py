import streamlit as st
import PyPDF2
import json
from openai import OpenAI

st.title("🧠 Resume Critique App")

api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
uploaded_file = st.file_uploader("📄 Upload your Resume (PDF)", type="pdf")
job_role = st.text_input("🎯 Target Job Role", placeholder="e.g. Data Scientist")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def analyze_resume(resume_text, job_role, key):
    client = OpenAI(api_key=key)
    prompt = f"""
You are a resume reviewer. Evaluate the resume below for the job role '{job_role}'.
Return a JSON response like:
{{
  "relevance_score": 78,
  "skills": {{"Python": 90, "SQL": 70}},
  "summary": "..."
}}

Resume:
{resume_text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Return structured JSON only."},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

if st.button("🚀 Analyze") and uploaded_file and api_key and job_role:
    text = extract_text_from_pdf(uploaded_file)
    result = analyze_resume(text, job_role, api_key)
    if result:
        st.success("✅ Analysis complete!")
        st.json(result)

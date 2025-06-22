import streamlit as st
import PyPDF2
import openai
import json

st.title("🧠 Resume Critique App")

api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
job_role = st.text_input("🎯 Target Job Role", placeholder="e.g. Data Scientist")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def analyze_resume(resume_text, job_role, key):
    openai.api_key = key
    prompt = f"""
You are a resume reviewer. Evaluate this resume for the job '{job_role}'.
Return JSON with relevance_score, skills (dict), summary.

Resume:
{resume_text}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Return structured JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

if st.button("Analyze") and uploaded_file and api_key and job_role:
    resume_text = extract_text_from_pdf(uploaded_file)
    result = analyze_resume(resume_text, job_role, api_key)
    if result:
        st.json(result)

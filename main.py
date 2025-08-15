import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import io

# --- Load API key from environment ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("No OpenAI API key found. Please set OPENAI_API_KEY in your environment.")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(page_title="Resume Critique", page_icon="📄")

st.title("📄 AI Resume Critique")

# --- Keep file in session state ---
if "resume_file" not in st.session_state:
    st.session_state.resume_file = None

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])

if uploaded_file is not None:
    st.session_state.resume_file = uploaded_file

if st.session_state.resume_file is not None:
    st.success(f"Uploaded: {st.session_state.resume_file.name}")

    if st.button("Analyze Resume"):
        with st.spinner("Analyzing your resume... ⏳"):

            file_bytes = st.session_state.resume_file.read()

            # Convert PDF/DOCX to text
            import fitz  # PyMuPDF for PDF
            import docx

            resume_text = ""
            if st.session_state.resume_file.name.endswith(".pdf"):
                pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
                for page in pdf_doc:
                    resume_text += page.get_text()
            elif st.session_state.resume_file.name.endswith(".docx"):
                doc = docx.Document(io.BytesIO(file_bytes))
                for para in doc.paragraphs:
                    resume_text += para.text + "\n"

            if not resume_text.strip():
                st.error("Could not extract text from your resume. Please upload a valid file.")
                st.stop()

            # --- Call OpenAI ---
            prompt = f"""
            You are an expert career coach and recruiter. Review this resume text and provide:
            1. Strengths
            2. Weaknesses
            3. Suggested improvements
            4. ATS optimization tips

            Resume:
            {resume_text}
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",  # cheaper + good quality
                messages=[
                    {"role": "system", "content": "You are a professional career coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            critique = response.choices[0].message.content
            st.subheader("📊 Resume Review")
            st.write(critique)

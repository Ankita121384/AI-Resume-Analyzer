import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import fitz
import docx

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "pdf":
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif file_type == "docx":
        document = docx.Document(uploaded_file)
        text = "\n".join([para.text for para in document.paragraphs])
        return text
    else:
        return None

def analyze_resume(resume_text, job_role):
    prompt = f"""
You are an expert career coach and ATS specialist.

Analyze the resume below for someone applying for: **{job_role}**

Respond in this exact format:

## 📊 Resume Score
Give a score out of 100 with a one-line reason.

## ✅ Strengths
List 3-5 strong points of this resume.

## ⚠️ Areas for Improvement
List 3-5 specific things that should be improved.

## 🛠️ Missing Skills
List important skills for a {job_role} role that are missing.

## 💡 Suggestions to Improve Resume
Give 3-5 concrete, actionable suggestions.

## 🎯 Interview Preparation Tips
Give 5 tips to prepare for an interview based on this resume.

---
RESUME:
{resume_text}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="centered")

st.title("📄 AI Resume Analyzer")
st.markdown("Upload your resume and get **AI-powered feedback** to land your dream job!")
st.divider()

job_role = st.text_input("🎯 What job role are you targeting?",
    placeholder="e.g. Data Analyst, Software Engineer, AI Intern")

uploaded_file = st.file_uploader("📎 Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])

if st.button("🔍 Analyze My Resume", use_container_width=True):
    if not job_role:
        st.warning("Please enter a target job role.")
    elif uploaded_file is None:
        st.warning("Please upload your resume.")
    else:
        with st.spinner("Analyzing your resume with AI... ⏳"):
            resume_text = extract_text(uploaded_file)
            if not resume_text or len(resume_text.strip()) < 50:
                st.error("Could not extract text from your resume. Please check the file.")
            else:
                feedback = analyze_resume(resume_text, job_role)
                st.success("Analysis complete! ✅")
                st.divider()
                st.markdown(feedback)

st.divider()
st.caption("Built with ❤️ using Python, Streamlit & Groq AI")
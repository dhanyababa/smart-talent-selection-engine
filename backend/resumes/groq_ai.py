import os
import json
import re
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def safe_json_loads(content):
    try:
        return json.loads(content)
    except:
        pass

    match = re.search(r"\{.*\}", content, re.DOTALL)

    if match:
        return json.loads(match.group())

    raise ValueError("No valid JSON found in AI response")


def extract_profile_with_ai(resume_text):
    prompt = f"""
Extract resume details and return ONLY valid JSON.

Use this exact JSON format:
{{
  "name": "",
  "email": "",
  "phone": "",
  "years_experience": 0,
  "top_skills": [],
  "professional_experience": "",
  "academic_projects": "",
  "certifications": "",
  "summary": ""
}}

Resume Text:
{resume_text[:6000]}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Return only valid JSON. No markdown. No explanation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()
        return safe_json_loads(content)

    except Exception as e:
        return {
            "name": "AI Extraction Failed",
            "email": "",
            "phone": "",
            "years_experience": 0,
            "top_skills": [],
            "professional_experience": "",
            "academic_projects": "",
            "certifications": "",
            "summary": str(e)
        }


def generate_ai_justification(job_description, profile, score):
    prompt = f"""
Write exactly 2 sentences explaining why this candidate fits the job.

Job Description:
{job_description}

Candidate Profile:
{profile}

Score:
{score}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an HR recruiter assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"AI justification failed: {str(e)}"
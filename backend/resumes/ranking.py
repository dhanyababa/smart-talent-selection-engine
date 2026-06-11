from sentence_transformers import SentenceTransformer, util
from .groq_ai import generate_ai_justification

model = SentenceTransformer("all-MiniLM-L6-v2")


def profile_to_text(profile):
    return f"""
    Name: {profile.get("name")}
    Experience: {profile.get("years_experience")} years
    Skills: {profile.get("top_skills")}
    Professional Experience: {profile.get("professional_experience")}
    Academic Projects: {profile.get("academic_projects")}
    Certifications: {profile.get("certifications")}
    Summary: {profile.get("summary")}
    """


def calculate_score(job_description, profile):
    candidate_text = profile_to_text(profile)

    jd_embedding = model.encode(job_description, convert_to_tensor=True)
    candidate_embedding = model.encode(candidate_text, convert_to_tensor=True)

    similarity = util.cos_sim(jd_embedding, candidate_embedding).item()

    years = profile.get("years_experience", 0)

    try:
        years = int(years)
    except:
        years = 0

    experience_bonus = min(years * 2, 10)

    final_score = similarity * 90 + experience_bonus

    return round(min(final_score, 100), 2)


def generate_justification(job_description, profile, score):
    return generate_ai_justification(job_description, profile, score)
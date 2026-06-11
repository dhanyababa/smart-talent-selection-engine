from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import JobRole, Resume, CandidateRanking
from .serializers import JobRoleSerializer, ResumeSerializer, CandidateRankingSerializer
from .parser import extract_text
from .groq_ai import extract_profile_with_ai
from .ranking import calculate_score, generate_justification


@api_view(['GET', 'POST'])
def job_roles(request):
    if request.method == 'GET':
        jobs = JobRole.objects.all().order_by('-created_at')
        return Response(JobRoleSerializer(jobs, many=True).data)

    serializer = JobRoleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
def upload_resume(request):
    job_role_id = request.data.get('job_role')
    files = request.FILES.getlist('files')

    if not job_role_id:
        return Response({"error": "Job role is required"}, status=400)

    if not files:
        return Response({"error": "At least one resume file is required"}, status=400)

    try:
        job_role = JobRole.objects.get(id=job_role_id)
    except JobRole.DoesNotExist:
        return Response({"error": "Invalid job role"}, status=404)

    allowed_extensions = [".pdf", ".docx", ".jpg", ".jpeg", ".png"]
    uploaded = []

    for file in files:
        file_name = file.name.lower()

        resume = Resume.objects.create(
            job_role=job_role,
            file=file,
            upload_status="Uploading"
        )

        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            resume.upload_status = "Failed"
            resume.error_message = "Unsupported file format"
            resume.save()
            uploaded.append(resume)
            continue

        try:
            resume.upload_status = "Extracting Text"
            resume.save()

            text = extract_text(resume.file.path)

            if not text or len(text.strip()) < 20:
                resume.upload_status = "Failed"
                resume.error_message = "Could not extract enough text. File may be corrupt or image quality may be low."
                resume.save()
                uploaded.append(resume)
                continue

            resume.upload_status = "AI Parsing"
            resume.save()

            profile = extract_profile_with_ai(text)

            resume.raw_text = text
            resume.parsed_profile = profile
            resume.candidate_name = profile.get("name", "")
            resume.email = profile.get("email", "")
            resume.phone = profile.get("phone", "")
            resume.upload_status = "Parsed"
            resume.save()

        except Exception as e:
            resume.upload_status = "Failed"
            resume.error_message = str(e)
            resume.save()

        uploaded.append(resume)

    return Response(ResumeSerializer(uploaded, many=True).data)


@api_view(['GET'])
def resumes_by_job(request, job_id):
    resumes = Resume.objects.filter(job_role_id=job_id)
    return Response(ResumeSerializer(resumes, many=True).data)

@api_view(['POST'])
def rank_candidates(request, job_id):
    try:
        job = JobRole.objects.get(id=job_id)
    except JobRole.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)

    resumes = Resume.objects.filter(job_role=job, upload_status="Parsed")

    CandidateRanking.objects.filter(job_role=job).delete()

    scored_candidates = []

    for resume in resumes:
        score = calculate_score(job.description, resume.parsed_profile)
        scored_candidates.append((resume, score))

    scored_candidates.sort(key=lambda item: item[1], reverse=True)

    for index, item in enumerate(scored_candidates):
        resume = item[0]
        score = item[1]

        if index < 5:
            justification = generate_justification(job.description, resume.parsed_profile, score)
        else:
            justification = "Candidate ranked based on semantic similarity and experience weight."

        CandidateRanking.objects.create(
            job_role=job,
            resume=resume,
            score=score,
            justification=justification
        )

    rankings = CandidateRanking.objects.filter(job_role=job)
    return Response(CandidateRankingSerializer(rankings, many=True).data)


@api_view(['GET'])
def dashboard_summary(request):
    jobs = JobRole.objects.all().order_by('-created_at')

    data = []

    for job in jobs:
        top_candidate = CandidateRanking.objects.filter(job_role=job).first()

        data.append({
            "id": job.id,
            "title": job.title,
            "resume_count": job.resumes.count(),
            "top_candidate": top_candidate.resume.candidate_name if top_candidate else "Not ranked yet",
            "top_score": top_candidate.score if top_candidate else None,
        })

    return Response(data)
@api_view(['POST'])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        return Response({
            "success": True,
            "message": "Login successful",
            "username": user.username
        })

    return Response({
        "success": False,
        "message": "Invalid username or password"
    }, status=401)
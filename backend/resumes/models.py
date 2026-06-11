# from django.db import models

# Create your models here.
from django.db import models


class JobRole(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Resume(models.Model):
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')

    batch_date = models.DateField(auto_now_add=True)

    candidate_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    raw_text = models.TextField(blank=True)
    parsed_profile = models.JSONField(default=dict)

    upload_status = models.CharField(max_length=50, default='Pending')
    error_message = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.candidate_name or self.file.name


class CandidateRanking(models.Model):
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    justification = models.TextField(blank=True)

    class Meta:
        ordering = ['-score']
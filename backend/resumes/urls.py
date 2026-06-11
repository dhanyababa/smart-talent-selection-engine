from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.job_roles),
    path('dashboard/', views.dashboard_summary),
    path('upload-resume/', views.upload_resume),
    path('jobs/<int:job_id>/resumes/', views.resumes_by_job),
    path('jobs/<int:job_id>/rank/', views.rank_candidates),
    path('login/', views.login_view),
]
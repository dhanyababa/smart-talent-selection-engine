# Smart Talent Selection Engine

A Python Full Stack with GenAI project for semantic resume screening and candidate ranking.
# Smart Talent Selection Engine

## Overview

Smart Talent Selection Engine is an AI-powered recruitment platform designed to streamline high-volume hiring processes. Traditional Applicant Tracking Systems (ATS) rely heavily on keyword matching, which often leads to the rejection of highly qualified candidates whose resumes use different terminology than the job description.

This project leverages Generative AI, semantic similarity models, and automated resume parsing to understand candidate profiles beyond simple keyword matching. Recruiters can upload resumes in multiple formats, automatically extract structured candidate information, rank candidates against a job description, and receive AI-generated hiring

## Features

- Recruiter dashboard
- Job role creation
- Bulk resume upload
- PDF, DOCX, JPG, PNG support
- Resume parsing
- Semantic skill mapping
- JD-to-candidate ranking
- AI-generated justification for candidate fit

## Tech Stack

Frontend:
- React
- Vite
- Axios

Backend:
- Django
- Django REST Framework
- SQLite
- PyMuPDF
- python-docx
- pytesseract
- sentence-transformers

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


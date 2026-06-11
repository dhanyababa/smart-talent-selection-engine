from rest_framework import serializers
from .models import JobRole, Resume, CandidateRanking


class JobRoleSerializer(serializers.ModelSerializer):
    resume_count = serializers.SerializerMethodField()

    class Meta:
        model = JobRole
        fields = '__all__'

    def get_resume_count(self, obj):
        return obj.resumes.count()


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'


class CandidateRankingSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer()

    class Meta:
        model = CandidateRanking
        fields = '__all__'
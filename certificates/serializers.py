# G:\My Projects\certificates\serializers.py

from rest_framework import serializers
from .models import Certificate

class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='progress.enrollment.student.user.username')
    course_title = serializers.ReadOnlyField(source='progress.enrollment.course.title')

    class Meta:
        model = Certificate
        fields = ['id', 'certificate_number', 'issue_date', 'file_url', 'student_name', 'course_title']
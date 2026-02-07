# G:\My Projects\trainings\serializers.py

from rest_framework import serializers
from .models import TrainingProgram, EnrollmentTraining

class TrainingProgramSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.company_name')
    current_participants = serializers.SerializerMethodField()

    class Meta:
        model = TrainingProgram
        fields = [
            'id', 'company', 'company_name', 'program_name', 
            'description', 'category', 'live_link', 'live_status',
            'scheduled_date', 'duration_hours', 'instructor_name',
            'instructor_email', 'max_participants', 'current_participants',
            'prerequisites', 'recording_link', 'resource_link',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['company', 'created_at', 'updated_at', 'current_participants']
    
    def get_current_participants(self, obj):
        """Get count of enrolled students"""
        return obj.enrolled_students.count()

class EnrollmentTrainingSerializer(serializers.ModelSerializer):
    program_details = TrainingProgramSerializer(source='program', read_only=True)

    class Meta:
        model = EnrollmentTraining
        fields = [
            'id', 'student', 'program', 'program_details', 
            'enrolled_at', 'completion_status'
        ]
        read_only_fields = ['student', 'enrolled_at']
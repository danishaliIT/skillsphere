# G:\My Projects\enrollments\serializers.py

from rest_framework import serializers
from .models import EnrollmentCourse, TrackProgress, Payment
from courses.serializers import CourseSerializer

class TrackProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackProgress
        fields = ['percentage', 'status', 'last_accessed']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id', 'status', 'paid_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    # Course ki details bhi saath dikhane ke liye
    course_details = CourseSerializer(source='course', read_only=True)
    progress = TrackProgressSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = EnrollmentCourse
        fields = ['id', 'student', 'course', 'course_details', 'enrolled_at', 'status', 'progress', 'payment']
        read_only_fields = ['student', 'enrolled_at']
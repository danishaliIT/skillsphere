from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import StudentProfileSerializer, InstructorProfileSerializer, CompanyProfileSerializer
from .models import StudentProfile, InstructorProfile, CompanyProfile
from django.db import transaction
from django.http import Http404
from .models import InstructorProfile
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import (
    InstructorEducation,
    InstructorEmployment,
    InstructorCertificate,
)
from .serializers import (
    InstructorEducationSerializer,
    InstructorEmploymentSerializer,
    InstructorCertificateSerializer,
)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self, role):
        if role == 'Student': return StudentProfileSerializer
        if role == 'Instructor': return InstructorProfileSerializer
        return CompanyProfileSerializer

    def get_profile(self, user):
        # Role-based profile fetching
        try:
            if user.role == 'Student':
                return user.student_profile
            if user.role == 'Instructor':
                return user.instructor_profile
            return user.company_profile
        except Exception:
            # If related profile is missing (old users), create one on-demand to avoid 500 errors
            with transaction.atomic():
                if user.role == 'Student':
                    return StudentProfile.objects.create(user=user)
                if user.role == 'Instructor':
                    return InstructorProfile.objects.create(user=user)
                return CompanyProfile.objects.create(user=user)

    def get(self, request):
        profile = self.get_profile(request.user)
        # Nested data (Address/Socials) automatically fetch ho jayega
        serializer = self.get_serializer_class(request.user.role)(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = self.get_profile(request.user)
        # 'partial=True' allows updating only specific fields
        serializer = self.get_serializer_class(request.user.role)(
            profile, data=request.data, partial=True
        )
        
        if serializer.is_valid():
            serializer.save() # Serializer will handle Address/Education logic
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Account deletion logic
        user = request.user
        user.delete()
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
class PublicStudentProfileView(APIView):
    # Public endpoint so recruiters and others can view public profiles
    permission_classes = [AllowAny]

    def get(self, request, pk=None, username=None):
        try:
            if username:
                student = StudentProfile.objects.filter(user__username=username, public_profile=True).first()
            elif pk:
                student = StudentProfile.objects.filter(pk=pk, public_profile=True).first()
            else:
                return Response({"error": "Provide pk or username"}, status=status.HTTP_400_BAD_REQUEST)

            if not student:
                return Response({"error": "Student not found or not public"}, status=status.HTTP_404_NOT_FOUND)

            serializer = StudentProfileSerializer(student)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
class StudentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # StudentProfile model se saara data uthayen
        students = StudentProfile.objects.all()
        # StudentProfileSerializer use karein
        serializer = StudentProfileSerializer(students, many=True)
        return Response(serializer.data)


class PublicInstructorProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None, username=None):
        try:
            if username:
                instructor = InstructorProfile.objects.filter(user__username=username, public_profile=True).first()
            elif pk:
                instructor = InstructorProfile.objects.filter(pk=pk, public_profile=True).first()
            else:
                return Response({"error": "Provide pk or username"}, status=status.HTTP_400_BAD_REQUEST)

            if not instructor:
                return Response({"error": "Instructor not found or not public"}, status=status.HTTP_404_NOT_FOUND)

            serializer = InstructorProfileSerializer(instructor)
            return Response(serializer.data)
        except InstructorProfile.DoesNotExist:
            return Response({"error": "Instructor not found"}, status=status.HTTP_404_NOT_FOUND)


class InstructorEducationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.instructor_profile
        qs = InstructorEducation.objects.filter(profile=profile)
        serializer = InstructorEducationSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        profile = request.user.instructor_profile
        serializer = InstructorEducationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstructorEducationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return InstructorEducation.objects.get(pk=pk)
        except InstructorEducation.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj.profile.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InstructorEducationSerializer(obj)
        return Response(serializer.data)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj.profile.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InstructorEducationSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj.profile.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from trainings.models import TrainingProgram, EnrollmentTraining  # ✅ YEH SAHI HAI
from django.utils import timezone
from datetime import timedelta

class CompanyDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure user is a company
        if request.user.role != 'Company':
            return Response({"error": "Unauthorized"}, status=403)
        
        company = request.user.company_profile
        
        # 1. Get all programs by this company
        programs = TrainingProgram.objects.filter(company=company)
        
        # 2. Get all enrollments in these programs
        all_enrollments = EnrollmentTraining.objects.filter(program__in=programs)
        
        # --- CALCULATIONS ---
        
        # Total Unique Students (Active Employees Proxy)
        total_employees = all_enrollments.values('student').distinct().count()
        
        # New Enrolled this month
        now = timezone.now()
        first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = all_enrollments.filter(enrolled_at__gte=first_day_this_month).count()
        
        # Certificates Issued (Completed Trainings)
        certificates_issued = all_enrollments.filter(completion_status='completed').count()
        
        # Avg Completion Rate
        total_records = all_enrollments.count()
        if total_records > 0:
            avg_completion = int((certificates_issued / total_records) * 100)
        else:
            avg_completion = 0

        return Response({
            "total_employees": total_employees,
            "new_this_month": new_this_month,
            "avg_completion": avg_completion,
            "certificates_issued": certificates_issued
        })


class InstructorEmploymentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.instructor_profile
        qs = InstructorEmployment.objects.filter(profile=profile)
        serializer = InstructorEmploymentSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        profile = request.user.instructor_profile
        serializer = InstructorEmploymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstructorEmploymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return InstructorEmployment.objects.get(pk=pk)
        except InstructorEmployment.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj.profile.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InstructorEmploymentSerializer(obj)
        return Response(serializer.data)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj.profile.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InstructorEmploymentSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj.profile.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InstructorCertificateListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        profile = request.user.instructor_profile
        qs = InstructorCertificate.objects.filter(profile=profile)
        serializer = InstructorCertificateSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        profile = request.user.instructor_profile
        serializer = InstructorCertificateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstructorCertificateDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        try:
            return InstructorCertificate.objects.get(pk=pk)
        except InstructorCertificate.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        obj = self.get_object(pk)
        if obj.profile.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InstructorCertificateSerializer(obj, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        obj = self.get_object(pk)
        if obj.profile.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = InstructorCertificateSerializer(obj, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        if obj.profile.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
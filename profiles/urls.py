from django.urls import path
from .views import (
    UserProfileView,
    PublicStudentProfileView,
    StudentListView,
    PublicInstructorProfileView,
    InstructorEducationListCreateView,
    InstructorEducationDetailView,
    InstructorEmploymentListCreateView,
    InstructorEmploymentDetailView,
    InstructorCertificateListCreateView,
    InstructorCertificateDetailView,
    CompanyDashboardStatsView,
)

urlpatterns = [
    # 1. Own Profile: GET (view) aur PATCH (update)
    # Ek hi endpoint par Student, Instructor, aur Company apna data manage karenge.
    path('me/', UserProfileView.as_view(), name='my-profile'),
    path('dashboard/stats/', CompanyDashboardStatsView.as_view(), name='company-dashboard-stats'),

    # 2. Student List: Companies aur Instructors ke liye
    # Yahan se saare students ka data list ki surat mein milega.
    path('students/', StudentListView.as_view(), name='student-list'),

    # 3. Public Portfolio: Recruiter access ke liye
    # Kisi bhi makhsoos student ka portfolio dekhne ke liye (e.g. Danish ki profile).
    path('student/<int:pk>/', PublicStudentProfileView.as_view(), name='public-student-profile'),
    path('student/username/<str:username>/', PublicStudentProfileView.as_view(), name='public-student-by-username'),
    path('instructor/<int:pk>/', PublicInstructorProfileView.as_view(), name='public-instructor-profile'),
    path('instructor/username/<str:username>/', PublicInstructorProfileView.as_view(), name='public-instructor-by-username'),
    # Instructor nested CRUD endpoints
    path('instructor/education/', InstructorEducationListCreateView.as_view(), name='instructor-education-list'),
    path('instructor/education/<int:pk>/', InstructorEducationDetailView.as_view(), name='instructor-education-detail'),
    path('instructor/employment/', InstructorEmploymentListCreateView.as_view(), name='instructor-employment-list'),
    path('instructor/employment/<int:pk>/', InstructorEmploymentDetailView.as_view(), name='instructor-employment-detail'),
    path('instructor/certificates/', InstructorCertificateListCreateView.as_view(), name='instructor-certificate-list'),
    path('instructor/certificates/<int:pk>/', InstructorCertificateDetailView.as_view(), name='instructor-certificate-detail'),
]
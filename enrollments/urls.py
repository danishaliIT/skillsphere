from django.urls import path
from .views import EnrollInCourseView, MyEnrolledCoursesView, ProcessPaymentView, UpdateProgressView

urlpatterns = [
    # 1. Nayi enrollment ke liye
    path('enroll/<int:course_id>/', EnrollInCourseView.as_view(), name='enroll-course'),
    
    # 2. Student ke dashboard ke liye list
    path('my-courses/', MyEnrolledCoursesView.as_view(), name='my-enrolled-courses'),
    
    # 3. Payment process karne ke liye
    path('payment/<int:enrollment_id>/', ProcessPaymentView.as_view(), name='process-payment'),
    
    # 4. Progress update (0% to 100%)
    path('progress/<int:enrollment_id>/', UpdateProgressView.as_view(), name='update-progress'),
]
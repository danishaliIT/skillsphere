from django.utils import timezone
from rest_framework import views, status, permissions, generics
from rest_framework.response import Response
from .models import EnrollmentCourse, TrackProgress, Payment
from .serializers import EnrollmentSerializer
from courses.models import Course

# 1. ENROLLMENT: Course mein dakhla lena
class EnrollInCourseView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        if request.user.role != 'Student':
            return Response({"error": "Only students can enroll."}, status=status.HTTP_403_FORBIDDEN)

        try:
            course = Course.objects.get(id=course_id)
            student_profile = request.user.student_profile
            
            if EnrollmentCourse.objects.filter(student=student_profile, course=course).exists():
                return Response({"error": "Already enrolled!"}, status=status.HTTP_400_BAD_REQUEST)

            # --- NEW PRICE CHECK LOGIC ---
            if course.price > 0:
                # Paid Course: Status 'pending' rakhein jab tak payment confirm na ho
                enrollment = EnrollmentCourse.objects.create(
                    student=student_profile, 
                    course=course, 
                    status='pending' 
                )
                return Response({
                    "action": "payment_required",
                    "enrollment_id": enrollment.id,
                    "price": course.price,
                    "message": f"This course costs ${course.price}. Please complete payment."
                }, status=status.HTTP_200_OK)

            # Free Course: Direct 'active'
            enrollment = EnrollmentCourse.objects.create(student=student_profile, course=course, status='active')
            return Response({"action": "enrolled", "message": "Successfully enrolled!"}, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

# 2. PROGRESS: Learning journey track karna
class UpdateProgressView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, enrollment_id):
        try:
            # Ensure karna ke student sirf apni progress update kare
            progress = TrackProgress.objects.get(
                enrollment_id=enrollment_id, 
                enrollment__student=request.user.student_profile
            )
            percentage = request.data.get('percentage')
            
            if percentage is not None:
                progress.update_progress(int(percentage)) # Model method call
                return Response({"message": "Progress updated", "status": progress.status})
            
            return Response({"error": "Percentage is required"}, status=status.HTTP_400_BAD_REQUEST)
        except TrackProgress.DoesNotExist:
            return Response({"error": "Record not found"}, status=status.HTTP_404_NOT_FOUND)

# 3. PAYMENT: Paid courses ko activate karna
class ProcessPaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, enrollment_id):
        try:
            enrollment = EnrollmentCourse.objects.get(id=enrollment_id)
            
            # Payment record dhoondein ya banayein
            payment, created = Payment.objects.get_or_create(
                enrollment=enrollment,
                defaults={'amount': enrollment.course.price}
            )

            transaction_id = request.data.get('transaction_id')
            payment_method = request.data.get('payment_method')

            if transaction_id:
                payment.status = 'completed'
                payment.transaction_id = transaction_id
                payment.payment_method = payment_method
                payment.paid_at = timezone.now() # Missing import fixed
                payment.save()

                # Payment ke baad enrollment ko 'active' karna
                enrollment.status = 'active'
                enrollment.save()

                return Response({"message": "Payment successful and course activated!"})
            
            return Response({"error": "Transaction ID missing"}, status=status.HTTP_400_BAD_REQUEST)

        except EnrollmentCourse.DoesNotExist:
            return Response({"error": "Enrollment not found"}, status=status.HTTP_404_NOT_FOUND)

# 4. DASHBOARD LIST: Student ke apne courses
class MyEnrolledCoursesView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Dashboard par Danish ke filter shuda courses
        return EnrollmentCourse.objects.filter(student=self.request.user.student_profile)
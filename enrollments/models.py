from django.db import models
from profiles.models import StudentProfile
from courses.models import Course
from django.utils import timezone

class EnrollmentCourse(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        # Aik student aik course mein do baar enroll nahi ho sakta
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.user.username} -> {self.course.title}"

class TrackProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    # Schema: enrollment_id (1:1 relationship)
    enrollment = models.OneToOneField(
        'EnrollmentCourse', 
        on_delete=models.CASCADE, 
        related_name='progress'
    )
    percentage = models.IntegerField(default=0) # 0 to 100
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progress: {self.enrollment.student.user.username} - {self.percentage}%"

    def update_progress(self, new_percentage):
        self.percentage = new_percentage
        if self.percentage >= 100:
            self.status = 'completed'
        elif self.percentage > 0:
            self.status = 'in_progress'
        self.save()

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Wallet'),
    ]

    enrollment = models.OneToOneField(EnrollmentCourse, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    transaction_id = models.CharField(max_length=255, unique=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment: {self.enrollment.course.title} - {self.status}"
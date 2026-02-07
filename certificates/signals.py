from django.db.models.signals import post_save
from django.dispatch import receiver
from enrollments.models import TrackProgress
from .models import Certificate
from notifications.models import Notification

@receiver(post_save, sender=TrackProgress)
def check_for_completion(sender, instance, **kwargs):
    # Agar progress 100% hai aur pehle se certificate nahi bana
    if instance.percentage >= 100 and not hasattr(instance, 'certificate'):
        # 1. Certificate Create Karein
        Certificate.objects.create(progress=instance)
        
        # 2. Student ko Notification Bhejein
        Notification.objects.create(
            user=instance.enrollment.student.user,
            title="Course Completed! 🎓",
            message=f"Congratulations! You have successfully completed {instance.enrollment.course.title}. Your certificate is ready.",
            notification_type="Alert"
        )
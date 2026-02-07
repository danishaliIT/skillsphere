from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.models import Notification
from .models import Course

@receiver(post_save, sender=Course)
def create_course_creation_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.instructor.user,  # ✅ FIX HERE
            title='New Course Created',
            message=f'You have successfully created a new course: "{instance.title}".',
            notification_type='Course_Creation'
        )

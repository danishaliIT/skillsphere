from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EnrollmentCourse, TrackProgress

@receiver(post_save, sender=EnrollmentCourse)
def create_progress_record(sender, instance, created, **kwargs):
    if created:
        # Enrollment hote hi progress 0% par set kardo
        TrackProgress.objects.create(enrollment=instance)
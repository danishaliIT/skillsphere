from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EnrollmentTraining
from notifications.models import Notification # Jo humne pehle banaya tha

@receiver(post_save, sender=EnrollmentTraining)
def notify_company_on_enrollment(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.program.company.user, # Company ka user
            title="New Student Enrolled",
            message=f"{instance.student.user.username} has joined your program: {instance.program.program_name}",
            notification_type="Update"
        )
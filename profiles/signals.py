from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile, InstructorProfile, CompanyProfile
from notifications.models import Notification

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'Student':
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'Instructor':
            InstructorProfile.objects.create(user=instance)
        elif instance.role == 'Company':
            CompanyProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'Student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.role == 'Instructor' and hasattr(instance, 'instructor_profile'):
        instance.instructor_profile.save()
    elif instance.role == 'Company' and hasattr(instance, 'company_profile'):
        instance.company_profile.save()


@receiver(post_save, sender=StudentProfile)
def notify_profile_updated(sender, instance, created, **kwargs):
    # Don't notify on initial creation
    if created:
        return

    # Create a user-facing notification about profile update
    try:
        Notification.objects.create(
            user=instance.user,
            title="Profile Updated",
            message="Your profile was updated successfully.",
            notification_type="Update"
        )
    except Exception:
        # Avoid breaking the save flow if notifications fail
        pass


@receiver(post_save, sender=InstructorProfile)
def notify_instructor_profile_updated(sender, instance, created, **kwargs):
    if created:
        return

    try:
        Notification.objects.create(
            user=instance.user,
            title="Profile Updated",
            message="Your instructor profile was updated successfully.",
            notification_type="Update"
        )
    except Exception:
        pass
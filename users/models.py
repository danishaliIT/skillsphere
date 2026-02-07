from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import random
from datetime import timedelta


class User(AbstractUser):
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Instructor', 'Instructor'),
        ('Company', 'Company'),
        ('Admin', 'Admin'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

    # Login ke liye email use hoga
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"

class OneTimePassword(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True) # Check karein ye field maujood hai?

    def is_valid(self):
        # OTP sirf 10 minutes ke liye valid hai
        return timezone.now() < self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.email}"
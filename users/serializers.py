from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OneTimePassword
from django.core.mail import send_mail
from django.conf import settings
import random

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # 1. OTP Generate karna
        otp_code = str(random.randint(100000, 999999))
        OneTimePassword.objects.create(user=user, otp_code=otp_code)
        
        # 2. Email bhejna
        subject = "Verify your email - OTP Code"
        message = f"Hi {user.username}, your OTP code is {otp_code}. It is valid for 10 minutes."
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        send_mail(subject, message, email_from, recipient_list)
        
        return user
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
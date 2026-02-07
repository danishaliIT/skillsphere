import random
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status, views, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from .serializers import UserRegistrationSerializer
from .models import OneTimePassword

User = get_user_model()

# --- Helper Function for OTP ---
# Ye function code repeat hone se bachata hai
def send_otp_email(user):
    otp_code = str(random.randint(100000, 999999))
    # Purane OTPs remove karke naya create karna
    OneTimePassword.objects.filter(user=user).delete() 
    OneTimePassword.objects.create(user=user, otp_code=otp_code)
    
    send_mail(
        subject="SkillSphere Verification Code",
        message=f"Your OTP code is {otp_code}. It will expire soon.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

# --- Registration & OTP Verification ---

class RegisterView(views.APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_email(user) # Registration ke foran baad email jayegi
            return Response({
                "message": "User registered successfully. Please check your email for OTP."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(views.APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        try:
            user = User.objects.get(email=email)
            otp_obj = OneTimePassword.objects.get(user=user, otp_code=otp_code)

            if otp_obj.is_valid():
                user.is_verified = True
                user.save()
                otp_obj.delete()
                return Response({"message": "Account verified successfully!"}, status=status.HTTP_200_OK)
            
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        except (User.DoesNotExist, OneTimePassword.DoesNotExist):
            return Response({"error": "Invalid email or OTP code."}, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(views.APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response({"message": "This account is already verified."}, status=status.HTTP_400_BAD_REQUEST)
            
            send_otp_email(user)
            return Response({"message": "New OTP has been sent to your email."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email not found."}, status=status.HTTP_404_NOT_FOUND)

# --- Login Logic ---

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # User verification check
        if not self.user.is_verified:
            raise serializers.ValidationError("Your email is not verified. Please verify your OTP first.")
        
        # Frontend ke liye extra details
        data['role'] = getattr(self.user, 'role', 'user')
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# --- Password Reset Logic ---

class PasswordResetRequestView(views.APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            send_otp_email(user)
            return Response({"message": "Reset OTP sent to your email."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "No account found with this email."}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetConfirmView(views.APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email=email)
            otp_obj = OneTimePassword.objects.get(user=user, otp_code=otp_code)

            if otp_obj.is_valid():
                user.set_password(new_password)
                user.save()
                otp_obj.delete()
                return Response({"message": "Password reset successful!"}, status=status.HTTP_200_OK)
            
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        except (User.DoesNotExist, OneTimePassword.DoesNotExist):
            return Response({"error": "Invalid email or OTP code."}, status=status.HTTP_400_BAD_REQUEST)

# --- Social Auth ---

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:5173"
    client_class = OAuth2Client
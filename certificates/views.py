# G:\My Projects\certificates\views.py

from rest_framework import generics, permissions
from .models import Certificate
from .serializers import CertificateSerializer

# 1. Tamam certificates ki list dekhne ke liye
class StudentCertificateListView(generics.ListAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Sirf logged-in student ke apne certificates filter karein
        return Certificate.objects.filter(
            progress__enrollment__student=self.request.user.student_profile
        )

# 2. Kisi aik certificate ki detail dekhne ke liye
class CertificateDetailView(generics.RetrieveAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
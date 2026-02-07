from django.urls import path
from .views import StudentCertificateListView, CertificateDetailView

urlpatterns = [
    # Student ke apne tamam certificates dekhne ke liye
    path('my-certificates/', StudentCertificateListView.as_view(), name='my-certificates'),
    
    # Kisi aik certificate ki detail (PDF link/Number) dekhne ke liye
    path('<int:pk>/', CertificateDetailView.as_view(), name='certificate-detail'),
]
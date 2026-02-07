import uuid
from django.db import models
from enrollments.models import TrackProgress

class Certificate(models.Model):
    # Schema: progress_id (1:1)
    progress = models.OneToOneField(TrackProgress, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(max_length=50, unique=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField(max_length=500, blank=True) # PDF ya Image link

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Unique certificate number generate karna (e.g., CERT-12345)
            self.certificate_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificate for {self.progress.enrollment.student.user.username}"
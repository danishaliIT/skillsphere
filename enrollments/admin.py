from django.contrib import admin
from .models import EnrollmentCourse, TrackProgress, Payment

admin.site.register(EnrollmentCourse)
admin.site.register(TrackProgress)
admin.site.register(Payment)
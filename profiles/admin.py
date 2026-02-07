from django.contrib import admin
from .models import StudentProfile, InstructorProfile, CompanyProfile

admin.site.register(StudentProfile)
admin.site.register(InstructorProfile)
admin.site.register(CompanyProfile)
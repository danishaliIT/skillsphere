from django.db import models
from django.conf import settings


class StudentAddress(models.Model):
    profile = models.OneToOneField('StudentProfile', on_delete=models.CASCADE, related_name='address')
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Pakistan')
    zip_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.city}, {self.country}"

# --- EDUCATION TABLE (One-to-Many) ---
# Student ke multiple records ho sakte hain (Matric, Inter, BS)
class StudentEducation(models.Model):
    profile = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, related_name='education_history')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255) # e.g. "Junior Executive (Data Entry Operator)"
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    grade_or_score = models.CharField(max_length=50, blank=True) # e.g. "32.2/60"

    class Meta:
        ordering = ['-end_date']

# --- SOCIAL PROFILES TABLE ---
class StudentSocial(models.Model):
    profile = models.OneToOneField('StudentProfile', on_delete=models.CASCADE, related_name='socials')
    linkedin = models.URLField(max_length=500, blank=True)
    github = models.URLField(max_length=500, blank=True) # For MERN/AI projects
    portfolio = models.URLField(max_length=500, blank=True)
    twitter = models.URLField(max_length=500, blank=True)

# --- MAIN STUDENT PROFILE (The Hub) ---
class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True) # e.g. "Interested in Military Technology & AI"
    profile_picture = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    experience = models.TextField(blank=True)
    public_profile = models.BooleanField(default=False, help_text='If true, profile is publicly viewable by username')

    def __str__(self):
        return f"Profile: {self.user.email}"

class InstructorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instructor_profile')
    full_name = models.CharField(max_length=200, blank=True)
    expertise = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    bio = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    # Extra fields added for public profiles and contact
    profile_picture = models.ImageField(upload_to='instructor_photos/', null=True, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    linkedin = models.URLField(max_length=500, blank=True)
    website = models.URLField(max_length=500, blank=True)
    skills = models.TextField(blank=True, help_text='Comma separated skills')
    public_profile = models.BooleanField(default=False, help_text='If true, instructor profile is publicly viewable by username')
    # Bank details
    bank_name = models.CharField(max_length=200, blank=True)
    bank_account_number = models.CharField(max_length=100, blank=True)
    bank_iban = models.CharField(max_length=100, blank=True)
    bank_swift = models.CharField(max_length=100, blank=True)


class InstructorEducation(models.Model):
    profile = models.ForeignKey('InstructorProfile', on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-end_date']


class InstructorEmployment(models.Model):
    profile = models.ForeignKey('InstructorProfile', on_delete=models.CASCADE, related_name='employment')
    company = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']


class InstructorCertificate(models.Model):
    profile = models.ForeignKey('InstructorProfile', on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255, blank=True)
    issued_date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='instructor_certificates/', null=True, blank=True)


class InstructorSocial(models.Model):
    profile = models.OneToOneField('InstructorProfile', on_delete=models.CASCADE, related_name='socials')
    linkedin = models.URLField(max_length=500, blank=True)
    twitter = models.URLField(max_length=500, blank=True)
    github = models.URLField(max_length=500, blank=True)
    website = models.URLField(max_length=500, blank=True)


class InstructorAddress(models.Model):
    profile = models.OneToOneField('InstructorProfile', on_delete=models.CASCADE, related_name='address')
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='')
    zip_code = models.CharField(max_length=20, blank=True)

class CompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    website_url = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
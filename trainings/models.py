from django.db import models
from profiles.models import CompanyProfile, StudentProfile

class TrainingProgram(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('soft_skills', 'Soft Skills'),
        ('management', 'Management'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('completed', 'Completed'),
    ]

    # Schema: company_id
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='programs')
    program_name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Live Training Details
    live_link = models.URLField(blank=True, null=True, help_text="Join link for live training session (e.g., Zoom, Google Meet, Teams)")
    live_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    scheduled_date = models.DateTimeField(blank=True, null=True, help_text="When the training is scheduled")
    duration_hours = models.IntegerField(default=2, help_text="Training duration in hours")
    
    # Additional Details
    instructor_name = models.CharField(max_length=255, blank=True, help_text="Name of the training instructor")
    instructor_email = models.EmailField(blank=True, help_text="Instructor contact email")
    max_participants = models.IntegerField(default=100, help_text="Maximum number of participants")
    prerequisites = models.TextField(blank=True, help_text="Prerequisites or requirements")
    
    # Recording & Resources
    recording_link = models.URLField(blank=True, null=True, help_text="Link to training session recording")
    resource_link = models.URLField(blank=True, null=True, help_text="Link to training materials/documents")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.program_name} - {self.get_live_status_display()}"

class EnrollmentTraining(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='training_enrollments')
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completion_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        unique_together = ('student', 'program')

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.program.program_name}"
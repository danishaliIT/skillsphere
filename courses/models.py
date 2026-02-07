from django.db import models
from django.conf import settings
from django.utils.text import slugify
from profiles.models import InstructorProfile

class Course(models.Model):
    CATEGORY_CHOICES = [
        ('Military Tech', 'Military Technology'), #
        ('AI & Robotics', 'AI & Robotics'), #
        ('Web Dev', 'Web Development (MERN)'), #
        ('NLP', 'Natural Language Processing'), #
        ('Finance', 'Finance Stories'), #
    ]
    
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='led_courses')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True) # Identifying courses via slug
    description = models.TextField()
    thumbnail = models.ImageField(
    upload_to='course_thumbnails/', 
    null=True,   # Purane courses ke liye null allow karega
    blank=True   # Form mein isey optional rakhega
)
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        default='Web Dev' # Yeh line purane data ko crash hone se bachayegi
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    # Controlled publishing workflow
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_courses')
    approval_notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) # Auto-generate slug from title
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- MONTHS / SECTIONS ---
class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255) # e.g., "Month 1: Fundamentals"
    order = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    # allow an optional cover file (image/pdf) or multiple via separate asset model

    class Meta:
        ordering = ['order']

# --- WEEKS / SUB-SECTIONS ---
class CourseSubModule(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='weeks')
    title = models.CharField(max_length=255) # e.g., "Week 1: Introduction to Drones"
    order = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

class Lesson(models.Model):
    CONTENT_TYPES = [
        ('Video', 'Video Lesson'),
        ('Image', 'Infographic/Image'),
        ('Text', 'Article/Description'),
        ('Quiz', 'Assessment'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]
    
    QUIZ_TYPES = [
        ('Multiple Choice', 'Multiple Choice'),
        ('Short Answer', 'Short Answer'),
        ('Essay', 'Essay'),
        ('Mixed', 'Mixed'),
    ]
    
    week = models.ForeignKey(CourseSubModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255) # e.g., "Day 1: Setup MERN Stack"
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    order = models.PositiveIntegerField()
    
    # --- VIDEO LESSON FIELDS ---
    video_url = models.URLField(blank=True, null=True) 
    duration = models.IntegerField(blank=True, null=True, help_text="Duration in minutes")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Beginner', blank=True)
    
    # --- QUIZ LESSON FIELDS ---
    total_questions = models.IntegerField(blank=True, null=True)
    passing_score = models.IntegerField(blank=True, null=True, help_text="Passing percentage")
    quiz_instructions = models.TextField(blank=True)
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES, default='Multiple Choice', blank=True)
    
    # --- TEXT LESSON FIELDS ---
    text_content = models.TextField(blank=True)
    resource_link = models.URLField(blank=True, null=True)
    
    # --- GENERAL FIELDS ---
    description = models.TextField(blank=True)
    content_file = models.FileField(upload_to='lesson_content/', blank=True, null=True)
    # additional rich content handled by Topic/SubTopic and LessonAsset models

    class Meta:
        ordering = ['order']

# --- QUIZ & REVIEW SYSTEMS ---
class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    total_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=50)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1) 

class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5) 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class CourseInstructor(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='co_instructors')
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, default='Assistant') 
    added_by_id = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('course', 'instructor')


# Assets for modules (multiple images/pdfs/videos per module)
class ModuleAsset(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to='course_module_assets/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


# Assets for weeks/submodules
class SubModuleAsset(models.Model):
    submodule = models.ForeignKey(CourseSubModule, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to='course_week_assets/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


# Assets for lessons/days
class LessonAsset(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assets')
    file = models.FileField(upload_to='lesson_assets/')
    file_type = models.CharField(max_length=50, blank=True, help_text='image/pdf/video')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


# Topics within a lesson (each topic can have multiple subtopics)
class Topic(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


# SubTopic under Topic, can have its own file/video/embed
class SubTopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopics')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True, null=True)
    resource_file = models.FileField(upload_to='subtopic_resources/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
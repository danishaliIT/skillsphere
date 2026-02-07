from django.contrib import admin
from .models import (
    Course, CourseModule, CourseSubModule, 
    Lesson, Quiz, Question, Review, CourseInstructor
)

# ==========================================
# 1. INLINES (Hierarchy setup)
# ==========================================

class QuestionInline(admin.TabularInline):
    """Quiz ke andar questions add karne ke liye"""
    model = Question
    extra = 1

class LessonInline(admin.StackedInline): 
    """Week ke andar Lessons add karne ke liye (Bada form)"""
    model = Lesson
    extra = 0
    # Fields ko organize kiya hai taake URL aur Description mix na hon
    fields = [
        ('title', 'order'), 
        ('content_type', 'difficulty'),
        'video_url',       # <-- Yahan sirf Link ayega
        'description',     # <-- Yahan lamba Text ayega
        'content_file',
        'resource_link'
    ]

class WeekInline(admin.TabularInline):
    """Module ke andar Weeks (SubModules) add karne ke liye"""
    model = CourseSubModule
    extra = 0
    show_change_link = True # Edit button dikhaye ga

class ModuleInline(admin.TabularInline):
    """Course ke andar Modules add karne ke liye"""
    model = CourseModule
    extra = 0
    show_change_link = True

# ==========================================
# 2. MAIN ADMIN VIEWS
# ==========================================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'status', 'category', 'price')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)} 
    inlines = [ModuleInline] # Course kholne par neechay Modules dikhenge

@admin.register(CourseModule)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title',)
    inlines = [WeekInline] # Module kholne par neechay Weeks dikhenge

@admin.register(CourseSubModule)
class WeekAdmin(admin.ModelAdmin):
    # Is model ko humne 'Week' kaha hai (models mein CourseSubModule hai)
    list_display = ('title', 'module', 'order')
    list_filter = ('module',)
    search_fields = ('title',)
    inlines = [LessonInline] # Week kholne par neechay Lessons dikhenge (Bada form)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'total_marks', 'passing_marks')
    inlines = [QuestionInline]

# ==========================================
# 3. OTHER REGISTRATIONS
# ==========================================

admin.site.register(Review)
admin.site.register(CourseInstructor)
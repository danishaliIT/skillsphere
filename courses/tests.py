from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, 
    LessonDetailView, 
    InstructorCourseListView, 
    CourseCatalogView
)

# Router humare endpoints ko organize rakhta hai
router = DefaultRouter()
router.register(r'catalog', CourseViewSet, basename='course-catalog')

urlpatterns = [
    # 1. Main Catalog & Detail (Identifying via SLUG)
    # Example: /api/courses/catalog/military-drone-tech/
    path('', include(router.urls)),

    # 2. Specific Lesson Content (Video/Quiz Detail)
    # Example: /api/courses/lessons/45/
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),

    # 3. Instructor Dashboard
    # Example: Sirf Danish Ali ke banaye huye courses
    path('my-workspace/', InstructorCourseListView.as_view(), name='instructor-courses'),

    # 4. Specialized Search (For Military Tech, AI, NLP)
    path('search/', CourseCatalogView.as_view(), name='course-search'),
]
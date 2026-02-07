from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, LessonDetailView, InstructorWorkspaceView, CourseDetailManagerView,
    CreateFullCourseView, CoursePlayerViewSet,
    ModuleAssetListCreateView, ModuleAssetDetailView, SubModuleAssetListCreateView,
    LessonAssetListCreateView, TopicListCreateView, TopicDetailView,
    SubTopicListCreateView, SubTopicDetailView
    , InstructorSubmitCourseView, AdminPendingCoursesView, AdminApproveCourseView, QuizAttemptView
      )

# Router automatic endpoints (GET, POST, etc.) generate karta hai
router = DefaultRouter()

# Catalog endpoint: /api/courses/
# Detail endpoint: /api/courses/<slug>/
router.register(r'', CourseViewSet, basename='course')

urlpatterns = [
    # 1. Create Full Course: Instructor ke liye course create karna
    path('create-full-course/', CreateFullCourseView.as_view(), name='create-full-course'),
    
    # 2. Instructor Workspace: Sirf apne banaye huye courses dekhne ke liye
    path('my-workspace/', InstructorWorkspaceView.as_view(), name='instructor-workspace'),
    
    # 3. Lesson Detail: Video ya Quiz content fetch karne ke liye
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('lesson/<int:lesson_id>/quiz/', QuizAttemptView.as_view(), name='attempt-quiz'),
    # Assets and content management
    path('modules/<int:module_id>/assets/', ModuleAssetListCreateView.as_view(), name='module-assets-create'),
    path('modules/assets/<int:pk>/', ModuleAssetDetailView.as_view(), name='module-asset-detail'),
    path('weeks/<int:submodule_id>/assets/', SubModuleAssetListCreateView.as_view(), name='week-assets-create'),
    path('lessons/<int:lesson_id>/assets/', LessonAssetListCreateView.as_view(), name='lesson-assets-create'),
    path('lessons/<int:lesson_id>/topics/', TopicListCreateView.as_view(), name='lesson-topics-create'),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic-detail'),
    path('topics/<int:topic_id>/subtopics/', SubTopicListCreateView.as_view(), name='topic-subtopics-create'),
    path('subtopics/<int:pk>/', SubTopicDetailView.as_view(), name='subtopic-detail'),
    # Submission / Approval
    path('my-workspace/submit/<str:slug>/', InstructorSubmitCourseView.as_view(), name='instructor-submit-course'),
    path('admin/pending-courses/', AdminPendingCoursesView.as_view(), name='admin-pending-courses'),
    path('admin/courses/<str:slug>/review/', AdminApproveCourseView.as_view(), name='admin-approve-course'),
    # 4. Router logic (Catalog aur Slug-based detail handle karega) - MUST BE LAST
    path('', include(router.urls)),
]
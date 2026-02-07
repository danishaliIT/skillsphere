from rest_framework import viewsets, generics, status, permissions, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import json

from .models import (
    Course, Lesson, CourseInstructor, CourseModule, 
    CourseSubModule, Quiz, Question, ModuleAsset, 
    SubModuleAsset, LessonAsset, Topic, SubTopic
)
from .serializers import (
    CourseSerializer, LessonSerializer, QuizDetailSerializer, 
    QuizResultSerializer, ModuleAssetSerializer, SubModuleAssetSerializer, 
    LessonAssetSerializer, TopicSerializer, SubTopicSerializer
)
from .permissions import IsInstructor

# ==========================================
# 1. PUBLIC CATALOG & PLAYER
# ==========================================

class CourseViewSet(viewsets.ModelViewSet): 
    """
    Identifying courses via SLUG. Handles List, Retrieve, and Partial Updates.
    """
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser, JSONParser) 

    def get_queryset(self):
        return Course.objects.all().prefetch_related('modules__weeks__lessons')

    def update(self, request, *args, **kwargs):
        """
        Custom update to handle JSON stringified modules from FormData.
        """
        course = self.get_object()
        data = request.data.copy()

        if 'modules' in data and isinstance(data['modules'], str):
            try:
                data['modules'] = json.loads(data['modules'])
            except ValueError:
                return Response({"error": "Invalid JSON in modules data"}, status=400)

        serializer = self.get_serializer(course, data=data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CoursePlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Detailed curriculum fetcher for students.
    """
    queryset = Course.objects.all().prefetch_related('modules__weeks__lessons')
    serializer_class = CourseSerializer
    lookup_field = 'slug' 
    permission_classes = [IsAuthenticatedOrReadOnly]

# ==========================================
# 2. INSTRUCTOR WORKSPACE & CREATION
# ==========================================

class CreateFullCourseView(generics.CreateAPIView):
    """
    The main deployment engine for deep nested course data.
    """
    serializer_class = CourseSerializer
    permission_classes = [IsInstructor]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if 'modules' in data and isinstance(data['modules'], str):
            try:
                data['modules'] = json.loads(data['modules'])
            except ValueError:
                return Response({"error": "Curriculum data is not valid JSON."}, status=400)

        serializer = self.get_serializer(data=data, context={'request': request})
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "message": "Course deployed successfully to SkillSphere! 🚀",
                "course": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InstructorWorkspaceView(generics.ListAPIView):
    """
    Returns list of courses owned by the authenticated instructor.
    """
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(instructor__user=self.request.user)

# ==========================================
# 3. QUIZ & LESSON INTERACTION
# ==========================================

class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

class QuizAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        try:
            quiz = lesson.quiz
        except Quiz.DoesNotExist:
            return Response({"error": "No quiz found for this lesson"}, status=404)
        serializer = QuizDetailSerializer(quiz)
        return Response(serializer.data)

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        try:
            quiz = lesson.quiz
        except Quiz.DoesNotExist:
            return Response({"error": "No quiz found"}, status=404)

        user_answers = request.data.get('answers', {})
        if not user_answers:
            return Response({"error": "No answers provided"}, status=400)

        total_questions = quiz.questions.count()
        correct_count = sum(
            1 for q in quiz.questions.all()
            if user_answers.get(str(q.id), '').upper() == q.correct_option.upper()
        )

        score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        is_passed = score_percentage >= quiz.passing_marks

        return Response({
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "score_percentage": round(score_percentage, 2),
            "passed": is_passed,
            "message": "Mission Successful! You Passed." if is_passed else "Mission Failed. Try Again."
        })

# ==========================================
# 4. ASSET & CONTENT MANAGEMENT (CRUD)
# ==========================================

class ModuleAssetListCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, module_id=None):
        module = get_object_or_404(CourseModule, pk=module_id)
        if module.course.instructor.user != request.user:
            return Response({"detail": "Permission denied."}, status=403)
        serializer = ModuleAssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(module=module)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TopicListCreateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id=None):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        if lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Permission denied."}, status=403)
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lesson=lesson)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class TopicDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        if topic.lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Permission denied."}, status=403)
        serializer = TopicSerializer(topic, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        if topic.lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Permission denied."}, status=403)
        topic.delete()
        return Response(status=204)

# ==========================================
# 5. WORKFLOW (Submission & Admin Approval)
# ==========================================

class InstructorSubmitCourseView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug=None):
        course = get_object_or_404(Course, slug=slug)
        if course.instructor.user != request.user:
            return Response({"detail": "Not authorized."}, status=403)
        course.status = 'pending'
        course.approval_notes = request.data.get('notes', '')
        course.save()
        return Response({'message': 'Course submitted for review'})

class AdminPendingCoursesView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Course.objects.filter(status='pending').prefetch_related('modules__weeks__lessons')
        serializer = CourseSerializer(qs, many=True)
        return Response(serializer.data)

class AdminApproveCourseView(views.APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, slug=None):
        course = get_object_or_404(Course, slug=slug)
        action = request.data.get('action', 'approve')
        notes = request.data.get('notes', '')
        
        if action == 'approve':
            course.status = 'published'
            course.published_at = timezone.now()
            course.approved_by = request.user
        elif action == 'reject':
            course.status = 'rejected'
        else:
            return Response({'error': 'Invalid action'}, status=400)
            
        course.approval_notes = notes
        course.save()
        return Response({'message': f'Course {action}ed successfully'})

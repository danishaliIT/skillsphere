from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .models import Course, Lesson, CourseInstructor
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .permissions import IsInstructor # Sirf instructors ke liye custom permission

# 1. PUBLIC CATALOG: Identifying courses via SLUG
class CourseViewSet(viewsets.ModelViewSet): 
    """
    Ab yeh Create, Update, Delete sab handle karega.
    """
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    # FormData handle karne ke liye parsers add karein
    parser_classes = (MultiPartParser, FormParser, JSONParser) 

    def get_queryset(self):
        qs = Course.objects.all().prefetch_related('modules__weeks__lessons')
        return qs

    # 2. UPDATE Method Override (Crucial Fix for 500 Error)
    def update(self, request, *args, **kwargs):
        course = self.get_object()
        
        # Data ki copy banayein taake edit kar sakein
        data = request.data.copy()

        # Agar 'modules' string format mein aaya hai (FormData se), toh JSON banao
        if 'modules' in data and isinstance(data['modules'], str):
            try:
                data['modules'] = json.loads(data['modules'])
            except ValueError:
                return Response({"error": "Invalid JSON in modules"}, status=400)

        # Serializer ko clean data pass karein
        serializer = self.get_serializer(course, data=data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# courses/views.py
# courses/views.py (Add this below your existing code)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Lesson, Quiz, Question
from .serializers import QuizDetailSerializer, QuizResultSerializer

class QuizAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    # 1. Quiz Fetch karna (GET)
    def get(self, request, lesson_id):
        # Lesson dhoondo
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Check karo is lesson ki quiz hai ya nahi
        try:
            quiz = lesson.quiz  # OneToOne field access
        except Quiz.DoesNotExist:
            return Response({"error": "No quiz found for this lesson"}, status=404)

        serializer = QuizDetailSerializer(quiz)
        return Response(serializer.data)

    # 2. Quiz Submit karna & Result Calculation (POST)
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        try:
            quiz = lesson.quiz
        except Quiz.DoesNotExist:
            return Response({"error": "No quiz found"}, status=404)

        # User ke answers (Format: { "question_id": "A", "question_id": "B" })
        user_answers = request.data.get('answers', {})

        if not user_answers:
            return Response({"error": "No answers provided"}, status=400)

        total_questions = quiz.questions.count()
        correct_count = 0

        # Loop through actual questions to check answers
        for question in quiz.questions.all():
            # User ne kya select kiya (question ID ko string mein convert karke check karo)
            selected_option = user_answers.get(str(question.id))
            
            # Match karo DB ke correct option se
            if selected_option and selected_option.upper() == question.correct_option.upper():
                correct_count += 1

        # Calculate Score
        score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        is_passed = score_percentage >= quiz.passing_marks

        # Response Data
        return Response({
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "score_percentage": round(score_percentage, 2),
            "passed": is_passed,
            "message": "Congratulations! You Passed." if is_passed else "You Failed. Try Again."
        }, status=status.HTTP_200_OK)


class CourseCreateView(generics.CreateAPIView):
    """
    Endpoint: /api/courses/create/
    Sirf authenticated Instructors naya course bana sakte hain
    """
    serializer_class = CourseSerializer
    permission_classes = [IsInstructor]

    def perform_create(self, serializer):
        # Course banane wale ko automatically 'Lead Instructor' set karna
        course = serializer.save(instructor=self.request.user.instructor_profile)
        
        # CourseInstructor table mein record create karna (Multiple instructor support ke liye)
        CourseInstructor.objects.create(
            course=course, 
            instructor=self.request.user.instructor_profile,
            role='Lead Instructor'
        )

class InstructorWorkspaceView(generics.ListAPIView):
    """
    Danish Ali ke apne banaye huye courses ki list
    """
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter: Sirf current instructor ke courses dikhana
        return Course.objects.filter(instructor__user=self.request.user)

# 3. MANAGEMENT: Specific Course Retrieve, Update, Delete
class CourseDetailManagerView(generics.RetrieveUpdateDestroyAPIView):
    """
    Specific course ko edit ya delete karne ke liye (via SLUG)
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    permission_classes = [IsInstructor] # Baad mein hum owner check lagayenge

# 4. CONTENT PLAYER: Lesson Detail
class LessonDetailView(generics.RetrieveAPIView):
    """
    Makhsoos Lesson (Day) ka video ya quiz data fetch karna
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

class CoursePlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DragonTech Intelligence Engine:
    Slug ke zariye poora curriculum fetch karna.
    """
    # prefetch_related use karne se speed barh jati hai
    queryset = Course.objects.all().prefetch_related('modules__weeks__lessons')
    serializer_class = CourseSerializer
    lookup_field = 'slug' 
    permission_classes = [IsAuthenticatedOrReadOnly]
import json
from django.db import transaction
from rest_framework import views, status, permissions
from rest_framework.response import Response
from .models import Course, CourseModule, CourseSubModule, Lesson
from profiles.models import InstructorProfile
from .models import ModuleAsset, SubModuleAsset, LessonAsset, Topic, SubTopic
from .serializers import (
    ModuleAssetSerializer, SubModuleAssetSerializer, LessonAssetSerializer,
    TopicSerializer, SubTopicSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from django.utils import timezone

class CreateFullCourseView(generics.CreateAPIView):
    """
    SkillSphere Deep Deployment View:
    Handling nested Modules, Weeks, Lessons and Cloudinary file uploads.
    """
    serializer_class = CourseSerializer
    permission_classes = [IsInstructor]
    parser_classes = (MultiPartParser, FormParser) # Multipart lazmi hai images/videos ke liye

    def create(self, request, *args, **kwargs):
        # 1. Request data ki copy banayein taake modifications kar sakein
        data = request.data.copy()

        # 2. Frontend se aaya hua 'modules' JSON string hai, isay Python list mein badlein
        if 'modules' in data and isinstance(data['modules'], str):
            try:
                data['modules'] = json.loads(data['modules'])
            except ValueError:
                return Response(
                    {"error": "Curriculum data format is invalid. Ensure it is valid JSON."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 3. Serializer initialize karein (Context ke sath taake Instructor profile attach ho)
        serializer = self.get_serializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            # 4. Data database mein save karein
            self.perform_create(serializer)
            
            # 5. Success response bhejein
            return Response(
                {
                    "message": "Course deployed successfully to SkillSphere!",
                    "course": serializer.data
                }, 
                status=status.HTTP_201_CREATED
            )
        
        # 6. Agar validation fail ho (e.g. missing order or title), toh debug print karein
        print("--- DEPLOYMENT ERROR LOG ---")
        print(serializer.errors) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Instructor profile serializer ke create method mein handle ho rahi hai
        serializer.save()


# ----- Asset and Topic APIs -----
class ModuleAssetListCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, module_id=None):
        module = get_object_or_404(CourseModule, pk=module_id)
        # ownership check
        if module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ModuleAssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(module=module)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModuleAssetDetailView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def delete(self, request, pk):
        asset = get_object_or_404(ModuleAsset, pk=pk)
        if asset.module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubModuleAssetListCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, submodule_id=None):
        sub = get_object_or_404(CourseSubModule, pk=submodule_id)
        if sub.module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubModuleAssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(submodule=sub)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LessonAssetListCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, lesson_id=None):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        if lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = LessonAssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lesson=lesson)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopicListCreateView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id=None):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        if lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(lesson=lesson)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopicDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        if topic.lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TopicSerializer(topic, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        if topic.lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        topic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubTopicListCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, topic_id=None):
        topic = get_object_or_404(Topic, pk=topic_id)
        if topic.lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubTopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(topic=topic)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTopicDetailView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        st = get_object_or_404(SubTopic, pk=pk)
        if st.topic.lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubTopicSerializer(st, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        st = get_object_or_404(SubTopic, pk=pk)
        if st.topic.lesson.week.module.course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        st.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ----- Instructor submit / Admin approval endpoints -----
class InstructorSubmitCourseView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug=None):
        course = get_object_or_404(Course, slug=slug)
        # only owner can submit
        if course.instructor.user != request.user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        course.status = 'pending'
        course.approval_notes = request.data.get('notes', '')
        course.save()
        return Response({'message': 'Course submitted for review'}, status=status.HTTP_200_OK)


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
            course.approval_notes = notes
            course.save()
            return Response({'message': 'Course published'}, status=status.HTTP_200_OK)
        elif action == 'reject':
            course.status = 'rejected'
            course.approval_notes = notes
            course.save()
            return Response({'message': 'Course rejected'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import serializers
from .models import (
    Course, CourseModule, CourseSubModule, 
    Lesson, Quiz, Question, Review, CourseInstructor,
    ModuleAsset, SubModuleAsset, LessonAsset, Topic, SubTopic
)

# ==========================================
# 1. BOTTOM LAYER (Assets, Topics, Quizzes)
#    (Inko sabse upar hona chahiye taake Lesson inko use kar sake)
# ==========================================

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['id', 'total_marks', 'passing_marks', 'questions']
# courses/serializers.py

from rest_framework import serializers
from .models import Quiz, Question

# 1. Questions dikhane ke liye (Without Answer Key)
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'option_a', 'option_b', 'option_c', 'option_d']
        # Note: 'correct_option' yahan mat daalna warna cheating ho jayegi!

# 2. Quiz Detail Serializer
class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'total_marks', 'passing_marks', 'questions']

# 3. Result Dikhane ke liye
class QuizResultSerializer(serializers.Serializer):
    total_questions = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    score_percentage = serializers.FloatField()
    passed = serializers.BooleanField()
    message = serializers.CharField()

class LessonAssetSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)
    class Meta:
        model = LessonAsset
        fields = ['id', 'lesson', 'file', 'file_type', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class SubTopicSerializer(serializers.ModelSerializer):
    resource_file = serializers.FileField(required=False, allow_null=True)
    class Meta:
        model = SubTopic
        fields = ['id', 'topic', 'title', 'description', 'video_url', 'resource_file', 'order']
        read_only_fields = ['id']

class TopicSerializer(serializers.ModelSerializer):
    subtopics = SubTopicSerializer(many=True, read_only=True)
    class Meta:
        model = Topic
        fields = ['id', 'lesson', 'title', 'description', 'order', 'subtopics']
        read_only_fields = ['id']

class ModuleAssetSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)
    class Meta:
        model = ModuleAsset
        fields = ['id', 'module', 'file', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class SubModuleAssetSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)
    class Meta:
        model = SubModuleAsset
        fields = ['id', 'submodule', 'file', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'comment', 'created_at']

class CourseInstructorSerializer(serializers.ModelSerializer):
    instructor_name = serializers.ReadOnlyField(source='instructor.full_name')
    instructor_photo = serializers.ReadOnlyField(source='instructor.profile_picture_url')
    class Meta:
        model = CourseInstructor
        fields = ['instructor_name', 'instructor_photo', 'role']


# ==========================================
# 2. CONTENT LAYER (Lesson)
# ==========================================

class LessonSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    assets = LessonAssetSerializer(many=True, read_only=True) # Ab yeh upar define hai, error nahi dega
    topics = TopicSerializer(many=True, read_only=True)       # Yeh bhi upar define hai

    # Frontend se temporary keys aayengi file handling ke liye
    temp_video_key = serializers.CharField(write_only=True, required=False, allow_null=True)
    temp_doc_key = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content_type', 'description', 'order',
            'video_url', 'duration', 'difficulty',
            'total_questions', 'passing_score', 'quiz_instructions', 'quiz_type',
            'text_content', 'resource_link',
            'quiz', 'assets', 'topics',
            'temp_video_key', 'temp_doc_key'
        ]

# ==========================================
# 3. SUB-MODULE LAYER (Weeks)
# ==========================================

class WeekSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True) # Uses LessonSerializer defined above
    assets = SubModuleAssetSerializer(many=True, read_only=True)

    class Meta:
        model = CourseSubModule
        fields = ['id', 'title', 'order', 'lessons', 'assets']

# ==========================================
# 4. MODULE LAYER (Modules)
# ==========================================

# Maine iska naam 'MonthSerializer' se change karke 'ModuleSerializer' kar diya hai
# taake CourseSerializer isay pehchan sake.
class ModuleSerializer(serializers.ModelSerializer):
    weeks = WeekSerializer(many=True, read_only=True) # Uses WeekSerializer defined above
    assets = ModuleAssetSerializer(many=True, read_only=True)

    class Meta:
        model = CourseModule
        fields = ['id', 'title', 'order', 'description', 'weeks', 'assets']

# ==========================================
# 5. MAIN COURSE LAYER
# ==========================================

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, required=False)
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'instructor']

    # --- CREATE LOGIC (Fixed for Files) ---
    def create(self, validated_data):
        modules_data = validated_data.pop('modules', [])
        request = self.context.get('request')
        
        if request and hasattr(request.user, 'instructor_profile'):
            validated_data['instructor'] = request.user.instructor_profile

        course = Course.objects.create(**validated_data)

        for module_data in modules_data:
            weeks_data = module_data.pop('weeks', [])
            module = CourseModule.objects.create(course=course, **module_data)

            for week_data in weeks_data:
                lessons_data = week_data.pop('lessons', [])
                week = CourseSubModule.objects.create(module=module, **week_data)

                for lesson_data in lessons_data:
                    # File handling keys ko remove karein
                    video_key = lesson_data.pop('temp_video_key', None)
                    lesson_data.pop('temp_doc_key', None)
                    
                    lesson = Lesson.objects.create(week=week, **lesson_data)
                    
                    # Agar request mein video file hai toh attach karein
                    if video_key and request.FILES.get(video_key):
                        lesson.content_file = request.FILES[video_key]
                        lesson.save()
        
        return course

    # --- UPDATE LOGIC (Updated for Quick Save & Nested Modules) ---
    def update(self, instance, validated_data):
        modules_data = validated_data.pop('modules', None)
        request = self.context.get('request')

        # 1. Basic Fields Update
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.category = validated_data.get('category', instance.category)
        if validated_data.get('thumbnail'):
            instance.thumbnail = validated_data.get('thumbnail')
        instance.save()

        # 2. Nested Modules Logic (Quick Save support)
        if modules_data is not None:
            for m_data in modules_data:
                weeks_data = m_data.pop('weeks', [])
                module_id = m_data.get('id')

                if module_id:
                    # Purane module ko update karein
                    module_inst = CourseModule.objects.get(id=module_id, course=instance)
                    module_inst.title = m_data.get('title', module_inst.title)
                    module_inst.order = m_data.get('order', module_inst.order)
                    module_inst.save()
                else:
                    # Naya module create karein
                    module_inst = CourseModule.objects.create(course=instance, **m_data)

                # 3. Nested Weeks Logic
                for w_data in weeks_data:
                    lessons_data = w_data.pop('lessons', [])
                    week_id = w_data.get('id')

                    if week_id:
                        week_inst = CourseSubModule.objects.get(id=week_id, module=module_inst)
                        week_inst.title = w_data.get('title', week_inst.title)
                        week_inst.order = w_data.get('order', week_inst.order)
                        week_inst.save()
                    else:
                        week_inst = CourseSubModule.objects.create(module=module_inst, **w_data)

                    # 4. Nested Lessons Logic
                    for l_data in lessons_data:
                        lesson_id = l_data.get('id')
                        video_key = l_data.pop('temp_video_key', None)
                        l_data.pop('temp_doc_key', None)

                        if lesson_id:
                            lesson_inst = Lesson.objects.get(id=lesson_id, week=week_inst)
                            for attr, value in l_data.items():
                                setattr(lesson_inst, attr, value)
                            lesson_inst.save()
                        else:
                            lesson_inst = Lesson.objects.create(week=week_inst, **l_data)

                        # File Update Logic
                        if video_key and request.FILES.get(video_key):
                            lesson_inst.content_file = request.FILES[video_key]
                            lesson_inst.save()

        return instance

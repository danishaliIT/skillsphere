from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import TrainingProgram, EnrollmentTraining
from .serializers import TrainingProgramSerializer, EnrollmentTrainingSerializer

class TrainingProgramListCreateView(generics.ListCreateAPIView):
    queryset = TrainingProgram.objects.all()
    serializer_class = TrainingProgramSerializer
    
    def get_permissions(self):
        """Allow anyone to list, but only authenticated users can create"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Filter by live status if requested"""
        queryset = super().get_queryset()
        live_status = self.request.query_params.get('live_status')
        if live_status:
            queryset = queryset.filter(live_status=live_status)
        return queryset.order_by('-scheduled_date')

    def perform_create(self, serializer):
        # Check karein ke user Company hai ya nahi
        if self.request.user.role != 'Company':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only companies can create training programs.")
            
        # Automatic company profile attach karein
        serializer.save(company=self.request.user.company_profile)

class TrainingProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrainingProgram.objects.all()
    serializer_class = TrainingProgramSerializer
    
    def get_permissions(self):
        """Allow anyone to retrieve, but only authenticated users can update/delete"""
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_update(self, serializer):
        # Only company can update their training
        if serializer.instance.company.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update your own trainings.")
        serializer.save()

class EnrollInTrainingView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentTrainingSerializer

    def post(self, request, program_id):
        if request.user.role != 'Student':
            return Response({"error": "Only students can join trainings."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            program = TrainingProgram.objects.get(id=program_id)
        except TrainingProgram.DoesNotExist:
            return Response({"error": "Training not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if max capacity reached
        if program.enrolled_students.count() >= program.max_participants:
            return Response({"error": "Training is full."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Junction table mein entry
        enrollment, created = EnrollmentTraining.objects.get_or_create(
            student=request.user.student_profile,
            program=program
        )
        if not created:
            return Response({"message": "Already enrolled."}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            "message": "Joined training successfully!",
            "live_link": program.live_link,
            "scheduled_date": program.scheduled_date
        }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_training_enrollments(request):
    """Get all trainings student is enrolled in"""
    if request.user.role != 'Student':
        return Response({"error": "Only students can view enrollments."}, status=status.HTTP_403_FORBIDDEN)
    
    enrollments = EnrollmentTraining.objects.filter(
        student=request.user.student_profile
    ).select_related('program')
    serializer = EnrollmentTrainingSerializer(enrollments, many=True)
    return Response(serializer.data)
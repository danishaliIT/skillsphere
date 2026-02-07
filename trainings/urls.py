from django.urls import path
from .views import (
    TrainingProgramListCreateView, 
    TrainingProgramDetailView,
    EnrollInTrainingView,
    my_training_enrollments
)

urlpatterns = [
    path('programs/', TrainingProgramListCreateView.as_view(), name='training-list'),
    path('programs/<int:pk>/', TrainingProgramDetailView.as_view(), name='training-detail'),
    path('enroll/<int:program_id>/', EnrollInTrainingView.as_view(), name='enroll-training'),
    path('my-enrollments/', my_training_enrollments, name='my-enrollments'),
]
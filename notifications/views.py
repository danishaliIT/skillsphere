from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class NotificationListView(generics.ListAPIView):
    """User ki apni notifications fetch karne ke liye"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationMarkReadView(generics.UpdateAPIView):
    """Notification ko read mark karne ke liye"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def perform_update(self, serializer):
        # Jab update ho toh is_read ko True kar dein
        serializer.save(is_read=True)


class NotificationMarkAllReadView(APIView):
    """Mark all notifications for the authenticated user as read"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        qs = Notification.objects.filter(user=request.user, is_read=False)
        updated = qs.update(is_read=True)
        return Response({'marked': updated}, status=status.HTTP_200_OK)
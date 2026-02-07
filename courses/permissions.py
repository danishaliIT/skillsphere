from rest_framework import permissions

class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        # Sirf login users aur jin ka role 'Instructor' ho
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'instructor_profile'))
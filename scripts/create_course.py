import os
import sys
from pathlib import Path
import random

# Ensure project root is on path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Course
from profiles.models import InstructorProfile

User = get_user_model()

def main():
    # 1. Get or create a user with the 'Instructor' role.
    instructor_user, user_created = User.objects.get_or_create(
        email='instructor@example.com',
        defaults={
            'username': 'instructor_test',
            'role': 'Instructor',
            'is_verified': True
        }
    )
    if user_created:
        instructor_user.set_password('testpassword')
        instructor_user.save()
        print(f"Created instructor user: {instructor_user.email}")
    else:
        print(f"Found instructor user: {instructor_user.email}")

    # 2. Get or create an `InstructorProfile` for that user.
    instructor_profile, profile_created = InstructorProfile.objects.get_or_create(
        user=instructor_user,
        defaults={
            'full_name': 'Test Instructor',
            'expertise': 'Django',
            'experience_years': 5,
            'bio': 'This is a test instructor.',
        }
    )
    if profile_created:
        print(f"Created instructor profile for: {instructor_user.email}")
    else:
        print(f"Found instructor profile for: {instructor_user.email}")


    # 3. Create a new `Course` with that `InstructorProfile`.
    course_title = f"New Course by Gemini {random.randint(1, 1000)}"
    new_course = Course.objects.create(
        instructor=instructor_profile,
        title=course_title,
        description="This is a test course created by a script.",
        category='Web Dev',
        price=19.99,
        status='pending' # Set to pending to trigger admin review
    )

    print(f"Successfully created course: '{new_course.title}' by {instructor_profile.full_name}")
    print("A notification should have been created for the instructor.")

if __name__ == '__main__':
    main()

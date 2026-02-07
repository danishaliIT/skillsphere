import os
import sys
from pathlib import Path

# Ensure project root is on path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from courses.models import Course

def main():
    qs = Course.objects.select_related('instructor__user').all()
    print('Total courses:', qs.count())
    for c in qs:
        uname = c.instructor.user.username if c.instructor and c.instructor.user else 'N/A'
        print(f'- {c.id} | {c.title!r} | status={c.status} | instructor={uname} | slug={c.slug}')

if __name__ == '__main__':
    main()

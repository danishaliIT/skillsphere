import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

def main(username='zahid'):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print('User not found:', username)
        return
    refresh = RefreshToken.for_user(user)
    print('ACCESS_TOKEN=', str(refresh.access_token))
    print('REFRESH_TOKEN=', str(refresh))

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

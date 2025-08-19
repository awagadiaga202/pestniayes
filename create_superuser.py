import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prestniayes.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
password = "admin123"
email = "admin@example.com"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password, role="admin")
    print("Superuser created ✅")
else:
    print("Superuser already exists ⚡")

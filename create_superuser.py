import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prestniayes.settings")
django.setup()

from django.contrib.auth.models import User

username = "awa"
email = "gadiagaawa2@.com"
password = "awa12345"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser créé ✅")
else:
    print("Superuser existe déjà ❌")

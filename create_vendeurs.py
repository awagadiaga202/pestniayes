import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prestniayes.settings")
django.setup()

from gestion.models import Utilisateur

# Liste des vendeurs à créer
vendeurs = [
    {"username": "cheikh", "password": "cheikh123"},
    {"username": "diarra", "password": "Diarra123"},
]

for v in vendeurs:
    if not Utilisateur.objects.filter(username=v["username"]).exists():
        user = Utilisateur.objects.create_user(
            username=v["username"],
            password=v["password"],
            role="vendeur"
        )
        print(f"✅ Utilisateur {v['username']} (vendeur) créé avec succès.")
    else:
        print(f"⚠️ {v['username']} existe déjà.")

#!/bin/bash
echo "Appliquer les migrations..."
python manage.py migrate

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "Création du superuser..."
python create_superuser.py

echo "Création des vendeurs..."
python create_vendeurs.py

echo "Démarrage du serveur Gunicorn..."
gunicorn prestniayes.wsgi:application --bind 0.0.0.0:10000

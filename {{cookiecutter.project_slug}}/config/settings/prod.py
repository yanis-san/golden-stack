from .base import *
import os

# ==============================================================================
# 🚀 GUIDE DE DÉPLOIEMENT CPANEL
# ==============================================================================
#
# A. VARIABLES D'ENVIRONNEMENT (Dans l'interface "Setup Python App") :
#    1. DJANGO_SETTINGS_MODULE = config.settings.prod  <-- CRITIQUE
#    2. DJANGO_SECRET_KEY      = (Générez une longue chaîne aléatoire)
#    3. DJANGO_ALLOWED_HOSTS   = mondomaine.com www.mondomaine.com
#    
#    [Base de données MySQL cPanel] :
#    4. DB_NAME     = (Nom de la base cPanel)
#    5. DB_USER     = (Utilisateur cPanel)
#    6. DB_PASSWORD = (Mot de passe utilisateur)
#    7. DB_HOST     = localhost
#
# B. APRÈS CHAQUE MISE À JOUR DU CODE (dans un terminal SSH cPanel) :
#    Activez d'abord le virtualenv configuré dans "Setup Python App".
#    Le shell SSH doit aussi disposer des variables de production ci-dessus.
#    Si cPanel ne les transmet pas au shell, définissez-les dans ce terminal
#    sans enregistrer de secret dans le dépôt.
#
#    export DJANGO_SETTINGS_MODULE=config.settings.prod
#    python manage.py migrate
#    python manage.py tailwind build
#    python manage.py collectstatic --noinput
#
#    Enfin, redémarrez l'application depuis "Setup Python App" (ou en touchant
#    le fichier passenger_wsgi.py si cette méthode est configurée sur le compte).
#    Ne lancez pas collectstatic pendant le développement local ; Tailwind
#    utilise alors son watcher.
#
# C. CONFIGURATION DU FICHIER 'passenger_wsgi.py' :
#    cPanel peut y générer du code nécessaire à l'environnement Python.
#    Ne remplacez pas tout le fichier sans préserver ce code.
#    Vérifiez que l'ajout du projet au chemin et le choix des settings sont faits
#    avant l'import de l'application Django. Adaptez l'exemple au fichier généré :
#
#    import os
#    import sys
#    project_root = os.path.dirname(os.path.abspath(__file__))
#    if project_root not in sys.path:
#        sys.path.insert(0, project_root)
#    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")
#    from config.wsgi import application
#
# ==============================================================================

# --- SÉCURITÉ CRITIQUE ---
DEBUG = False

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    raise ValueError("❌ ERREUR PROD : Variable 'DJANGO_SECRET_KEY' manquante !")

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(' ')

# --- BASE DE DONNÉES (MySQL via PyMySQL) ---
# En production, on impose MySQL.
import pymysql
pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# --- OPTIMISATION STATIQUES (WhiteNoise Prod) ---
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# --- SÉCURITÉ HTTPS ---
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
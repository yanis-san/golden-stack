import os
import subprocess
import sys
import urllib.request
import time

# --- CONFIGURATION ---
SUPERUSER_NAME = "yanis"
SUPERUSER_EMAIL = "yanis@example.com"
SUPERUSER_PASS = "ueshlamiff"
MAX_RETRIES = 3
RETRY_DELAY = 5  # secondes

def download_file(url, dest_path):
    print(f"⬇️  Téléchargement de {os.path.basename(dest_path)}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
    except Exception as e:
        print(f"❌ Erreur téléchargement {url}: {e}")

def run_with_retry(cmd, description, max_retries=MAX_RETRIES):
    """Exécute une commande avec retry en cas d'échec réseau"""
    for attempt in range(1, max_retries + 1):
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            if attempt < max_retries:
                print(f"⚠️  Tentative {attempt}/{max_retries} échouée pour '{description}'")
                print(f"   Nouvelle tentative dans {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ Échec de '{description}' après {max_retries} tentatives")
                raise e
    return False

def get_venv_python():
    """Récupère le chemin de l'exécutable Python dans le venv"""
    if sys.platform == "win32":
        return os.path.join(".venv", "Scripts", "python.exe")
    return os.path.join(".venv", "bin", "python")

def main():
    print("\n🚀 Initialisation de la Golden Stack (Correction Windows)...\n")

    # 1. ASSETS
    static_js_dir = os.path.join('static', 'js')
    if not os.path.exists(static_js_dir):
        os.makedirs(static_js_dir)

    download_file("https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js", os.path.join(static_js_dir, "alpine.min.js"))
    download_file("https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js", os.path.join(static_js_dir, "htmx.min.js"))

    # 2. VENV
    print(f"\n📦 Création du venv...")
    subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    venv_python = get_venv_python()

    # 3. INSTALL
    print("📥 Installation des libs...")
    subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    # 4. TAILWIND BINARY (avec retry car le téléchargement peut échouer)
    print("🎨 Installation binaire Tailwind...")
    run_with_retry(
        [venv_python, "manage.py", "tailwind", "install"],
        "Installation Tailwind"
    )

    # 5. MIGRATIONS
    print("🗄️  Migrations...")
    subprocess.run([venv_python, "manage.py", "migrate"], check=True)

    # 6. SUPERUSER
    print(f"👤 Création Admin '{SUPERUSER_NAME}'...")
    create_user_script = f"""
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='{SUPERUSER_NAME}').exists():
    User.objects.create_superuser('{SUPERUSER_NAME}', '{SUPERUSER_EMAIL}', '{SUPERUSER_PASS}')
else:
    pass
"""
    subprocess.run([venv_python, "manage.py", "shell", "-c", create_user_script], check=True)

    # 7. INSTRUCTIONS DE DÉMARRAGE (OS SPECIFIC)
    print("\n" + "="*50)
    print("✅ INSTALLATION TERMINÉE !")
    print("="*50)
    print(f"🔑 Admin : {SUPERUSER_NAME} / {SUPERUSER_PASS}")
    print("\n👉 PROCEDURE DE LANCEMENT :")
    
    if sys.platform == "win32":
        # Instructions Spécifiques Windows (2 Terminaux)
        print("⚠️  Sur Windows, il faut 2 terminaux :")
        print("\n   [Terminal 1 - Django]")
        print("   .\\.venv\\Scripts\\activate")
        print("   python manage.py runserver")
        print("\n   [Terminal 2 - Tailwind Watcher]")
        print("   .\\.venv\\Scripts\\activate")
        print("   python manage.py tailwind start")
    else:
        # Instructions Linux/Mac (1 Terminal)
        print("\n   source .venv/bin/activate")
        print("   python manage.py tailwind dev")
    
    print("="*50 + "\n")

if __name__ == '__main__':
    main()
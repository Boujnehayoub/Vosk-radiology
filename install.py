#!/usr/bin/env python3
"""
install.py — Script d'installation et de vérification de l'environnement
=========================================================================
Lance ce script UNE SEULE FOIS avant le premier démarrage.
Il vérifie Python, installe les dépendances et valide le modèle Vosk.

Usage : python install.py
        python install.py --model /chemin/vers/vosk-model-fr-0.22
"""

import argparse
import subprocess
import sys
import importlib
from pathlib import Path


# ─── Couleurs console ─────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"  {GREEN}✅ {msg}{RESET}")
def warn(msg): print(f"  {YELLOW}⚠️  {msg}{RESET}")
def err(msg):  print(f"  {RED}❌ {msg}{RESET}")
def info(msg): print(f"  {BLUE}ℹ️  {msg}{RESET}")
def title(msg):print(f"\n{BOLD}{msg}{RESET}")


def check_python_version() -> bool:
    title("1. Vérification de Python")
    major, minor = sys.version_info[:2]
    if major == 3 and minor >= 11:
        ok(f"Python {major}.{minor} détecté (requis : 3.11+)")
        return True
    else:
        err(f"Python {major}.{minor} détecté — Python 3.11+ requis")
        info("Téléchargez Python 3.11 sur https://python.org")
        return False


def check_tkinter() -> bool:
    title("2. Vérification de Tkinter")
    try:
        import tkinter
        ok("Tkinter disponible")
        return True
    except ImportError:
        err("Tkinter non disponible")
        info("Linux : sudo apt install python3.11-tk")
        info("macOS : réinstaller Python depuis python.org (inclut Tk)")
        return False


def install_dependencies() -> bool:
    title("3. Installation des dépendances Python")
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        err("requirements.txt introuvable")
        return False

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "-r", str(req_file), "--quiet"
        ])
        ok("vosk installé")
        ok("pyaudio installé")
        return True
    except subprocess.CalledProcessError:
        err("Échec de l'installation des dépendances")
        info("Windows : pip install pipwin && pipwin install pyaudio")
        info("Linux   : sudo apt install portaudio19-dev, puis pip install pyaudio")
        return False


def check_vosk_import() -> bool:
    title("4. Vérification de l'import Vosk")
    try:
        import vosk
        ok(f"Vosk importé avec succès")
        return True
    except ImportError as e:
        err(f"Impossible d'importer vosk : {e}")
        return False


def check_pyaudio_import() -> bool:
    title("5. Vérification de PyAudio")
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        n = pa.get_device_count()
        pa.terminate()
        ok(f"PyAudio OK — {n} périphérique(s) audio détecté(s)")
        return True
    except Exception as e:
        err(f"PyAudio erreur : {e}")
        info("Assurez-vous que PortAudio est installé sur votre système")
        return False


def check_model(model_path: str) -> bool:
    title("6. Vérification du modèle Vosk")
    path = Path(model_path)

    if not path.exists():
        err(f"Modèle introuvable : {path}")
        info("Téléchargez le modèle :")
        info("  wget https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip")
        info("  unzip vosk-model-fr-0.22.zip")
        return False

    # Vérifier les fichiers essentiels du modèle
    required_files = ["am/final.mdl", "conf/model.conf"]
    missing = [f for f in required_files if not (path / f).exists()]

    if missing:
        warn(f"Fichiers manquants dans le modèle : {missing}")
        warn("Le modèle est peut-être incomplet ou corrompu.")
        return False

    size_mb = sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1e6
    ok(f"Modèle trouvé : {path.name} ({size_mb:.0f} Mo)")
    return True


def generate_vocab_file() -> bool:
    title("7. Génération du vocabulaire médical")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from semaine2.medical_vocab import build_vosk_vocab_file, MEDICAL_VOCABULARY
        build_vosk_vocab_file("data/vocab_medical.txt")
        total = sum(len(v) for v in MEDICAL_VOCABULARY.values())
        ok(f"vocab_medical.txt généré ({total} termes)")
        return True
    except Exception as e:
        err(f"Erreur lors de la génération : {e}")
        return False


def list_microphones():
    title("8. Micros disponibles")
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        found = False
        for i in range(pa.get_device_count()):
            info_dev = pa.get_device_info_by_index(i)
            if info_dev["maxInputChannels"] > 0:
                print(f"     [{i}] {info_dev['name']}")
                found = True
        pa.terminate()
        if not found:
            warn("Aucun microphone détecté !")
        return found
    except Exception:
        warn("Impossible de lister les micros")
        return False


def print_launch_instructions(model_path: str):
    print(f"\n{'═'*55}")
    print(f"{BOLD}{GREEN}  ✅ Installation terminée !{RESET}")
    print(f"{'═'*55}")
    print(f"\n  Pour lancer le projet :\n")
    print(f"  {BOLD}Interface graphique (recommandé) :{RESET}")
    print(f"    python main.py --model {model_path}\n")
    print(f"  {BOLD}Terminal uniquement :{RESET}")
    print(f"    python main.py --mode terminal --model {model_path}\n")
    print(f"  {BOLD}Tests unitaires :{RESET}")
    print(f"    python -m pytest tests/ -v\n")
    print(f"{'═'*55}\n")


# ─── Point d'entrée ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Installation DictéeRadio")
    parser.add_argument(
        "--model", default="vosk-model-fr-0.22",
        help="Chemin vers le dossier du modèle Vosk"
    )
    args = parser.parse_args()

    print(f"\n{'═'*55}")
    print(f"{BOLD}  🏥 DictéeRadio — Installation et vérification{RESET}")
    print(f"{'═'*55}")

    steps = [
        check_python_version,
        check_tkinter,
        install_dependencies,
        check_vosk_import,
        check_pyaudio_import,
        lambda: check_model(args.model),
        generate_vocab_file,
        list_microphones,
    ]

    results = [step() for step in steps]
    critical = results[:6]   # les 6 premières sont critiques

    if all(critical):
        print_launch_instructions(args.model)
        sys.exit(0)
    else:
        print(f"\n{RED}{BOLD}  ⚠️  Certaines vérifications ont échoué.{RESET}")
        print(f"  Corrigez les erreurs ci-dessus avant de lancer le projet.\n")
        sys.exit(1)

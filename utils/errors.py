"""
utils/errors.py — Gestion des erreurs et vérifications système
===============================================================
Toutes les vérifications préalables au lancement du projet.
"""

import sys
from pathlib import Path


# ─── Couleurs console ─────────────────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


class DicteeRadioError(Exception):
    """Erreur de base du projet."""
    pass

class ModelNotFoundError(DicteeRadioError):
    """Le modèle Vosk est introuvable."""
    pass

class AudioDeviceError(DicteeRadioError):
    """Problème avec le périphérique audio."""
    pass

class DependencyError(DicteeRadioError):
    """Dépendance Python manquante."""
    pass


def print_startup_banner() -> None:
    """Affiche le banner de démarrage."""
    print(f"""
{BOLD}{'═'*52}
  🏥  DictéeRadio — Dictée vocale médicale
       Prototype hors-ligne · Vosk · Python 3.11
{'═'*52}{RESET}""")


def check_vosk_available() -> None:
    """Vérifie que Vosk est installé."""
    try:
        import vosk  # noqa: F401
    except ImportError:
        print(f"{RED}❌ Vosk non installé.{RESET}")
        print(f"   Lancez : {BOLD}pip install -r requirements.txt{RESET}")
        sys.exit(1)


def check_pyaudio_available() -> None:
    """Vérifie que PyAudio est installé et qu'un micro existe."""
    try:
        import pyaudio
    except ImportError:
        print(f"{RED}❌ PyAudio non installé.{RESET}")
        print(f"   Lancez : {BOLD}pip install -r requirements.txt{RESET}")
        print(f"   Windows : {BOLD}pip install pipwin && pipwin install pyaudio{RESET}")
        sys.exit(1)

    try:
        pa = pyaudio.PyAudio()
        has_input = any(
            pa.get_device_info_by_index(i)["maxInputChannels"] > 0
            for i in range(pa.get_device_count())
        )
        pa.terminate()
        if not has_input:
            print(f"{YELLOW}⚠️  Aucun microphone détecté.{RESET}")
            print("   Branchez un micro et relancez.")
            sys.exit(1)
    except Exception as e:
        print(f"{RED}❌ Erreur PyAudio : {e}{RESET}")
        print("   Linux : sudo apt install portaudio19-dev")
        sys.exit(1)


def check_model_exists(model_path: str) -> None:
    """Vérifie que le dossier du modèle Vosk existe et est valide."""
    path = Path(model_path)

    if not path.exists():
        print(f"{RED}❌ Modèle introuvable : {path}{RESET}")
        print(f"\n   Téléchargez le modèle :")
        print(f"   {BOLD}wget https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip{RESET}")
        print(f"   {BOLD}unzip vosk-model-fr-0.22.zip{RESET}")
        sys.exit(1)

    # Vérifier les fichiers essentiels
    required = ["am/final.mdl", "conf/model.conf"]
    missing  = [f for f in required if not (path / f).exists()]
    if missing:
        print(f"{YELLOW}⚠️  Modèle incomplet — fichiers manquants : {missing}{RESET}")
        print("   Le modèle est peut-être corrompu. Re-téléchargez-le.")
        sys.exit(1)

    print(f"{GREEN}✅ Modèle chargé : {path.name}{RESET}")


def safe_open_stream(pa, rate: int, chunk: int, device_index=None):
    """
    Ouvre un flux audio avec gestion d'erreur claire.
    Retourne le stream ou lève AudioDeviceError.
    """
    import pyaudio

    try:
        return pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=chunk,
            input_device_index=device_index,
        )
    except OSError as e:
        if device_index is not None:
            raise AudioDeviceError(
                f"Micro index {device_index} introuvable ou inaccessible.\n"
                f"   Utilisez --list-devices pour voir les micros disponibles."
            ) from e
        raise AudioDeviceError(
            f"Impossible d'ouvrir le microphone : {e}\n"
            f"   Vérifiez que votre micro est branché et non utilisé par une autre application."
        ) from e

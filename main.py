#!/usr/bin/env python3
"""
main.py — Point d'entrée unique de DictéeRadio
================================================
Lance l'interface graphique Tkinter OU le mode terminal.

Usage :
    python main.py                                  # GUI par défaut
    python main.py --model vosk-model-fr-0.22       # GUI avec modèle custom
    python main.py --mode terminal                  # Mode terminal
    python main.py --mode terminal --device 2       # Terminal + micro spécifique
    python main.py --list-devices                   # Lister les micros
"""

import argparse
import sys
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports relatifs
sys.path.insert(0, str(Path(__file__).parent))

from utils.errors import (
    check_model_exists,
    check_pyaudio_available,
    check_vosk_available,
    print_startup_banner,
)


def launch_gui(model_path: str) -> None:
    """Lance l'interface graphique Tkinter."""
    try:
        import tkinter
    except ImportError:
        print("❌ Tkinter non disponible. Utilisez --mode terminal")
        print("   Linux : sudo apt install python3.11-tk")
        sys.exit(1)

    from semaine4.app_tkinter import DicteeVocaleApp
    app = DicteeVocaleApp(model_path=model_path)
    app.mainloop()


def launch_terminal(model_path: str, device_index: int | None) -> None:
    """Lance la transcription en mode terminal."""
    from semaine1.hello_vocal import stream_microphone
    stream_microphone(model_path, device_index)


def list_devices() -> None:
    """Affiche les périphériques audio disponibles."""
    import pyaudio
    pa = pyaudio.PyAudio()
    print("\n🎙️  Microphones disponibles :\n")
    found = False
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            default = " ← par défaut" if i == pa.get_default_input_device_info()["index"] else ""
            print(f"  [{i}] {info['name']}{default}")
            found = True
    pa.terminate()
    if not found:
        print("  ⚠️  Aucun microphone détecté !")
    print()


# ─── Point d'entrée ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🏥 DictéeRadio — Dictée vocale médicale hors-ligne",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python main.py                             Interface graphique
  python main.py --mode terminal             Mode terminal
  python main.py --model /path/to/model      Modèle personnalisé
  python main.py --list-devices              Lister les micros
        """
    )
    parser.add_argument(
        "--model", default="vosk-model-fr-0.22",
        help="Chemin vers le dossier du modèle Vosk (défaut: vosk-model-fr-0.22)"
    )
    parser.add_argument(
        "--mode", choices=["gui", "terminal"], default="gui",
        help="Mode de lancement : gui (défaut) ou terminal"
    )
    parser.add_argument(
        "--device", type=int, default=None,
        help="Index du microphone (mode terminal uniquement)"
    )
    parser.add_argument(
        "--list-devices", action="store_true",
        help="Lister les micros disponibles et quitter"
    )
    args = parser.parse_args()

    # Afficher le banner
    print_startup_banner()

    # Lister les micros et quitter
    if args.list_devices:
        check_pyaudio_available()
        list_devices()
        sys.exit(0)

    # Vérifications préalables
    check_vosk_available()
    check_pyaudio_available()
    check_model_exists(args.model)

    # Lancement
    if args.mode == "gui":
        launch_gui(args.model)
    else:
        launch_terminal(args.model, args.device)

"""
SEMAINE 1 — Hello World Vocal
==============================
Capture le micro en streaming et affiche la transcription en temps réel.
Usage : python hello_vocal.py --model ../../vosk-model-fr-0.22
"""

import argparse
import json
import sys
import queue
import threading

import pyaudio
import vosk

# Import de la gestion d'erreurs (chemin relatif depuis main.py)
try:
    from utils.errors import safe_open_stream, AudioDeviceError
except ImportError:
    # Fallback si lancé directement depuis semaine1/
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
    from utils.errors import safe_open_stream, AudioDeviceError

# ─── Paramètres audio ────────────────────────────────────────────────────────
SAMPLE_RATE  = 16000   # Hz — Vosk exige 16 kHz
CHUNK_SIZE   = 4000    # ~250 ms par bloc
CHANNELS     = 1
FORMAT       = pyaudio.paInt16


def list_microphones() -> None:
    """Affiche tous les périphériques d'entrée disponibles."""
    pa = pyaudio.PyAudio()
    print("\n🎙️  Microphones disponibles :")
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            print(f"  [{i}] {info['name']}")
    pa.terminate()
    print()


def stream_microphone(model_path: str, device_index: int | None = None) -> None:
    """Ouvre le micro et affiche la transcription en continu."""

    # Chargement du modèle Vosk
    print(f"⏳ Chargement du modèle : {model_path}")
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.SetWords(True)   # inclure les timestamps mot par mot
    print("✅ Modèle chargé. Parlez maintenant (Ctrl+C pour arrêter).\n")

    # File thread-safe : le callback audio pousse les chunks ici
    audio_queue: queue.Queue[bytes] = queue.Queue()

    def audio_callback(in_data, frame_count, time_info, status):
        audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
        input_device_index=device_index,
        stream_callback=audio_callback,
    )
    stream.start_stream()

    try:
        while True:
            data = audio_queue.get()

            if recognizer.AcceptWaveform(data):
                # Résultat final (silence détecté)
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"\n📝 [{text}]")
            else:
                # Résultat partiel (en cours de dictée)
                partial = json.loads(recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text:
                    print(f"\r  ✏️  {partial_text:<60}", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt.")
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()


# ─── Point d'entrée ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hello World vocal — Vosk FR")
    parser.add_argument("--model",  default="vosk-model-fr-0.22",
                        help="Chemin vers le dossier du modèle Vosk")
    parser.add_argument("--device", type=int, default=None,
                        help="Index du micro (voir --list)")
    parser.add_argument("--list",   action="store_true",
                        help="Lister les micros disponibles et quitter")
    args = parser.parse_args()

    if args.list:
        list_microphones()
        sys.exit(0)

    stream_microphone(args.model, args.device)

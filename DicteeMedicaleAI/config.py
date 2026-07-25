import os
import sys
from pathlib import Path
import pyaudio

# Dossier parent de ce fichier
BASE_DIR = Path(__file__).resolve().parent

# --- Configuration Vosk ---
# Chemin relatif ou absolu vers le modèle
MODEL_PATH = str(BASE_DIR / "vosk-model-fr-0.22")

# --- Configuration Audio ---
SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_FORMAT = pyaudio.paInt16  # int16 PCM requis par Vosk
CHUNK_SIZE = 4000

# --- Dictionnaire médical ---
MEDICAL_TERMS_PATH = str(BASE_DIR / "medical_terms.txt")
USE_GRAMMAR_CONSTRAINT = False  # Si True, Vosk ne reconnaîtra QUE les mots autorisés

# --- Commandes vocales de ponctuation ---
# Associe des mots prononcés à des caractères ou actions
PUNCTUATION_COMMANDS = {
    "point d'interrogation": "?",
    "point d'exclamation": "!",
    "nouveau paragraphe": "\n\n",
    "nouvelle ligne": "\n",
    "deux points": ":",
    "point-virgule": ";",
    "virgule": ",",
    "point": ".",
}

# --- Corrections phonétiques personnalisées ---
# Importation depuis le vocabulaire médical de référence
try:
    from medical_vocab import PHONETIC_CORRECTIONS as VOCAB_PHONETIC_CORRECTIONS
except ImportError:
    VOCAB_PHONETIC_CORRECTIONS = {}

# Vosk entend (en minuscules) -> Remplacer par (fusionné avec medical_vocab.py)
PHONETIC_CORRECTIONS = {
    **VOCAB_PHONETIC_CORRECTIONS,
    # Surcharges et termes spécifiques additionnels
    "contrast": "contraste",
    "cerebrale": "cérébrale",
    "cerebral": "cérébral",
    "femur": "fémur",
    "decelee": "décelée",
    "decelees": "décelées",
}

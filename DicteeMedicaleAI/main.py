import os
import sys
import logging
from pathlib import Path

# Ajouter le répertoire parent au path pour faciliter l'exécution de n'importe où
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from recognizer import MedicalSpeechRecognizer
from microphone import MicrophoneManager
from gui import DicteeMedicaleGUI

# Configuration des logs de l'application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def verify_environment() -> None:
    """
    Vérifie que l'environnement d'exécution dispose de toutes les ressources
    nécessaires (fichiers du modèle Vosk, bibliothèques requises).
    """
    logging.info("--- Vérification de l'environnement ---")
    
    # 1. Vérification du modèle Vosk
    model_path = Path(config.MODEL_PATH)
    if not model_path.exists():
        logging.error(f"Le dossier du modèle Vosk n'existe pas : {model_path.resolve()}")
        print(f"\n[ERREUR CRITIQUE] Modèle Vosk introuvable !")
        print(f"Le dossier suivant doit être créé et contenir le modèle français :")
        print(f" -> {model_path.resolve()}")
        print("Veuillez télécharger le modèle depuis : https://alphacephei.com/vosk/models")
        print("Téléchargez 'vosk-model-fr-0.22.zip' et extrayez-le dans ce dossier.\n")
        sys.exit(1)
        
    # Vérification des fichiers clés à l'intérieur du modèle Vosk
    required_files = ["am/final.mdl", "conf/model.conf"]
    for file_rel in required_files:
        file_path = model_path / file_rel
        if not file_path.exists():
            logging.error(f"Fichier du modèle Vosk manquant : {file_path.resolve()}")
            print(f"\n[ERREUR CRITIQUE] Le dossier du modèle Vosk est incomplet !")
            print(f"Le fichier '{file_rel}' est manquant dans {model_path.resolve()}.\n")
            sys.exit(1)
            
    logging.info("Vérification du modèle Vosk : OK")

    # 2. Vérification de PyAudio
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        device_count = pa.get_device_count()
        pa.terminate()
        if device_count == 0:
            logging.warning("Aucun périphérique d'entrée audio (microphone) n'a été détecté.")
        else:
            logging.info(f"Vérification audio : OK ({device_count} périphériques détectés)")
    except ImportError:
        logging.error("La bibliothèque PyAudio n'est pas installée.")
        print("\n[ERREUR CRITIQUE] PyAudio non disponible !")
        print("Veuillez installer PyAudio en lançant : pip install pyaudio\n")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erreur d'initialisation du sous-système audio : {e}")
        print(f"\n[ERREUR CRITIQUE] Impossible d'accéder au sous-système audio : {e}\n")
        sys.exit(1)
        
    logging.info("--- Environnement vérifié avec succès ---")

def main() -> None:
    logging.info("Démarrage de l'application de dictée vocale médicale...")
    
    # Étape 1 : Diagnostiquer l'environnement
    verify_environment()
    
    # Étape 2 : Initialisation des gestionnaires
    try:
        recognizer = MedicalSpeechRecognizer()
        mic_manager = MicrophoneManager(
            sample_rate=config.SAMPLE_RATE,
            channels=config.CHANNELS,
            audio_format=config.AUDIO_FORMAT,
            chunk_size=config.CHUNK_SIZE
        )
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation des composants : {e}")
        print(f"[ERREUR] Impossible d'initialiser les modules : {e}")
        sys.exit(1)

    # Étape 3 : Lancement de l'interface utilisateur
    try:
        app = DicteeMedicaleGUI(recognizer=recognizer, mic_manager=mic_manager)
        app.mainloop()
    except Exception as e:
        logging.error(f"Une erreur inattendue est survenue dans l'application : {e}")
        print(f"[ERREUR APPLICATIVE] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

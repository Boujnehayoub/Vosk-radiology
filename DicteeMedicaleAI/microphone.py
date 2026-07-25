import pyaudio
import sys
import logging
from typing import Callable, Optional

# Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MicrophoneManager:
    """
    Classe responsable de l'initialisation de PyAudio, de la capture du flux
    et de la fermeture propre des ressources audio.
    """
    def __init__(self, sample_rate: int = 16000, channels: int = 1, 
                 audio_format: int = pyaudio.paInt16, chunk_size: int = 4000):
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_format = audio_format
        self.chunk_size = chunk_size
        
        self.pa: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.is_active = False

    def initialize(self) -> None:
        """
        Initialise PyAudio et vérifie la présence d'au moins un périphérique d'entrée.
        """
        try:
            if not self.pa:
                self.pa = pyaudio.PyAudio()
            
            # Vérifier qu'il y a au moins un périphérique de capture
            try:
                default_device = self.pa.get_default_input_device_info()
                logging.info(f"Microphone par défaut détecté : {default_device['name']} (index {default_device['index']})")
            except OSError:
                raise RuntimeError("Aucun périphérique d'entrée audio (microphone) par défaut n'a été détecté par le système.")
                
        except Exception as e:
            self.terminate()
            raise RuntimeError(f"Erreur d'initialisation du sous-système audio PyAudio : {e}")

    def start_stream(self, callback: Callable[[bytes], None]) -> None:
        """
        Démarre la capture audio en arrière-plan avec un callback appelé à chaque chunk.
        """
        if self.is_active:
            return

        self.initialize()
        
        def pyaudio_callback(in_data, frame_count, time_info, status):
            if self.is_active:
                callback(in_data)
            return (None, pyaudio.paContinue)

        try:
            # Ouverture du flux d'entrée
            self.stream = self.pa.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=pyaudio_callback
            )
            self.is_active = True
            self.stream.start_stream()
            logging.info("Flux de capture audio démarré.")
        except Exception as e:
            self.stop_stream()
            raise RuntimeError(f"Impossible de démarrer la capture audio : {e}")

    def stop_stream(self) -> None:
        """
        Arrête l'écoute et libère le flux actuel sans détruire l'objet PyAudio.
        """
        self.is_active = False
        if self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
                logging.info("Flux audio arrêté et fermé.")
            except Exception as e:
                logging.error(f"Erreur lors de la fermeture du flux : {e}")
            finally:
                self.stream = None

    def terminate(self) -> None:
        """
        Ferme toutes les connexions audio et libère l'instance PyAudio.
        """
        self.stop_stream()
        if self.pa:
            try:
                self.pa.terminate()
                logging.info("Sous-système PyAudio libéré.")
            except Exception as e:
                logging.error(f"Erreur lors de la libération de PyAudio : {e}")
            finally:
                self.pa = None

    def get_rms_volume(self, data: bytes) -> int:
        """
        Calcule une valeur de volume (0 à 100) à partir d'un chunk audio de type int16.
        """
        import audioop
        try:
            rms = audioop.rms(data, 2)  # 2 bytes pour int16
            volume = min(100, int(rms / 300))  # Mappage empirique
            return volume
        except Exception:
            return 0

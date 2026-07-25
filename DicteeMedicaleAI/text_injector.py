import time
import threading
import pyperclip
import pyautogui
import keyboard

# Verrou de synchronisation pour garantir la séquentialité de l'injection
_injection_lock = threading.Lock()

# Compteur du nombre de caractères injectés lors de la transcription partielle courante.
# Ce compteur permet de savoir combien de retours arrière (backspaces) envoyer pour écraser la prédiction précédente.
last_partial_length = 0

def safe_copy_to_clipboard(text: str, retries: int = 5, delay: float = 0.015) -> bool:
    """
    Copie du texte dans le presse-papiers de manière sécurisée en gérant les conflits d'accès.
    """
    for i in range(retries):
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            time.sleep(delay)
    return False

def reset_injector() -> None:
    """
    Réinitialise la longueur du texte partiel injecté.
    Utile lors du démarrage ou de l'arrêt de l'écoute.
    """
    global last_partial_length
    with _injection_lock:
        last_partial_length = 0

def inject_text(text: str, is_partial: bool = False) -> None:
    """
    Injecte le texte finalisé dans le champ de saisie actif.
    Pour éviter de polluer le presse-papiers de l'utilisateur et d'avoir des conflits de synchronisation,
    nous n'injectons que le texte validé (final) et nous utilisons keyboard.write.
    """
    if is_partial:
        # On n'injecte pas le texte partiel dans les applications tierces pour éviter
        # le scintillement et l'usage intensif de Backspace qui perturbe la saisie.
        return

    global last_partial_length
    
    with _injection_lock:
        try:
            if text:
                # Ajoute un espace pour séparer les phrases
                paste_text = text + " "
                # Écrit directement le texte caractère par caractère (supporte l'Unicode)
                keyboard.write(paste_text)
                last_partial_length = 0
        except Exception as e:
            print(f"[TextInjector Error] {e}")


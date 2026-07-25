import os
import json
import re
import logging
import threading
import vosk
from typing import Optional, List, Set, Dict, Tuple
import config

# Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MedicalSpeechRecognizer:
    """
    Classe gérant le modèle Vosk, la reconnaissance vocale et 
    le post-traitement du texte (correction médicale, ponctuation, capitalisation).
    """
    def __init__(self, model_path: str = config.MODEL_PATH):
        self.model_path = model_path
        self.model: Optional[vosk.Model] = None
        self.recognizer: Optional[vosk.KaldiRecognizer] = None
        self.medical_words: Set[str] = set()
        self.medical_terms_raw: List[str] = []
        
        # Charger le dictionnaire médical
        self._load_medical_dictionary()

    def _load_medical_dictionary(self) -> None:
        """
        Charge les termes médicaux depuis medical_terms.txt pour enrichir la reconnaissance
        et servir à la mise en évidence ou aux corrections.
        """
        if os.path.exists(config.MEDICAL_TERMS_PATH):
            try:
                with open(config.MEDICAL_TERMS_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        # Ignorer les commentaires et lignes vides
                        if not line or line.startswith("#"):
                            continue
                        
                        self.medical_terms_raw.append(line)
                        # Extraire chaque mot individuel (en minuscules sans ponctuation)
                        for word in line.lower().split():
                            cleaned_word = re.sub(r"[^a-zàâäéèêëîïôùûüç'-]", "", word)
                            if cleaned_word:
                                self.medical_words.add(cleaned_word)
                logging.info(f"Dictionnaire médical chargé : {len(self.medical_terms_raw)} termes, {len(self.medical_words)} mots uniques.")
            except Exception as e:
                logging.error(f"Erreur lors du chargement de {config.MEDICAL_TERMS_PATH} : {e}")
        else:
            logging.warning(f"Fichier de termes médicaux introuvable à : {config.MEDICAL_TERMS_PATH}")

    def load_model(self) -> None:
        """
        Charge le modèle Vosk en mémoire.
        """
        if self.model:
            return

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Dossier du modèle Vosk introuvable : {self.model_path}\n"
                "Veuillez vous assurer que le dossier existe et contient les fichiers am/final.mdl, etc."
            )

        logging.info(f"Chargement du modèle Vosk depuis {self.model_path}...")
        self.model = vosk.Model(self.model_path)
        logging.info("Modèle Vosk chargé avec succès.")
        
        # Initialisation du KaldiRecognizer
        self.reset_recognizer()

    def reset_recognizer(self) -> None:
        """
        Réinitialise le KaldiRecognizer. Permet de vider le buffer interne de Vosk.
        """
        if not self.model:
            return

        if config.USE_GRAMMAR_CONSTRAINT and self.medical_words:
            # Construction d'une grammaire restreinte : mots grammaticaux de base + termes médicaux + ponctuations
            common_french = {
                "le", "la", "les", "un", "une", "des", "du", "de", "d'", "l'", "en", "dans", "par", "pour", "sur",
                "avec", "sans", "sous", "dans", "et", "ou", "mais", "pas", "plus", "moins", "est", "sont", "a",
                "ont", "était", "étaient", "avait", "avaient", "je", "il", "elle", "nous", "vous", "ils", "elles",
                "se", "ce", "ces", "son", "sa", "ses", "leur", "leurs", "qui", "que", "dont", "où", "y", "en",
                "ne", "pas", "plus", "jamais", "rien", "aucun", "aucune", "ni", "gauche", "droit", "droite",
                "bilatéral", "bilatéraux", "antérieur", "postérieur", "supérieur", "inférieur", "médial",
                "latéral", "proximal", "distal", "normal", "normale", "anomalie", "anomalies", "visible",
                "visibles", "pas", "d'anomalie", "décelée", "décelées", "examen", "technique", "conclusion"
            }
            
            # Mots associés aux commandes de ponctuation
            punctuation_words = set()
            for cmd in config.PUNCTUATION_COMMANDS.keys():
                for word in cmd.split():
                    punctuation_words.add(word)
            
            # Fusion de tous les mots autorisés
            grammar_words = self.medical_words.union(common_french).union(punctuation_words)
            # Tri pour constance
            grammar_list = sorted(list(grammar_words))
            
            # Instanciation avec grammaire restreinte
            self.recognizer = vosk.KaldiRecognizer(self.model, config.SAMPLE_RATE, json.dumps(grammar_list, ensure_ascii=False))
            logging.info(f"KaldiRecognizer initialisé avec une grammaire restreinte de {len(grammar_list)} mots.")
        else:
            # Instanciation standard (vocabulaire complet du modèle)
            self.recognizer = vosk.KaldiRecognizer(self.model, config.SAMPLE_RATE)
            logging.info("KaldiRecognizer initialisé en mode vocabulaire complet.")
            
        self.recognizer.SetWords(True)

    def process_audio_chunk(self, chunk: bytes) -> Tuple[bool, Optional[str]]:
        """
        Envoie un chunk audio à Vosk.
        Retourne (is_final, result_text) :
        - is_final=True quand une phrase est terminée (silence). result_text est le texte final.
        - is_final=False pour les prédictions partielles. result_text est le texte partiel.
        """
        if not self.recognizer:
            raise RuntimeError("Le reconnaisseur Vosk n'est pas initialisé.")

        if self.recognizer.AcceptWaveform(chunk):
            res = json.loads(self.recognizer.Result())
            text = res.get("text", "").strip()
            return True, text
        else:
            res = json.loads(self.recognizer.PartialResult())
            text = res.get("partial", "").strip()
            return False, text

    def format_text(self, text: str, is_partial: bool = False) -> str:
        """
        Pipeline de formatage du texte :
        1. Passage en minuscules.
        2. Application des corrections phonétiques.
        3. Remplacement des mots de ponctuation parlée.
        4. Normalisation des espaces (autour des signes de ponctuation).
        5. Capitalisation des débuts de phrase.
        """
        if not text:
            return ""

        # 1. Conversion de base
        formatted = text.lower()

        # 2. Corrections phonétiques (depuis config.py)
        for wrong, correct in config.PHONETIC_CORRECTIONS.items():
            # Remplacement par mot entier ou regex pour éviter les faux positifs internes
            # Le remplacement de sous-chaîne direct est parfois trop agressif, mais pour des termes spécifiques
            # comme "irm" ou "paranchyme", le remplacement direct ou regex fonctionne.
            # On utilise un remplacement de mot avec regex pour être sûr d'avoir des correspondances exactes de mots
            pattern = r'\b' + re.escape(wrong) + r'\b'
            formatted = re.sub(pattern, correct, formatted)

        # 3. Remplacement des ponctuations parlées
        # On trie du plus long au plus court pour éviter les conflits (ex: "point d'interrogation" avant "point")
        sorted_punctuation_cmds = sorted(config.PUNCTUATION_COMMANDS.items(), key=lambda x: len(x[0]), reverse=True)
        
        for spoken, symbol in sorted_punctuation_cmds:
            pattern = r'\b' + re.escape(spoken) + r'\b'
            formatted = re.sub(pattern, symbol, formatted)

        # 4. Normalisation des espaces
        # Enlever les espaces devant la ponctuation : "normale ." -> "normale."
        formatted = re.sub(r'\s+([.,;:!?])', r'\1', formatted)
        # Enlever les espaces autour des retours chariot / sauts de ligne
        formatted = re.sub(r'[ \t]*\n[ \t]*', '\n', formatted)
        # S'assurer d'un espace après la ponctuation (sauf si fin de chaîne, espace ou autre ponctuation)
        formatted = re.sub(r'([.,;:!?])(?=[^\s\n.,;:!?])', r'\1 ', formatted)
        # Nettoyer les espaces multiples
        formatted = re.sub(r' +', ' ', formatted)
        
        # 5. Capitalisation des phrases (uniquement si ce n'est pas un partiel, ou si le partiel est bien avancé)
        # On l'applique toujours mais c'est particulièrement nécessaire sur le résultat final.
        formatted = self._capitalize_sentences(formatted)

        return formatted.strip()

    def _capitalize_sentences(self, text: str) -> str:
        """
        Met en majuscule le premier caractère du texte et les caractères après une ponctuation forte.
        """
        if not text:
            return ""
        
        def repl(match):
            return match.group(1) + match.group(2).upper()
        
        # Recherche le début du texte ou la ponctuation (. ! ?) ou un retour chariot, suivi de blancs éventuels, suivi d'une lettre
        # Gère les caractères accentués français
        return re.sub(r'(^|[.!?\n]\s*)([a-zàâäéèêëîïôùûüç])', repl, text)

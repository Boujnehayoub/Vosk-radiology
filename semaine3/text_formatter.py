"""
SEMAINE 3 — Post-traitement et mise en forme du texte
======================================================
Formate le texte brut Vosk :
  - Ponctuation vocale (point, virgule, nouveau paragraphe…)
  - Majuscule en début de phrase
  - Corrections médicales phonétiques
  - Numéros et unités (millimètres → mm, etc.)
"""

import re
from dataclasses import dataclass, field
from semaine2.medical_vocab import apply_phonetic_corrections, MEDICAL_VOCABULARY


# ─── Commandes vocales → symboles ────────────────────────────────────────────
PUNCTUATION_COMMANDS: dict[str, str] = {
    # Ponctuation de fin
    "point":                        ".",
    "point final":                  ".",
    "point d'interrogation":        "?",
    "point d interrogation":        "?",
    "point d'exclamation":          "!",
    "point d exclamation":          "!",
    "points de suspension":         "…",

    # Ponctuation interne
    "virgule":                      ",",
    "point-virgule":                ";",
    "point virgule":                ";",
    "deux points":                  ":",
    "tiret":                        " —",
    "trait d'union":                "-",
    "parenthèse ouvrante":          "(",
    "parenthèse fermante":          ")",
    "guillemet ouvrant":            "«",
    "guillemet fermant":            "»",

    # Structure
    "nouveau paragraphe":           "\n\n",
    "nouvelle ligne":               "\n",
    "alinéa":                       "\n\n",
    "retour à la ligne":            "\n",

    # Commandes spéciales
    "effacer dernier mot":          "__DELETE_LAST__",
    "effacer tout":                 "__CLEAR__",
}

# Unités médicales courantes (ex: "dix millimètres" → "10 mm")
UNIT_SHORTCUTS: dict[str, str] = {
    r"\bmillimètres?\b":    "mm",
    r"\bcentimètres?\b":    "cm",
    r"\bkilogrammes?\b":    "kg",
    r"\bgrammes?\b":        "g",
    r"\bmilligrammes?\b":   "mg",
    r"\bmicrogrammes?\b":   "µg",
    r"\bsecondes?\b":       "s",
    r"\bminutes?\b":        "min",
    r"\bheures?\b":         "h",
    r"\bmégahertz\b":       "MHz",
    r"\btesla\b":           "T",
    r"\bgray\b":            "Gy",
    r"\bsievert\b":         "Sv",
}


@dataclass
class Transcription:
    """Représente une transcription en cours de construction."""
    raw_segments:   list[str] = field(default_factory=list)
    final_text:     str       = ""

    def append_segment(self, segment: str) -> None:
        self.raw_segments.append(segment)
        self.final_text = format_text(" ".join(self.raw_segments))

    def clear(self) -> None:
        self.raw_segments.clear()
        self.final_text = ""

    def delete_last_word(self) -> None:
        if self.raw_segments:
            self.raw_segments[-1] = " ".join(
                self.raw_segments[-1].split()[:-1]
            )
            self.final_text = format_text(" ".join(self.raw_segments))


# ─── Fonctions de formatage ───────────────────────────────────────────────────

def apply_punctuation_commands(text: str) -> str:
    """
    Remplace les mots de ponctuation dictés par leurs symboles.
    Ex: "douleur thoracique virgule irradiante" → "douleur thoracique, irradiante"
    """
    # Trier par longueur décroissante pour matcher les expressions en premier
    for command, symbol in sorted(
        PUNCTUATION_COMMANDS.items(), key=lambda x: -len(x[0])
    ):
        # Recherche insensible à la casse, séparé par des espaces
        pattern = r"(?<!\w)" + re.escape(command) + r"(?!\w)"
        if symbol == "__DELETE_LAST__":
            text = re.sub(pattern, "__DELETE_LAST__", text, flags=re.IGNORECASE)
        elif symbol == "__CLEAR__":
            text = re.sub(pattern, "__CLEAR__", text, flags=re.IGNORECASE)
        else:
            text = re.sub(pattern, symbol, text, flags=re.IGNORECASE)
    return text


def apply_unit_shortcuts(text: str) -> str:
    """Convertit les unités écrites en abréviation."""
    for pattern, abbrev in UNIT_SHORTCUTS.items():
        text = re.sub(pattern, abbrev, text, flags=re.IGNORECASE)
    return text


def capitalize_sentences(text: str) -> str:
    """Met en majuscule le premier caractère après chaque fin de phrase."""
    # Après . ! ? ou en début de texte
    def cap_after(match):
        return match.group(1) + match.group(2).upper()

    text = re.sub(r"(^|[.!?]\s+)([a-zàâäéèêëîïôùûüç])", cap_after, text)
    return text[0].upper() + text[1:] if text else text


def fix_spacing(text: str) -> str:
    """Corrige les espaces autour de la ponctuation."""
    # Pas d'espace avant : , ; . ! ?
    text = re.sub(r"\s+([,;:!?.»])", r"\1", text)
    # Espace après ces signes (sauf si fin de ligne)
    text = re.sub(r"([,;:!?.»])(?!\s|$|\n)", r"\1 ", text)
    # Espace après «
    text = re.sub(r"(«)(?!\s)", r"\1 ", text)
    # Espaces multiples → simple
    text = re.sub(r" {2,}", " ", text)
    # Espaces en début/fin de ligne
    text = re.sub(r"^ +| +$", "", text, flags=re.MULTILINE)
    return text


def highlight_medical_terms(text: str) -> str:
    """
    Retourne le texte avec les termes médicaux entourés de [crochets].
    Utile pour le débogage et les tests.
    """
    all_terms = [
        term for terms in MEDICAL_VOCABULARY.values() for term in terms
    ]
    # Trier du plus long au plus court pour éviter les sous-matches
    for term in sorted(all_terms, key=len, reverse=True):
        pattern = re.escape(term)
        text = re.sub(
            pattern, f"[{term}]", text, flags=re.IGNORECASE
        )
    return text


def format_text(raw: str, highlight: bool = False) -> str:
    """
    Pipeline complet de formatage :
    1. Corrections phonétiques médicales
    2. Commandes de ponctuation
    3. Raccourcis d'unités
    4. Espacement
    5. Majuscules
    (6. Mise en évidence des termes — optionnel)
    """
    text = raw.strip()
    text = apply_phonetic_corrections(text)
    text = apply_punctuation_commands(text)
    text = apply_unit_shortcuts(text)
    text = fix_spacing(text)
    text = capitalize_sentences(text)
    if highlight:
        text = highlight_medical_terms(text)
    return text


# ─── Démonstration ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  SEMAINE 3 — Post-traitement du texte")
    print("=" * 60)

    test_phrases = [
        (
            "echographie hepatique virgule le foie mesure quinze centimètres "
            "virgule paranchyme homogène point pas de dilatation des voies "
            "biliaires point nouveau paragraphe conclusion aspect normal",
            "Exemple compte-rendu écho hépatique"
        ),
        (
            "irm du genou gauche sans injection coupe axiale coronale et sagittale "
            "virgule epanchement articulaire de faible abondance point "
            "pas de lésion méniscale décelée point",
            "Exemple IRM genou"
        ),
        (
            "scanner thoracique virgule pneumo thorax gauche de cinq millimètres "
            "d'épaisseur virgule pas de hematome sous dural point",
            "Exemple scanner thorax"
        ),
    ]

    for raw, label in test_phrases:
        formatted = format_text(raw)
        highlighted = format_text(raw, highlight=True)

        print(f"\n{'─'*55}")
        print(f"📋 {label}")
        print(f"{'─'*55}")
        print(f"  Brut      : {raw[:80]}…")
        print(f"  Formaté   : {formatted}")
        print(f"  Highlights: {highlighted}")

    print("\n✅ Semaine 3 terminée.\n")

"""
SEMAINE 2 — Vocabulaire médical & radiologique
================================================
Teste la reconnaissance sur du vocabulaire spécialisé et mesure le taux
de succès mot par mot. Génère aussi le fichier vocab.txt pour Vosk.
"""

import json
import re
import time
from pathlib import Path
from difflib import SequenceMatcher


# ─── Dictionnaire médical français ───────────────────────────────────────────
# Organisé par catégorie pour faciliter la maintenance.

MEDICAL_VOCABULARY: dict[str, list[str]] = {

    "imagerie_generale": [
        "radiographie", "radiologie", "radiologue", "échographie",
        "IRM", "scanner", "tomodensitométrie", "scintigraphie",
        "mammographie", "fluoroscopie", "artériographie", "angiographie",
        "urographie", "myélographie", "hystérosalpingographie",
    ],

    "anatomie": [
        "parenchyme", "cortex", "médullaire", "hilaire", "péri-hilaire",
        "péricarde", "myocarde", "endocarde", "péritoine", "mésentère",
        "rétropéritonéal", "sous-cutané", "interstitiel", "intraparenchymateux",
        "péri-vasculaire", "péri-bronchique", "sous-pleural",
    ],

    "thorax": [
        "pneumothorax", "hémothorax", "pleurésie", "épanchement pleural",
        "atélectasie", "consolidation", "opacité", "hyperclarté",
        "bronchectasie", "emphysème", "pneumonie", "broncho-pneumonie",
        "médiastin", "cardiomégalie", "aorte", "trachée", "bronche",
    ],

    "abdomen": [
        "foie", "rate", "pancréas", "vésicule biliaire", "voie biliaire",
        "cholécystite", "lithiase", "cholédoque", "dilatation des voies biliaires",
        "ascite", "hépatomégalie", "splénomégalie", "stéatose hépatique",
        "cirrhose", "aorte abdominale", "anévrysme",
    ],

    "neuro_cranien": [
        "encéphale", "cerveau", "cervelet", "tronc cérébral", "bulbe rachidien",
        "cortex cérébral", "substance blanche", "substance grise",
        "ventricules", "plexus choroïdes", "hypophyse", "sinus caverneux",
        "accident vasculaire cérébral", "ischémie", "hémorragie",
        "hématome sous-dural", "hématome extra-dural", "hémorragie méningée",
    ],

    "os_articulations": [
        "fracture", "fracture-tassement", "fracture comminutive",
        "luxation", "subluxation", "ostéoporose", "ostéolyse", "ostéosclérose",
        "condensation osseuse", "arthrose", "arthrite", "synovite",
        "épanchement articulaire", "pincement articulaire",
    ],

    "terminologie_descriptive": [
        "hypodense", "hyperdense", "isodense", "hypoéchogène", "hyperéchogène",
        "hétérogène", "homogène", "lobulé", "spiculé", "bien limité",
        "mal limité", "calcification", "nécrose", "rehaussement",
        "prise de contraste", "sans injection", "avec injection",
        "coupe axiale", "coupe coronale", "coupe sagittale",
    ],

    "compte_rendu": [
        "compte-rendu", "conclusion", "indication", "technique d'examen",
        "comparaison", "aspect stable", "aspect modifié", "par rapport au précédent",
        "en regard de", "au niveau de", "mesurant", "millimètres", "centimètres",
        "signal normal", "pas d'anomalie décelée", "dans les limites de la normale",
    ],
}


# ─── Corrections phonétiques (ce que Vosk entend → terme correct) ─────────────
PHONETIC_CORRECTIONS: dict[str, str] = {
    # erreurs fréquentes sur les termes médicaux
    "irm":               "IRM",
    "i r m":             "IRM",
    "aire aime":         "IRM",
    "echographie":       "échographie",
    "scanner":           "scanner",
    "scanneur":          "scanner",
    "paranchyme":        "parenchyme",
    "paranchiyme":       "parenchyme",
    "pneumothorax":      "pneumothorax",
    "pneumo thorax":     "pneumothorax",
    "hepatomegalie":     "hépatomégalie",
    "cardiomegalie":     "cardiomégalie",
    "atelactasie":       "atélectasie",
    "consolidasion":     "consolidation",
    "hypo dense":        "hypodense",
    "hyper dense":       "hyperdense",
    "hipo dense":        "hypodense",
    "osteoporose":       "ostéoporose",
    "hematome":          "hématome",
    "ischemie":          "ischémie",
    "stenose":          "sténose",
    "pericarde":         "péricarde",
    "myocarde":          "myocarde",
    "cholecystite":      "cholécystite",
    "lithiase":          "lithiase",
    "anevrismes":        "anévrysmes",
}


def build_vosk_vocab_file(output_path: str = "data/vocab_medical.txt") -> None:
    """
    Génère un fichier vocab.txt contenant tous les mots du dictionnaire.
    Ce fichier peut être passé à KaldiRecognizer pour contraindre le modèle.
    """
    all_terms: set[str] = set()
    for terms in MEDICAL_VOCABULARY.values():
        for term in terms:
            # Vosk attend un mot par ligne, en minuscules
            for word in term.lower().split():
                all_terms.add(re.sub(r"[^a-zàâäéèêëîïôùûüç'-]", "", word))

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(sorted(all_terms)), encoding="utf-8")
    print(f"✅ Vocabulaire écrit : {path}  ({len(all_terms)} mots)")


def apply_phonetic_corrections(text: str) -> str:
    """Applique les corrections phonétiques sur un texte transcrit."""
    text_lower = text.lower()
    for wrong, correct in PHONETIC_CORRECTIONS.items():
        text_lower = text_lower.replace(wrong, correct)
    return text_lower


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def evaluate_recognition(transcribed: str, expected: str) -> dict:
    """Évalue la qualité de la transcription mot par mot."""
    transcribed_words = transcribed.split()
    expected_words    = expected.split()

    correct = sum(
        1 for tw, ew in zip(transcribed_words, expected_words)
        if tw.lower() == ew.lower()
    )
    total = max(len(expected_words), 1)

    return {
        "transcribed":   transcribed,
        "expected":      expected,
        "word_accuracy": round(correct / total * 100, 1),
        "similarity":    round(similarity(transcribed, expected) * 100, 1),
    }


# ─── Démonstration ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  SEMAINE 2 — Vocabulaire médical")
    print("=" * 60)

    # 1. Génération du fichier vocab
    build_vosk_vocab_file()

    # 2. Affichage du dictionnaire par catégorie
    total = 0
    print("\n📚 Dictionnaire médical chargé :")
    for category, terms in MEDICAL_VOCABULARY.items():
        print(f"\n  📂 {category.replace('_', ' ').title()} ({len(terms)} termes)")
        for t in terms[:4]:
            print(f"     • {t}")
        if len(terms) > 4:
            print(f"     … +{len(terms)-4} autres")
        total += len(terms)
    print(f"\n  TOTAL : {total} termes médicaux\n")

    # 3. Simulation d'évaluation (sans micro)
    test_cases = [
        ("irm du genou gauche sans injection", "IRM du genou gauche sans injection"),
        ("echographie hepatique paranchyme homogene", "échographie hépatique parenchyme homogène"),
        ("pneumo thorax gauche", "pneumothorax gauche"),
        ("hematome sous dural", "hématome sous-dural"),
    ]

    print("🧪 Simulation de corrections phonétiques :")
    for raw, expected in test_cases:
        corrected = apply_phonetic_corrections(raw)
        result    = evaluate_recognition(corrected, expected)
        status    = "✅" if result["similarity"] > 80 else "⚠️"
        print(f"\n  Brut      : {raw}")
        print(f"  Corrigé   : {corrected}")
        print(f"  Attendu   : {expected}")
        print(f"  Similarité: {result['similarity']}%  {status}")

    print("\n✅ Semaine 2 terminée.\n")

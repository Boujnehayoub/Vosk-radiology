"""
tests/test_all.py — Tests unitaires complets
=============================================
Couvre : corrections phonétiques, formatage, ponctuation vocale, unités.

Usage :
    python -m pytest tests/ -v
    python -m pytest tests/ -v --tb=short
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from semaine2.medical_vocab import (
    apply_phonetic_corrections,
    MEDICAL_VOCABULARY,
    PHONETIC_CORRECTIONS,
)
from semaine3.text_formatter import (
    apply_punctuation_commands,
    apply_unit_shortcuts,
    capitalize_sentences,
    fix_spacing,
    format_text,
    highlight_medical_terms,
)


# ═══════════════════════════════════════════════════════════════
# SEMAINE 2 — Corrections phonétiques
# ═══════════════════════════════════════════════════════════════

class TestPhoneticCorrections:
    """Tests pour les corrections phonétiques médicales."""

    def test_irm_correction(self):
        assert apply_phonetic_corrections("irm du genou") == "IRM du genou"

    def test_irm_espaces(self):
        assert apply_phonetic_corrections("i r m cervical") == "IRM cervical"

    def test_echographie(self):
        result = apply_phonetic_corrections("echographie abdominale")
        assert "échographie" in result

    def test_parenchyme(self):
        result = apply_phonetic_corrections("paranchyme hepatique")
        assert "parenchyme" in result

    def test_pneumothorax(self):
        result = apply_phonetic_corrections("pneumo thorax gauche")
        assert "pneumothorax" in result

    def test_hematome(self):
        result = apply_phonetic_corrections("hematome sous dural")
        assert "hématome" in result

    def test_texte_deja_correct(self):
        """Un texte déjà correct ne doit pas être modifié."""
        texte = "échographie abdominale normale"
        assert apply_phonetic_corrections(texte) == texte

    def test_toutes_les_corrections_sont_strings(self):
        """Toutes les clés et valeurs du dictionnaire sont des chaînes."""
        for key, value in PHONETIC_CORRECTIONS.items():
            assert isinstance(key, str), f"Clé invalide : {key!r}"
            assert isinstance(value, str), f"Valeur invalide : {value!r}"


class TestMedicalVocabulary:
    """Tests pour le dictionnaire médical."""

    def test_categories_non_vides(self):
        for cat, terms in MEDICAL_VOCABULARY.items():
            assert len(terms) > 0, f"Catégorie vide : {cat}"

    def test_termes_sont_strings(self):
        for cat, terms in MEDICAL_VOCABULARY.items():
            for term in terms:
                assert isinstance(term, str), f"Terme invalide dans {cat}: {term!r}"

    def test_categories_attendues(self):
        expected = {"imagerie_generale", "thorax", "abdomen", "neuro_cranien"}
        assert expected.issubset(set(MEDICAL_VOCABULARY.keys()))

    def test_total_termes_suffisant(self):
        total = sum(len(v) for v in MEDICAL_VOCABULARY.values())
        assert total >= 100, f"Trop peu de termes : {total}"


# ═══════════════════════════════════════════════════════════════
# SEMAINE 3 — Post-traitement
# ═══════════════════════════════════════════════════════════════

class TestPunctuationCommands:
    """Tests pour les commandes de ponctuation vocale."""

    def test_virgule(self):
        result = apply_punctuation_commands("douleur thoracique virgule irradiante")
        assert "," in result
        assert "virgule" not in result

    def test_point(self):
        result = apply_punctuation_commands("examen normal point")
        assert "." in result
        assert "point" not in result

    def test_nouveau_paragraphe(self):
        result = apply_punctuation_commands("conclusion nouveau paragraphe aspect normal")
        assert "\n" in result

    def test_point_interrogation(self):
        result = apply_punctuation_commands("anomalie décelée point d'interrogation")
        assert "?" in result

    def test_deux_points(self):
        result = apply_punctuation_commands("conclusion deux points aspect normal")
        assert ":" in result

    def test_commande_insensible_casse(self):
        result = apply_punctuation_commands("résultat VIRGULE normal")
        assert "," in result

    def test_phrase_sans_commande(self):
        texte = "aucune anomalie décelée"
        result = apply_punctuation_commands(texte)
        assert result == texte


class TestUnitShortcuts:
    """Tests pour les abréviations d'unités."""

    def test_millimetres(self):
        result = apply_unit_shortcuts("lésion de 12 millimètres")
        assert "mm" in result
        assert "millimètres" not in result

    def test_centimetres(self):
        result = apply_unit_shortcuts("foie de 15 centimètres")
        assert "cm" in result

    def test_kilogrammes(self):
        result = apply_unit_shortcuts("poids 70 kilogrammes")
        assert "kg" in result

    def test_milligrammes(self):
        result = apply_unit_shortcuts("dose de 500 milligrammes")
        assert "mg" in result

    def test_singulier_pluriel(self):
        r1 = apply_unit_shortcuts("1 millimètre")
        r2 = apply_unit_shortcuts("2 millimètres")
        assert "mm" in r1
        assert "mm" in r2


class TestCapitalizeSentences:
    """Tests pour la mise en majuscule des phrases."""

    def test_debut_texte(self):
        result = capitalize_sentences("aspect normal")
        assert result[0].isupper()

    def test_apres_point(self):
        result = capitalize_sentences("premier segment. second segment")
        assert "Second" in result or "second" not in result.split(". ")[1]

    def test_texte_vide(self):
        assert capitalize_sentences("") == ""


class TestFixSpacing:
    """Tests pour la correction des espaces."""

    def test_espace_avant_virgule(self):
        result = fix_spacing("texte , suite")
        assert "texte, suite" in result

    def test_espace_avant_point(self):
        result = fix_spacing("texte . fin")
        assert "texte. fin" in result or "texte." in result

    def test_double_espace(self):
        result = fix_spacing("texte  double  espace")
        assert "  " not in result


class TestFormatTextPipeline:
    """Tests du pipeline complet format_text()."""

    def test_pipeline_compte_rendu_basique(self):
        raw = "echographie hepatique virgule paranchyme homogène point"
        result = format_text(raw)
        assert "," in result
        assert "." in result
        assert "échographie" in result.lower()
        assert "parenchyme" in result.lower()

    def test_pipeline_irm(self):
        raw = "irm du genou sans injection coupe axiale virgule aspect normal point"
        result = format_text(raw)
        assert "IRM" in result
        assert "," in result

    def test_pipeline_majuscule_debut(self):
        raw = "scanner thoracique virgule pas d'anomalie"
        result = format_text(raw)
        assert result[0].isupper()

    def test_pipeline_unites(self):
        raw = "nodule mesurant 8 millimètres"
        result = format_text(raw)
        assert "mm" in result

    def test_pipeline_plusieurs_phrases(self):
        raw = (
            "echographie hepatique virgule foie de taille normale point "
            "nouveau paragraphe conclusion virgule pas d'anomalie point"
        )
        result = format_text(raw)
        assert "\n" in result
        assert result.count(".") >= 2


class TestHighlightMedicalTerms:
    """Tests pour la mise en évidence des termes médicaux."""

    def test_terme_encadre(self):
        result = highlight_medical_terms("IRM du genou sans anomalie")
        assert "[IRM]" in result

    def test_plusieurs_termes(self):
        result = highlight_medical_terms("scanner thoracique virgule pneumothorax gauche")
        assert "[" in result

    def test_texte_sans_terme(self):
        result = highlight_medical_terms("bonjour tout le monde")
        assert "[" not in result


# ═══════════════════════════════════════════════════════════════
# Tests d'intégration
# ═══════════════════════════════════════════════════════════════

class TestIntegration:
    """Tests de bout en bout simulant une vraie dictée."""

    DICTEE_RADIO = (
        "echographie hepatique virgule le foie mesure quinze centimètres "
        "virgule paranchyme homogène point pas de dilatation des voies "
        "biliaires point nouveau paragraphe conclusion virgule aspect normal point"
    )

    DICTEE_IRM = (
        "irm du genou gauche sans injection virgule coupe axiale coronale et "
        "sagittale virgule epanchement articulaire de faible abondance point "
        "pas de lésion méniscale décelée point"
    )

    def test_dictee_radio_produit_texte_non_vide(self):
        result = format_text(self.DICTEE_RADIO)
        assert len(result.strip()) > 10

    def test_dictee_radio_contient_virgules(self):
        result = format_text(self.DICTEE_RADIO)
        assert result.count(",") >= 2

    def test_dictee_radio_commence_par_majuscule(self):
        result = format_text(self.DICTEE_RADIO)
        assert result[0].isupper()

    def test_dictee_irm_corrige_irm(self):
        result = format_text(self.DICTEE_IRM)
        assert "IRM" in result

    def test_dictee_radio_centimetres_abreges(self):
        result = format_text(self.DICTEE_RADIO)
        assert "cm" in result

    def test_dictee_radio_paragraphe(self):
        result = format_text(self.DICTEE_RADIO)
        assert "\n" in result


# ─── Lancement direct ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Lancez les tests avec : python -m pytest tests/ -v")
    print("Lancement rapide      : python -m pytest tests/ -q")

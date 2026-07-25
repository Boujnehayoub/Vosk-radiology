"""
DicteeMedicaleAI/medical_vocab.py
=================================
Vocabulaire médical extrait des vrais comptes rendus radiologiques +
enrichi par catégorie. Utilisé pour corriger la transcription.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# VOCABULAIRE EXTRAIT DES COMPTES RENDUS RÉELS
# (Échographie abdominale/rénale, Scanner thoracique, IRM médullaire/rectum,
#  Hystéro-salpingographie, Uro-scanner)
# ═══════════════════════════════════════════════════════════════════════════════

MEDICAL_VOCABULARY: dict[str, list[str]] = {

    # ── Examens d'imagerie ────────────────────────────────────────────────────
    "examens": [
        "échographie abdominale", "échographie rénale", "échographie pelvienne",
        "échographie hépatique", "échographie obstétricale",
        "scanner thoracique", "scanner abdominal", "scanner cérébral",
        "uro-scanner", "scanner TAP",
        "IRM médullaire", "IRM du rectum", "IRM cérébrale", "IRM lombaire",
        "IRM cervicale", "IRM du genou",
        "hystéro-salpingographie",
        "radiographie", "mammographie", "scintigraphie",
        "artériographie", "angiographie",
        "tomodensitométrie", "TDM",
    ],

    # ── Technique d'examen ────────────────────────────────────────────────────
    "technique": [
        "acquisition hélicoïdale", "acquisition multiplanaire",
        "coupes sagittales", "coupes axiales", "coupes coronales",
        "coupes pondérées T1", "coupes pondérées T2",
        "séquences de diffusion", "cartographie ADC",
        "séquences T1 FS", "avant et après injection",
        "injection de gadolinium", "injection de produit de contraste",
        "sans injection de produit de contraste",
        "Merge 2D", "haute résolution",
        "apex pulmonaires", "bases pulmonaires",
        "dôme du foie", "plancher pelvien",
        "spire de 16x1mm",
    ],

    # ── Abdomen et foie ───────────────────────────────────────────────────────
    "abdomen": [
        "foie", "rate", "pancréas", "vésicule biliaire", "voies biliaires",
        "voies biliaires intra-hépatiques", "voies biliaires extra-hépatiques",
        "vaisseaux hépatiques", "échostructure homogène", "échostructure hétérogène",
        "contours réguliers", "contours irréguliers",
        "calcul enclavé", "calcul pyélique", "calcul caliciel",
        "collet", "paroi fine", "paroi épaissie",
        "distension", "légèrement distendue",
        "palpation sélective", "sensible à la palpation",
        "hépatomégalie", "splénomégalie",
        "stéatose hépatique", "cirrhose",
        "épanchement péritonéal", "ascite",
        "adénopathie abdominale", "adénopathie mésentérique",
        "adénopathie rétro-péritonéale", "adénopathie pelvienne",
        "formations ovalaires mésentériques", "hile vasculaire",
        "épigastrique", "mésentérique",
    ],

    # ── Reins et voies urinaires ──────────────────────────────────────────────
    "urologie": [
        "reins", "rein droit", "rein gauche",
        "cavités pyélo-calicielles", "cavités urétéro-pyélo-calicielles",
        "dilatation des cavités", "pyélon",
        "cortex", "épaisseur corticale", "corticale conservée",
        "hyperéchogène", "hypoéchogène",
        "lithiase rénale", "lithiase vésicale",
        "kystes corticaux séreux", "kystes rénaux bilatéraux simples",
        "vessie", "réplétion", "faible réplétion",
        "uretère", "syndrome de jonction",
        "non obstructif", "sans obstacle décelé",
        "caliciel inférieur", "caliciel supérieur",
        "grand axe", "antéro-postérieur",
        "IV d'iode", "produit de contraste iodé",
    ],

    # ── Thorax et poumons ─────────────────────────────────────────────────────
    "thorax": [
        "pneumopathie interstitielle diffuse bilatérale",
        "pneumopathie", "pneumonie", "broncho-pneumonie",
        "épaississement septal", "lignes septales",
        "verre dépoli", "plages de verre dépoli",
        "prédominance basale", "bases pulmonaires",
        "collapsus", "atélectasie",
        "lobe moyen", "lingula", "lingulaire inférieur",
        "segment médial", "bronchectasies cylindriques",
        "troubles ventilatoires", "troubles ventilatoires en bande",
        "remaniements séquellaires",
        "ganglion médiastinal", "médiastin",
        "structures cardio-vasculaires",
        "hernie hiatale par glissement",
        "crosse aortique", "infiltration calcique",
        "épanchement pleural", "épanchement péricardique",
        "thyroïde", "nodule hypodense",
        "pneumothorax", "hémothorax", "pleurésie",
        "fibrosante", "fibrose",
    ],

    # ── Rachis et IRM médullaire ──────────────────────────────────────────────
    "rachis": [
        "rachis cervical", "rachis dorsal", "rachis lombaire",
        "étage cervico-dorsal", "étage lombaire",
        "charnière cervico-occipitale", "charnière recto-sigmoïdienne",
        "lordose cervicale", "cyphose",
        "corps vertébraux", "murs postérieurs",
        "disque intervertébral", "hernie discale",
        "hernie discale médiane", "hernie discale para-médiane",
        "protrusion discale", "protrusion discale globale",
        "saillie discale focale", "saillie discale",
        "déshydratation discale", "espace épidural antérieur",
        "rétrécissement canalaire", "canal rachidien",
        "foramens", "foramen", "foraminal",
        "arthrose inter-apophysaire postérieure",
        "hypertrophie des ligaments jaunes",
        "cordon médullaire", "cône médullaire",
        "myélopathie cervicarthrosique", "cervicarthrose",
        "hernies intra-spongieuses", "vertèbres dorsales",
        "racine L5", "racine S1", "conflit radiculaire",
        "lombosciatique", "sciatique",
        "D12", "L3-L4", "L4-L5", "L5-S1", "C4-C5", "C5-C6",
        "homolatérale",
    ],

    # ── IRM du rectum / oncologie ─────────────────────────────────────────────
    "oncologie_pelvienne": [
        "adénocarcinome du rectum", "adénocarcinome",
        "bilan d'extension locorégionale",
        "processus tumoral", "processus tumoral circonférentiel",
        "infiltrant", "bourgeonnant",
        "moyen rectum", "haut rectum", "bas rectum",
        "marge anale", "jonction anorectale",
        "graisse péri-rectale", "mésorectum",
        "CRM", "marge de résection circonférentielle",
        "EMVI", "invasion vasculaire extramurale",
        "hypersignal intermédiaire en T2",
        "restriction de la diffusion",
        "rehaussement hétérogène",
        "réflexion péritonéale",
        "prostate", "vésicules séminales",
        "adénopathies mésorectales",
        "iliaque interne", "obturatrice",
        "stadification IRM",
        "cT3d", "cN+",
        "TDM TAP",
    ],

    # ── Gynécologie ───────────────────────────────────────────────────────────
    "gynecologie": [
        "cavité utérine", "utérus",
        "lacune intra-cavitaire",
        "isthme", "endocol",
        "trompe gauche", "trompe droite",
        "hydrosalpinx",
        "opacifiée jusqu'en distalité",
        "passage péritonéal",
        "cathétérisme sélectif",
        "perméable", "fine et régulière",
        "diffusion du produit de contraste",
        "cavité péritonéale",
        "anomalie pelvienne",
    ],

    # ── Terminologie descriptive générale ─────────────────────────────────────
    "descriptif": [
        "de taille normale", "de taille augmentée",
        "bien différenciés", "correctement différenciés",
        "homogène", "hétérogène",
        "hypodense", "hyperdense", "isodense",
        "hypoéchogène", "hyperéchogène",
        "lobulé", "spiculé", "ovalaire",
        "bien limité", "mal limité",
        "calcification", "nécrose",
        "rehaussement", "prise de contraste",
        "en place", "de contours réguliers",
        "sans anomalie notable", "sans anomalie visible",
        "absence d'anomalie", "pas d'anomalie décelée",
        "absence de dilatation",
        "sans rétrécissement", "sans conflit",
        "non décelable", "non décelé",
        "bilatéral", "bilatéraux", "homolatéral",
        "spontanément visible",
        "à confronter au contexte clinique",
        "à correler au bilan biologique",
    ],

    # ── Compte rendu / structure ───────────────────────────────────────────────
    "compte_rendu": [
        "compte-rendu", "conclusion", "au total",
        "renseignements cliniques", "indication",
        "technique", "résultat",
        "aspect stable", "aspect modified",
        "par rapport au précédent examen",
        "on ne dispose pas de l'ancienne imagerie",
        "à noter", "en regard de",
        "mesurant", "millimètres", "centimètres",
        "grand axe", "petit axe",
        "signal normal", "aspect normal",
        "dans les limites de la normale",
        "département d'imagerie médicale",
        "radiologue", "médecin radiologue",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# CORRECTIONS PHONÉTIQUES
# (ce que l'ASR transcrit souvent mal → terme correct)
# ═══════════════════════════════════════════════════════════════════════════════

PHONETIC_CORRECTIONS: dict[str, str] = {
    # Examens
    "irm":                          "IRM",
    "i r m":                        "IRM",
    "aire aime":                     "IRM",
    "tdm":                          "TDM",
    "tap":                          "TAP",
    "echographie":                  "échographie",
    "écho":                         "écho",
    "scanneur":                     "scanner",

    # Abdomen
    "paranchyme":                   "parenchyme",
    "paranchiyme":                  "parenchyme",
    "hepatomegalie":                "hépatomégalie",
    "hepatique":                    "hépatique",
    "vesicule":                     "vésicule",
    "biliaire":                     "biliaire",
    "pancrais":                     "pancréas",
    "pancreas":                     "pancréas",
    "peritoine":                    "péritoine",
    "peritoneal":                   "péritonéal",
    "adenopathie":                  "adénopathie",
    "mensentère":                   "mésentère",

    # Urologie
    "pyelo":                        "pyélo",
    "pyelocalicielles":             "pyélo-calicielles",
    "calicielles":                  "calicielles",
    "ureteropyelocalicielles":      "urétéro-pyélo-calicielles",
    "hydroneuphrosis":              "hydronéphrose",
    "lithiaze":                     "lithiase",

    # Neuro / général
    "hematome":                     "hématome",
    "hemorragie":                   "hémorragie",

    # Thorax
    "pneumo thorax":                "pneumothorax",
    "pneumo-thorax":                "pneumothorax",
    "bronchectasie":                "bronchectasie",
    "atelectasie":                  "atélectasie",
    "atelactasie":                  "atélectasie",
    "epanchement":                  "épanchement",
    "pericardique":                 "péricardique",
    "pleurale":                     "pleurale",

    # Rachis
    "lombosciatique":               "lombosciatique",
    "hernie discale":               "hernie discale",
    "protrusion":                   "protrusion",
    "foraminal":                    "foraminal",
    "canalaire":                    "canalaire",
    "medullaire":                   "médullaire",
    "myélopathie":                  "myélopathie",
    "cervicarthrose":               "cervicarthrose",
    "spongieuse":                   "spongieuse",

    # Oncologie
    "adenocarcinome":               "adénocarcinome",
    "mesorectum":                   "mésorectum",
    "circonferentiel":              "circonférentiel",
    "rectale":                      "rectale",

    # Gynéco
    "hydrosalpinx":                 "hydrosalpinx",
    "hysterosalpingographie":       "hystéro-salpingographie",
    "hystérosalpingographie":       "hystéro-salpingographie",
    "uterin":                       "utérin",
    "uterine":                      "utérine",
    "trompe":                       "trompe",

    # Abréviations numériques
    "emvi":                         "EMVI",
    "crm":                          "CRM",
    "adc":                          "ADC",
}


def apply_phonetic_corrections(text: str) -> str:
    """Applique les corrections phonétiques sur un texte transcrit."""
    import re
    result = text
    for wrong, correct in sorted(PHONETIC_CORRECTIONS.items(), key=lambda x: -len(x[0])):
        pattern = r"(?<!\w)" + re.escape(wrong) + r"(?!\w)"
        result = re.sub(pattern, correct, result, flags=re.IGNORECASE)
    return result


def get_all_terms() -> list[str]:
    """Retourne tous les termes médicaux en liste plate."""
    return [term for terms in MEDICAL_VOCABULARY.values() for term in terms]


if __name__ == "__main__":
    total = sum(len(v) for v in MEDICAL_VOCABULARY.values())
    print(f"✅ Vocabulaire médical : {total} termes dans {len(MEDICAL_VOCABULARY)} catégories")
    for cat, terms in MEDICAL_VOCABULARY.items():
        print(f"   {cat}: {len(terms)} termes")


# 🏥 DictéeRadio — Prototype IA Vocale
**Stage 1 mois — Dictée vocale hors-ligne pour la radiologie**  
Python 3.11 · Vosk · PyAudio · Tkinter

---

## 📋 Présentation

DictéeRadio est un prototype de dictée vocale 100 % local (sans internet),
conçu pour la rédaction de comptes-rendus radiologiques.  
Il utilise le moteur **Vosk** avec le modèle français `vosk-model-fr-0.22`.

---

## 🗂️ Structure du projet

```
vosk_radiology/
├── semaine1/
│   └── hello_vocal.py        ← Script de base : streaming micro → terminal
├── semaine2/
│   └── medical_vocab.py      ← Dictionnaire médical + corrections phonétiques
├── semaine3/
│   └── text_formatter.py     ← Post-traitement : ponctuation, unités, majuscules
├── semaine4/
│   └── app_tkinter.py        ← Interface graphique complète (Tkinter)
├── data/
│   └── vocab_medical.txt     ← Généré par semaine2 (vocabulaire pour Vosk)
└── README.md
```

---

## ⚙️ Installation

### 1. Prérequis système

```bash
# Ubuntu / Debian
sudo apt install python3.11 python3.11-tk portaudio19-dev

# Windows : installer PortAudio via les binaires PyAudio (voir ci-dessous)
```

### 2. Environnement virtuel

```bash
python3.11 -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows
```

### 3. Dépendances Python

```bash
pip install vosk pyaudio
```

> **Windows :** si `pyaudio` échoue, utiliser :
> ```bash
> pip install pipwin && pipwin install pyaudio
> ```

### 4. Modèle Vosk français

```bash
# Téléchargement du modèle léger (40 Mo) — pour les tests
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip

# Modèle complet recommandé (1.4 Go) — meilleure précision médicale
wget https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip
unzip vosk-model-fr-0.22.zip
```

---

## 🚀 Lancement

### Semaine 1 — Hello World vocal (terminal)

```bash
# Lister les micros disponibles
python semaine1/hello_vocal.py --list

# Lancer la transcription
python semaine1/hello_vocal.py --model vosk-model-fr-0.22

# Avec un micro spécifique (ex: index 2)
python semaine1/hello_vocal.py --model vosk-model-fr-0.22 --device 2
```

### Semaine 2 — Test du vocabulaire médical

```bash
python semaine2/medical_vocab.py
# → Génère data/vocab_medical.txt
# → Affiche les catégories et les corrections phonétiques
```

### Semaine 3 — Test du post-traitement

```bash
python semaine3/text_formatter.py
# → Démo de formatage sur des phrases radiologiques
```

### Semaine 4 — Interface graphique

```bash
python semaine4/app_tkinter.py --model vosk-model-fr-0.22
```

---

## 🎙️ Commandes vocales reconnues

| Vous dites       | Résultat      |
|------------------|---------------|
| `virgule`        | `,`           |
| `point`          | `.`           |
| `deux points`    | `:`           |
| `point d'interrogation` | `?`  |
| `nouveau paragraphe` | saut de ligne |
| `effacer dernier mot` | supprime le dernier mot |
| `effacer tout`   | vide le texte |

---

## 🔬 Vocabulaire médical intégré (~130 termes)

- **Imagerie** : IRM, échographie, scanner, tomodensitométrie…
- **Thorax** : pneumothorax, atélectasie, consolidation, pleurésie…
- **Abdomen** : foie, rate, pancréas, cholécystite, ascite…
- **Neuro** : hématome, ischémie, hémorragie méningée…
- **Os** : fracture, luxation, ostéoporose, arthrose…
- **Descriptif** : hypodense, hyperdense, hétérogène, spiculé…

---

## 🧠 Architecture technique

```
Micro (PyAudio)
     │ chunks 16 kHz int16
     ▼
KaldiRecognizer (Vosk)
     │ JSON partiel / final
     ▼
format_text() — Semaine 3
  ├── apply_phonetic_corrections()
  ├── apply_punctuation_commands()
  ├── apply_unit_shortcuts()
  ├── fix_spacing()
  └── capitalize_sentences()
     │
     ▼
Zone texte Tkinter
  └── highlight_medical_terms()  (coloration bleue)
```

---

## 📊 Résultats attendus

| Métrique                        | Valeur cible |
|---------------------------------|-------------|
| Latence de transcription        | < 500 ms    |
| Précision termes courants       | > 90 %      |
| Précision termes médicaux       | 60–80 %     |
| Fonctionnement hors-ligne       | ✅ 100 %    |
| Données transmises au cloud     | ✅ 0 octet  |

---

## 🔧 Améliorations futures (hors scope du stage)

- [ ] Fine-tuning du modèle Vosk sur corpus radiologique
- [ ] Export PDF/DOCX du compte-rendu
- [ ] Templates de phrases radiologiques
- [ ] Correction orthographique post-transcription (pyspellchecker)
- [ ] Support multi-locuteurs (identification du radiologue)

---

## 📄 Dépendances

| Package  | Version | Rôle                        |
|----------|---------|------------------------------|
| vosk     | ≥ 0.3.45 | Moteur ASR hors-ligne       |
| pyaudio  | ≥ 0.2.14 | Capture audio (microphone)  |
| tkinter  | natif    | Interface graphique          |

---

*Prototype réalisé dans le cadre d'un stage de 1 mois — confidentiel médical garanti.*


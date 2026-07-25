# 🏥 Assistant de Dictée Vocale Médicale IA (Windows)

Une application Windows locale et 100% hors-ligne de dictée vocale médicale en temps réel. Conçue spécialement pour les médecins et radiologues, elle s'intègre de manière transparente avec n'importe quel éditeur de texte ou application Windows (Microsoft Word, Google Chrome, Bloc-notes, Excel, formulaires web ou logiciels médicaux DPI/RIS) en écrivant le texte reconnu directement là où se trouve votre curseur.

---

## 🚀 Fonctionnalités clés

1. **Streaming temps réel** : Les mots transcrits apparaissent au fur et à mesure que vous parlez (pas de délai "Enregistrer → Attendre → Transcrire").
2. **Injection directe universelle** : Écrit dans la zone de texte active du système grâce à une simulation d'écriture rapide par copier-coller (`Presse-papiers` + `CTRL+V`).
3. **100% Local & Privé** : Fonctionne entièrement hors-ligne grâce au moteur Vosk. Aucun flux audio ni texte n'est envoyé sur Internet (parfaitement conforme à la confidentialité médicale / RGPD / secret médical).
4. **Vocabulaire médical enrichi** : Chargement d'une base de plus de 1300 termes médicaux réels (Radiologie, Anatomie, Pathologies, Descripteurs cliniques) pour optimiser les prédictions et corriger les homophones ou erreurs d'écriture fréquentes.
5. **Formatage automatique** : Gestion de la ponctuation dictée (ex: "point", "virgule", "nouvelle ligne") et capitalisation automatique des phrases.
6. **Interface flottante compacte** : Fenêtre Tkinter de taille réduite, positionnée en haut de l'écran et toujours visible au-dessus des autres applications (`topmost`).

---

## 📁 Structure du Projet

```
DicteeMedicaleAI/
│
├── main.py               # Point d'entrée principal (Diagnostics & Initialisation)
├── gui.py                # Interface Tkinter flottante compacte
├── microphone.py         # Capture audio du flux microphone via PyAudio
├── recognizer.py         # Reconnaissance Vosk & Pipeline de formatage de texte
├── text_injector.py      # Simulation de touches et injection (Presse-papiers + Backspaces)
├── config.py             # Fichier de configuration globale (paramètres audio, modèle, ponctuation)
├── medical_terms.txt     # Dictionnaire de plus de 1000 mots médicaux en français
├── requirements.txt      # Liste des dépendances Python
└── README.md             # Ce guide d'utilisation
```

---

## 🛠️ Installation

### 1. Prérequis
* Windows 10/11
* Python 3.11+ installé et configuré dans votre variable d'environnement `PATH`.

### 2. Création de l'environnement virtuel et activation
Ouvrez votre terminal (PowerShell ou CMD) dans le dossier du projet :

```bash
# Créer l'environnement virtuel (.venv)
python -m venv .venv

# Activer l'environnement virtuel sur Windows
.venv\Scripts\activate
```

### 3. Installation des dépendances
Installez les bibliothèques requises à l'aide du gestionnaire `pip` :

```bash
pip install -r requirements.txt
```

> **Note PyAudio** : Si l'installation de `pyaudio` échoue, vous pouvez utiliser `pipwin` pour l'installer sous Windows :
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

---

## 📦 Téléchargement et Configuration du Modèle Vosk

L'application requiert le modèle français de Vosk.
1. Téléchargez le grand modèle français **`vosk-model-fr-0.22`** (environ 1.4 Go) depuis le site officiel de Vosk :
   [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
2. Extrayez l'archive `.zip`.
3. Renommez le dossier extrait en `vosk-model-fr-0.22`.
4. Déplacez ce dossier dans le répertoire `DicteeMedicaleAI/` de sorte que le chemin soit :
   `DicteeMedicaleAI/vosk-model-fr-0.22/`

---

## 📖 Utilisation

1. Assurez-vous que votre microphone est branché et défini comme périphérique d'enregistrement par défaut sous Windows.
2. Lancez l'application :
   ```bash
   python main.py
   ```
3. Une petite fenêtre flottante noire apparaît en haut de votre écran. Elle reste au premier plan.
4. Attendez le chargement du modèle Vosk (le statut passe à `Prêt` et le badge devient vert `PRÊT`).
5. Ouvrez le logiciel dans lequel vous souhaitez écrire (Word, Chrome, Bloc-notes, etc.) et **cliquez dans la zone de texte où le curseur clignote**.
6. Cliquez sur le bouton **`[ Activer Micro ]`** de l'application de dictée.
7. Parlez naturellement. Le texte reconnu s'affiche progressivement (en mode streaming) directement là où se trouve votre curseur.
8. Pour arrêter la dictée, cliquez sur **`[ Arrêter Micro ]`**. Le microphone sera libéré.

### Exemple de dictée et formatage :
* **Vous dites** : `"scanner abdominal sans injection de produit de contraste virgule à la recherche d'une cholécystite point nouvelle ligne pancréas de taille normale point"`
* **Résultat automatique injecté** : 
  ```text
  Scanner abdominal sans injection de produit de contraste, à la recherche d'une cholécystite.
  Pancréas de taille normale. 
  ```

---

## ⚙️ Paramétrage et Personnalisation

Le fichier `config.py` vous permet d'ajuster le fonctionnement de l'application :
* **`USE_GRAMMAR_CONSTRAINT`** : Si défini sur `True`, contraint la reconnaissance aux seuls mots définis dans `medical_terms.txt` et aux mots grammaticaux de base. Cela réduit les erreurs d'homophonie mais bloque les mots en dehors du dictionnaire. Par défaut à `False` pour utiliser le dictionnaire global.
* **`PUNCTUATION_COMMANDS`** : Permet de configurer ou d'ajouter de nouvelles commandes vocales de ponctuation.
* **`PHONETIC_CORRECTIONS`** : Permet d'ajouter des corrections d'orthographe ou de transcription phonétique pour vos besoins spécifiques en radiologie.

---

## 🧪 Tests de Validation

Pour tester les composants logiques de l'application (notamment le formateur de texte et les corrections phonétiques), vous pouvez lancer un script de test rapide :

Créez un script de test ou exécutez vos tests unitaires.
Exemple pour exécuter la suite de tests globale (à la racine du projet parent) :
```bash
python -m pytest tests/ -v
```

---

## ⚠️ Notes importantes pour Windows
* **Privilèges d'administration** : Sous Windows, les applications s'exécutant avec des droits d'administrateur bloquent l'injection de touches clavier des applications standards (mécanisme de sécurité Windows UIPI). Si vous devez dicter dans un logiciel lancé en tant qu'administrateur, vous devez également lancer ce script Python en tant qu'administrateur.

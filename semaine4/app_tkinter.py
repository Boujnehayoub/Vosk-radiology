"""
SEMAINE 4 — Interface Tkinter de dictée vocale médicale
=========================================================
Interface graphique avec :
  - Bouton Parler / Arrêter
  - Zone texte en temps réel
  - Indicateur de volume
  - Boutons Copier / Effacer / Sauvegarder
  - Mise en évidence des termes médicaux
  - Barre d'état
"""

import argparse
import json
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path

import pyaudio
import vosk

# ─── Ajout du chemin parent pour les imports des semaines précédentes ─────────
sys.path.insert(0, str(Path(__file__).parent.parent))
from semaine3.text_formatter import format_text, Transcription, MEDICAL_VOCABULARY

# ─── Constantes audio ─────────────────────────────────────────────────────────
SAMPLE_RATE = 16000
CHUNK_SIZE  = 4000
FORMAT      = pyaudio.paInt16
CHANNELS    = 1

# ─── Palette de couleurs ──────────────────────────────────────────────────────
COLORS = {
    "bg":           "#1A1A2E",   # fond sombre bleu nuit
    "panel":        "#16213E",   # panneaux légèrement plus clairs
    "accent":       "#0F3460",   # bleu médical foncé
    "highlight":    "#E94560",   # rouge médical vif
    "text":         "#E0E0E0",   # texte principal
    "text_dim":     "#8888AA",   # texte secondaire
    "medical_term": "#4FC3F7",   # termes médicaux en bleu clair
    "partial":      "#FFB74D",   # texte partiel en orange
    "success":      "#66BB6A",   # vert succès
    "error":        "#EF5350",   # rouge erreur
    "button_rec":   "#E94560",   # bouton enregistrement
    "button_stop":  "#607D8B",   # bouton stop
}


class DicteeVocaleApp(tk.Tk):
    """Application principale de dictée vocale radiologique."""

    def __init__(self, model_path: str):
        super().__init__()
        self.model_path    = model_path
        self.transcription = Transcription()
        self.audio_queue:  queue.Queue[bytes] = queue.Queue()
        self.is_recording  = False
        self.pa:           pyaudio.PyAudio | None = None
        self.stream:       pyaudio.Stream | None  = None
        self.recognizer:   vosk.KaldiRecognizer | None = None

        # Construire l'interface
        self._setup_window()
        self._build_ui()

        # Charger le modèle en arrière-plan
        self._load_model_async()

    # ──────────────────────────────────────────────────────────────────────────
    # Configuration de la fenêtre
    # ──────────────────────────────────────────────────────────────────────────

    def _setup_window(self):
        self.title("🏥 DictéeRadio — Prototype IA Vocale")
        self.geometry("900x680")
        self.minsize(700, 520)
        self.configure(bg=COLORS["bg"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame",       background=COLORS["bg"])
        style.configure("Panel.TFrame", background=COLORS["panel"])
        style.configure(
            "TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("Helvetica", 11),
        )
        style.configure(
            "Title.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["highlight"],
            font=("Helvetica", 16, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=COLORS["accent"],
            foreground=COLORS["text"],
            font=("Helvetica", 9),
            padding=(8, 4),
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Construction de l'UI
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ─── En-tête ──────────────────────────────────────────────────────────
        header = ttk.Frame(self)
        header.pack(fill="x", padx=16, pady=(14, 4))

        ttk.Label(header, text="🏥 DictéeRadio", style="Title.TLabel").pack(side="left")
        ttk.Label(
            header,
            text="Dictée vocale médicale hors-ligne • Vosk FR",
            style="TLabel",
            foreground=COLORS["text_dim"],
            font=("Helvetica", 10),
        ).pack(side="left", padx=12)

        # Badge modèle
        self.lbl_model = ttk.Label(
            header, text="⏳ Chargement…",
            background=COLORS["accent"], foreground=COLORS["text_dim"],
            font=("Helvetica", 9), padding=(6, 3),
        )
        self.lbl_model.pack(side="right")

        # Séparateur
        sep = tk.Frame(self, bg=COLORS["accent"], height=1)
        sep.pack(fill="x", padx=0, pady=4)

        # ─── Boutons de contrôle ──────────────────────────────────────────────
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", padx=16, pady=8)

        self.btn_record = tk.Button(
            ctrl,
            text="🎙  Parler",
            bg=COLORS["button_rec"], fg="white",
            font=("Helvetica", 13, "bold"),
            relief="flat", cursor="hand2",
            padx=20, pady=8,
            state="disabled",
            command=self._toggle_recording,
        )
        self.btn_record.pack(side="left")

        # Indicateur de volume
        self.volume_bar = ttk.Progressbar(
            ctrl, length=160, mode="determinate", maximum=100
        )
        self.volume_bar.pack(side="left", padx=12)
        ttk.Label(ctrl, text="Volume", foreground=COLORS["text_dim"],
                  font=("Helvetica", 9)).pack(side="left")

        # Compteur de mots
        self.lbl_words = ttk.Label(
            ctrl, text="0 mots", foreground=COLORS["text_dim"],
            font=("Helvetica", 10),
        )
        self.lbl_words.pack(side="right")

        # ─── Zone de texte principale ─────────────────────────────────────────
        txt_frame = tk.Frame(self, bg=COLORS["panel"], bd=0)
        txt_frame.pack(fill="both", expand=True, padx=16, pady=4)

        self.txt_main = tk.Text(
            txt_frame,
            bg=COLORS["panel"], fg=COLORS["text"],
            font=("Georgia", 13),
            relief="flat", padx=14, pady=12,
            wrap="word",
            insertbackground=COLORS["highlight"],
            selectbackground=COLORS["accent"],
        )
        self.txt_main.pack(side="left", fill="both", expand=True)

        # Scrollbar
        sb = ttk.Scrollbar(txt_frame, command=self.txt_main.yview)
        sb.pack(side="right", fill="y")
        self.txt_main.configure(yscrollcommand=sb.set)

        # Tags de couleur dans la zone texte
        self.txt_main.tag_configure("medical",  foreground=COLORS["medical_term"])
        self.txt_main.tag_configure("partial",  foreground=COLORS["partial"],
                                    font=("Georgia", 13, "italic"))
        self.txt_main.tag_configure("sentence_start", font=("Georgia", 13, "bold"))

        # ─── Texte partiel (sous la zone principale) ─────────────────────────
        self.lbl_partial = tk.Label(
            self,
            text="",
            bg=COLORS["bg"], fg=COLORS["partial"],
            font=("Helvetica", 10, "italic"),
            anchor="w",
        )
        self.lbl_partial.pack(fill="x", padx=20, pady=(0, 4))

        # ─── Boutons d'action ─────────────────────────────────────────────────
        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=16, pady=4)

        for label, cmd in [
            ("📋 Copier",    self._copy_text),
            ("💾 Sauvegarder", self._save_text),
            ("🗑  Effacer",   self._clear_text),
        ]:
            tk.Button(
                actions, text=label,
                bg=COLORS["accent"], fg=COLORS["text"],
                font=("Helvetica", 10), relief="flat",
                cursor="hand2", padx=12, pady=5,
                command=cmd,
            ).pack(side="left", padx=4)

        # Statistiques termes médicaux
        self.lbl_stats = ttk.Label(
            actions, text="",
            foreground=COLORS["medical_term"],
            font=("Helvetica", 9),
        )
        self.lbl_stats.pack(side="right")

        # ─── Barre d'état ─────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Chargement du modèle Vosk…")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bg=COLORS["accent"], fg=COLORS["text"],
            font=("Helvetica", 9), anchor="w", padx=10,
        )
        status_bar.pack(fill="x", side="bottom")

    # ──────────────────────────────────────────────────────────────────────────
    # Chargement asynchrone du modèle
    # ──────────────────────────────────────────────────────────────────────────

    def _load_model_async(self):
        def load():
            try:
                self._set_status("⏳ Chargement du modèle Vosk (peut prendre ~30s)…")
                model = vosk.Model(self.model_path)
                self.recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
                self.recognizer.SetWords(True)

                # ── Intégration du vocabulaire médical ──────────────────────
                # Si le fichier vocab_medical.txt existe, on contraint Vosk
                # à favoriser ces termes → meilleure précision médicale.
                vocab_path = Path(__file__).parent.parent / "data" / "vocab_medical.txt"
                if vocab_path.exists():
                    with open(vocab_path, encoding="utf-8") as f:
                        words = [line.strip() for line in f if line.strip()]
                    # KaldiRecognizer accepte une grammar (liste JSON de mots)
                    import json as _json
                    self.recognizer.SetGrammar(_json.dumps(words, ensure_ascii=False))

                self.after(0, self._on_model_ready)
            except Exception as exc:
                self.after(0, lambda: self._on_model_error(str(exc)))

        threading.Thread(target=load, daemon=True).start()

    def _on_model_ready(self):
        self.btn_record.configure(state="normal")
        self.lbl_model.configure(
            text="✅ Modèle chargé", foreground=COLORS["success"]
        )
        self._set_status("✅ Modèle prêt. Cliquez sur « Parler » pour commencer.")

    def _on_model_error(self, error: str):
        self.lbl_model.configure(
            text="❌ Erreur modèle", foreground=COLORS["error"]
        )
        self._set_status(f"❌ Impossible de charger le modèle : {error}")
        messagebox.showerror(
            "Erreur modèle Vosk",
            f"Le modèle n'a pas pu être chargé :\n{error}\n\n"
            f"Vérifiez le chemin : {self.model_path}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Enregistrement audio
    # ──────────────────────────────────────────────────────────────────────────

    def _toggle_recording(self):
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        self.is_recording = True
        self.btn_record.configure(
            text="⏹  Arrêter", bg=COLORS["button_stop"]
        )
        self._set_status("🎙  Enregistrement en cours… Parlez maintenant.")
        self.pa = pyaudio.PyAudio()

        def audio_callback(in_data, frame_count, time_info, status):
            self.audio_queue.put(in_data)
            # Calcul du volume approximatif
            import audioop
            rms = audioop.rms(in_data, 2)
            volume = min(100, int(rms / 300))
            self.after(0, lambda: self.volume_bar.configure(value=volume))
            return (None, pyaudio.paContinue)

        try:
            self.stream = self.pa.open(
                format=FORMAT, channels=CHANNELS,
                rate=SAMPLE_RATE, input=True,
                frames_per_buffer=CHUNK_SIZE,
                stream_callback=audio_callback,
            )
        except OSError as e:
            self.pa.terminate()
            self.is_recording = False
            self.btn_record.configure(text="🎙  Parler", bg=COLORS["button_rec"])
            self._set_status(f"❌ Microphone inaccessible : {e}")
            messagebox.showerror(
                "Erreur microphone",
                f"Impossible d'ouvrir le microphone :\n{e}\n\n"
                "Vérifiez qu'il est branché et non utilisé par une autre application."
            )
            return
        self.stream.start_stream()
        threading.Thread(target=self._recognition_loop, daemon=True).start()

    def _stop_recording(self):
        self.is_recording = False
        self.btn_record.configure(
            text="🎙  Parler", bg=COLORS["button_rec"]
        )
        self.volume_bar.configure(value=0)
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()
        self.lbl_partial.configure(text="")
        self._set_status("⏸  Enregistrement arrêté. Cliquez sur « Parler » pour continuer.")

    def _recognition_loop(self):
        """Boucle de reconnaissance dans un thread séparé."""
        while self.is_recording:
            try:
                data = self.audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text   = result.get("text", "").strip()
                if text:
                    formatted = format_text(text)
                    self.after(0, lambda t=formatted: self._append_text(t))
            else:
                partial = json.loads(self.recognizer.PartialResult())
                p_text  = partial.get("partial", "").strip()
                self.after(0, lambda t=p_text: self.lbl_partial.configure(
                    text=f"  ✏️  {t}" if t else ""
                ))

    # ──────────────────────────────────────────────────────────────────────────
    # Mise à jour du texte
    # ──────────────────────────────────────────────────────────────────────────

    def _append_text(self, text: str):
        """Insère un segment de texte formaté dans la zone principale."""
        if not text:
            return

        current = self.txt_main.get("1.0", "end-1c")
        separator = " " if current and not current.endswith("\n") else ""
        self.txt_main.insert("end", separator + text)

        # Coloration des termes médicaux
        self._highlight_medical_terms()
        self.txt_main.see("end")

        # Mise à jour du compteur de mots
        all_text  = self.txt_main.get("1.0", "end-1c")
        word_count = len(all_text.split())
        self.lbl_words.configure(text=f"{word_count} mots")

        # Comptage des termes médicaux
        self._update_stats(all_text)

    def _highlight_medical_terms(self):
        """Colore les termes médicaux reconnus dans la zone de texte."""
        self.txt_main.tag_remove("medical", "1.0", "end")
        content = self.txt_main.get("1.0", "end")

        all_terms = [
            term for terms in MEDICAL_VOCABULARY.values() for term in terms
        ]
        for term in sorted(all_terms, key=len, reverse=True):
            start = "1.0"
            while True:
                pos = self.txt_main.search(
                    term, start, stopindex="end", nocase=True
                )
                if not pos:
                    break
                end = f"{pos}+{len(term)}c"
                self.txt_main.tag_add("medical", pos, end)
                start = end

    def _update_stats(self, text: str):
        all_terms = [
            term for terms in MEDICAL_VOCABULARY.values() for term in terms
        ]
        found = sum(
            1 for t in all_terms if t.lower() in text.lower()
        )
        self.lbl_stats.configure(
            text=f"🔬 {found} terme(s) médical(aux) détecté(s)"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Actions boutons
    # ──────────────────────────────────────────────────────────────────────────

    def _copy_text(self):
        text = self.txt_main.get("1.0", "end-1c")
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text)
            self._set_status("📋 Texte copié dans le presse-papiers.")

    def _save_text(self):
        text = self.txt_main.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showinfo("Vide", "Aucun texte à sauvegarder.")
            return
        filename = f"dictee_{datetime.now():%Y%m%d_%H%M%S}.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=filename,
            filetypes=[("Fichier texte", "*.txt"), ("Tous", "*.*")],
        )
        if path:
            Path(path).write_text(text, encoding="utf-8")
            self._set_status(f"💾 Sauvegardé : {path}")

    def _clear_text(self):
        if messagebox.askyesno("Effacer", "Effacer tout le texte ?"):
            self.txt_main.delete("1.0", "end")
            self.transcription.clear()
            self.lbl_words.configure(text="0 mots")
            self.lbl_stats.configure(text="")
            self._set_status("🗑  Texte effacé.")

    # ──────────────────────────────────────────────────────────────────────────
    # Utilitaires
    # ──────────────────────────────────────────────────────────────────────────

    def _set_status(self, message: str):
        self.status_var.set(f"  {message}")

    def _on_close(self):
        if self.is_recording:
            self._stop_recording()
        self.destroy()


# ─── Point d'entrée ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DictéeRadio — Interface Tkinter")
    parser.add_argument(
        "--model", default="vosk-model-fr-0.22",
        help="Chemin vers le dossier du modèle Vosk"
    )
    args = parser.parse_args()

    app = DicteeVocaleApp(model_path=args.model)
    app.mainloop()

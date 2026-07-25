import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import logging
import time
from typing import Optional

import config
from recognizer import MedicalSpeechRecognizer
from microphone import MicrophoneManager
from text_injector import inject_text, reset_injector

# Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Palette de couleurs professionnelle
THEME = {
    "bg":            "#0f0f12",
    "panel":         "#1a1a1e",
    "panel2":        "#16161a",
    "accent":        "#4f46e5",
    "accent_hover":  "#4338ca",
    "danger":        "#ef4444",
    "danger_hover":  "#dc2626",
    "success":       "#10b981",
    "success_hover": "#059669",
    "warning":       "#f59e0b",
    "text":          "#f3f4f6",
    "text_dim":      "#9ca3af",
    "text_partial":  "#60a5fa",   # bleu clair pour le texte en cours
    "border":        "#2d2d34",
    "text_area_bg":  "#0d0d10",
}


class DicteeMedicaleGUI(tk.Tk):
    """
    Interface graphique de dictée vocale médicale.
    Affiche tout le texte transcrit dans une grande zone de texte scrollable.
    """

    def __init__(self, recognizer: MedicalSpeechRecognizer, mic_manager: MicrophoneManager):
        super().__init__()
        self.recognizer  = recognizer
        self.mic_manager = mic_manager

        self.audio_queue: queue.Queue[bytes] = queue.Queue()
        self.is_listening   = False
        self.inject_enabled = tk.BooleanVar(value=False)   # injection désactivée par défaut
        self.recognition_thread: Optional[threading.Thread] = None

        # Texte accumulé (sans le partiel courant)
        self._accumulated_text = ""
        # Longueur du texte partiel affiché dans la zone de texte
        self._partial_len = 0

        self._setup_window()
        self._create_widgets()

        self.update_status("Chargement...", is_error=False)
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="disabled")

        self.after(100, self._async_load_model)

    # ─── Configuration de la fenêtre ──────────────────────────────────────────

    def _setup_window(self) -> None:
        self.title("🏥 Dictée Médicale IA")
        self.configure(bg=THEME["bg"])
        self.wm_attributes("-topmost", True)
        self.resizable(True, True)
        self.minsize(480, 520)

        w, h = 560, 620
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = max(10, (sh - h) // 2 - 60)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─── Création des widgets ─────────────────────────────────────────────────

    def _create_widgets(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TProgressbar", thickness=6,
                        troughcolor=THEME["panel"], background=THEME["accent"])
        style.configure("TCheckbutton",
                        background=THEME["bg"], foreground=THEME["text_dim"],
                        font=("Segoe UI", 9))

        # ── En-tête ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=THEME["panel"],
                       highlightbackground=THEME["border"], highlightthickness=1)
        hdr.pack(fill="x", padx=10, pady=(10, 4))

        tk.Label(hdr, text="🏥  Dictée Médicale IA",
                 font=("Segoe UI", 13, "bold"),
                 fg=THEME["text"], bg=THEME["panel"]).pack(side="left", padx=12, pady=8)

        self.lbl_mic_badge = tk.Label(
            hdr, text="MIC OFF",
            font=("Segoe UI", 8, "bold"),
            fg=THEME["text_dim"], bg=THEME["bg"],
            padx=7, pady=3, relief="flat")
        self.lbl_mic_badge.pack(side="right", padx=10, pady=8)

        # ── Statut + barre volume ─────────────────────────────────────────────
        sf = tk.Frame(self, bg=THEME["bg"])
        sf.pack(fill="x", padx=12, pady=(4, 2))

        self.lbl_status = tk.Label(sf, text="Statut : Prêt",
                                   font=("Segoe UI", 9),
                                   fg=THEME["text_dim"], bg=THEME["bg"], anchor="w")
        self.lbl_status.pack(side="left", fill="x", expand=True)

        self.vol_bar = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.vol_bar.pack(fill="x", padx=12, pady=(0, 6))

        # ── Boutons Activer / Arrêter ─────────────────────────────────────────
        bf = tk.Frame(self, bg=THEME["bg"])
        bf.pack(fill="x", padx=12, pady=(0, 6))

        self.btn_start = self._make_btn(
            bf, "🎤  Activer Micro", THEME["success"], THEME["success_hover"],
            self.start_listening)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_stop = self._make_btn(
            bf, "🛑  Arrêter Micro", THEME["danger"], THEME["danger_hover"],
            self.stop_listening)
        self.btn_stop.pack(side="right", fill="x", expand=True, padx=(4, 0))

        # ── Options (injection + effacer + copier) ────────────────────────────
        of = tk.Frame(self, bg=THEME["bg"])
        of.pack(fill="x", padx=12, pady=(0, 6))

        self.chk_inject = ttk.Checkbutton(
            of,
            text="💉 Injecter dans l'app active",
            variable=self.inject_enabled,
            style="TCheckbutton")
        self.chk_inject.pack(side="left")

        btn_copy = tk.Button(
            of, text="📋 Copier", font=("Segoe UI", 8),
            bg=THEME["panel"], fg=THEME["text_dim"],
            activebackground=THEME["border"], activeforeground=THEME["text"],
            relief="flat", bd=0, cursor="hand2", padx=8, pady=3,
            command=self._copy_text)
        btn_copy.pack(side="right", padx=(4, 0))

        btn_clear = tk.Button(
            of, text="🗑️ Effacer", font=("Segoe UI", 8),
            bg=THEME["panel"], fg=THEME["text_dim"],
            activebackground=THEME["border"], activeforeground=THEME["text"],
            relief="flat", bd=0, cursor="hand2", padx=8, pady=3,
            command=self._clear_text)
        btn_clear.pack(side="right")

        # ── Grande zone de texte ──────────────────────────────────────────────
        txt_frame = tk.LabelFrame(
            self, text="  📝 Transcription  ",
            font=("Segoe UI", 9, "bold"),
            fg=THEME["text_dim"], bg=THEME["panel"],
            highlightbackground=THEME["border"], highlightthickness=1, bd=0)
        txt_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.txt_area = tk.Text(
            txt_frame,
            font=("Segoe UI", 12),
            fg=THEME["text"],
            bg=THEME["text_area_bg"],
            insertbackground=THEME["accent"],
            selectbackground=THEME["accent"],
            relief="flat", bd=0,
            wrap="word",
            state="disabled",
            padx=12, pady=10)

        scrollbar = ttk.Scrollbar(txt_frame, command=self.txt_area.yview)
        self.txt_area.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.txt_area.pack(fill="both", expand=True)

        # Tags de mise en forme
        self.txt_area.tag_configure("final",   foreground=THEME["text"],         font=("Segoe UI", 12))
        self.txt_area.tag_configure("partial", foreground=THEME["text_partial"], font=("Segoe UI", 12, "italic"))
        self.txt_area.tag_configure("hint",    foreground=THEME["text_dim"],     font=("Segoe UI", 10, "italic"))

        # Message d'accueil
        self._write_hint("Parlez après avoir cliqué sur «Activer Micro»...")

    # ─── Helpers UI ───────────────────────────────────────────────────────────

    def _make_btn(self, parent, text, bg, bg_hover, cmd):
        btn = tk.Button(parent, text=text,
                        font=("Segoe UI", 10, "bold"),
                        bg=bg, fg=THEME["text"],
                        activebackground=bg_hover, activeforeground=THEME["text"],
                        relief="flat", bd=0, cursor="hand2",
                        padx=10, pady=9, command=cmd)
        btn.bind("<Enter>", lambda e: btn.configure(bg=bg_hover))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn

    def _write_hint(self, msg: str) -> None:
        self.txt_area.configure(state="normal")
        self.txt_area.delete("1.0", "end")
        self.txt_area.insert("end", msg, "hint")
        self.txt_area.configure(state="disabled")

    def _clear_text(self) -> None:
        self._accumulated_text = ""
        self._partial_len = 0
        self._write_hint("Zone effacée. Parlez pour commencer...")

    def _copy_text(self) -> None:
        content = self.txt_area.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update_status("Texte copié !", is_error=False)
            self.after(2000, lambda: self.update_status("Écoute active..." if self.is_listening else "Prêt"))

    # ─── Zone de texte : mise à jour ─────────────────────────────────────────

    def _refresh_text_area(self, partial: str = "") -> None:
        """Réécrit la zone de texte : texte accumulé (final) + texte partiel en cours."""
        self.txt_area.configure(state="normal")
        self.txt_area.delete("1.0", "end")

        if self._accumulated_text:
            self.txt_area.insert("end", self._accumulated_text, "final")

        if partial:
            self.txt_area.insert("end", partial, "partial")

        self.txt_area.see("end")
        self.txt_area.configure(state="disabled")

    def update_last_text(self, text: str, is_final: bool) -> None:
        """Appelé depuis le thread de reconnaissance (via self.after)."""
        if is_final:
            # Ajouter le texte final à l'accumulateur
            if self._accumulated_text and not self._accumulated_text.endswith("\n"):
                self._accumulated_text += text + " "
            else:
                self._accumulated_text += text + " "
            self._refresh_text_area(partial="")
        else:
            # Afficher le texte partiel sans l'accumuler
            self._refresh_text_area(partial=text + "…")

    # ─── Chargement modèle ────────────────────────────────────────────────────

    def _async_load_model(self) -> None:
        def load():
            try:
                self.update_status("Chargement du modèle Vosk...", is_error=False)
                self.recognizer.load_model()
                self.after(0, self._on_model_loaded)
            except Exception as e:
                self.after(0, lambda err=str(e): self._on_model_error(err))
        threading.Thread(target=load, daemon=True).start()

    def _on_model_loaded(self) -> None:
        self.update_status("Prêt", is_error=False)
        self.btn_start.configure(state="normal")
        self.lbl_mic_badge.configure(text="PRÊT", fg=THEME["success"])

    def _on_model_error(self, err_msg: str) -> None:
        self.update_status("Erreur de modèle", is_error=True)
        self.lbl_mic_badge.configure(text="ERR", fg=THEME["danger"])
        messagebox.showerror(
            "Erreur de modèle Vosk",
            f"Impossible de charger le modèle Vosk.\n\nDétails :\n{err_msg}\n\n"
            f"Vérifiez que le dossier {config.MODEL_PATH} est complet.")

    # ─── Statut ───────────────────────────────────────────────────────────────

    def update_status(self, text: str, is_error: bool = False) -> None:
        color = THEME["danger"] if is_error else THEME["text_dim"]
        self.lbl_status.configure(text=f"Statut : {text}", fg=color)

    # ─── Contrôle micro ──────────────────────────────────────────────────────

    def start_listening(self) -> None:
        if self.is_listening:
            return
        self.is_listening = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.lbl_mic_badge.configure(text="🔴 ON", fg=THEME["danger"])
        self.update_status("Écoute active...")

        # Vider la queue audio
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        reset_injector()

        # Si la zone est vide, effacer le message d'accueil
        if not self._accumulated_text:
            self.txt_area.configure(state="normal")
            self.txt_area.delete("1.0", "end")
            self.txt_area.configure(state="disabled")

        try:
            self.mic_manager.start_stream(self._audio_callback)
        except Exception as e:
            self.is_listening = False
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.lbl_mic_badge.configure(text="PRÊT", fg=THEME["success"])
            self.update_status("Erreur micro", is_error=True)
            messagebox.showerror("Erreur microphone", f"Impossible d'ouvrir le micro :\n{e}")
            return

        self.recognition_thread = threading.Thread(
            target=self._recognition_loop, daemon=True)
        self.recognition_thread.start()

    def stop_listening(self) -> None:
        if not self.is_listening:
            return
        self.is_listening = False
        self.mic_manager.stop_stream()
        reset_injector()

        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.lbl_mic_badge.configure(text="PRÊT", fg=THEME["success"])
        self.update_status("Prêt")
        self.vol_bar.configure(value=0)
        # Effacer le partiel restant
        self._refresh_text_area(partial="")
        logging.info("Écoute arrêtée.")

    # ─── Callbacks audio / reconnaissance ────────────────────────────────────

    def _audio_callback(self, in_data: bytes) -> None:
        self.audio_queue.put(in_data)
        vol = self.mic_manager.get_rms_volume(in_data)
        self.after(0, lambda v=vol: self.vol_bar.configure(value=v))

    def _recognition_loop(self) -> None:
        logging.info("Début de la boucle de reconnaissance vocale.")
        while self.is_listening:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                is_final, text = self.recognizer.process_audio_chunk(chunk)
                if text:
                    formatted = self.recognizer.format_text(text, is_partial=not is_final)

                    # Injection dans l'app active (si activée)
                    if self.inject_enabled.get():
                        inject_text(formatted, is_partial=not is_final)

                    # Affichage dans la zone de texte de l'app
                    self.after(0, self.update_last_text, formatted, is_final)

            except Exception as e:
                logging.error(f"Erreur dans la boucle de reconnaissance : {e}")
                self.after(0, lambda err=str(e): self.update_status(
                    f"Erreur : {err[:30]}", is_error=True))

        logging.info("Fin de la boucle de reconnaissance vocale.")

    # ─── Fermeture ────────────────────────────────────────────────────────────

    def _on_close(self) -> None:
        self.is_listening = False
        self.mic_manager.terminate()
        self.destroy()

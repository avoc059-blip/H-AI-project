"""
sos_window.py — Fenêtre d'urgence Tkinter pour H-Ai Hospital System
Lancée dans un thread séparé depuis app.py via la route /sos
"""

import tkinter as tk
from tkinter import font as tkfont


def open_sos():
    """Ouvre la fenêtre d'alerte d'urgence Tkinter."""

    root = tk.Tk()
    root.title("🚨 Alerte d'Urgence — H-Ai")
    root.resizable(False, False)
    root.configure(bg="#1a0a0a")

    # ── Centrer la fenêtre sur l'écran ──────────────────────
    width, height = 480, 370
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

    # ── Polices ─────────────────────────────────────────────
    font_title  = tkfont.Font(family="Helvetica", size=16, weight="bold")
    font_label  = tkfont.Font(family="Helvetica", size=11)
    font_info   = tkfont.Font(family="Helvetica", size=12, weight="bold")
    font_msg    = tkfont.Font(family="Helvetica", size=10, slant="italic")
    font_btn    = tkfont.Font(family="Helvetica", size=11, weight="bold")

    # ── Bande rouge en haut ──────────────────────────────────
    banner = tk.Frame(root, bg="#dc2626", height=8)
    banner.pack(fill="x")

    # ── Icône + Titre ────────────────────────────────────────
    tk.Label(
        root, text="🚨", font=tkfont.Font(size=40),
        bg="#1a0a0a", fg="#ef4444"
    ).pack(pady=(18, 0))

    tk.Label(
        root, text="Emergency Alert",
        font=font_title, bg="#1a0a0a", fg="#ef4444"
    ).pack(pady=(4, 0))

    tk.Frame(root, bg="#7f1d1d", height=1).pack(fill="x", padx=40, pady=12)

    # ── Informations d'urgence ───────────────────────────────
    info_frame = tk.Frame(root, bg="#2a0a0a", bd=0, relief="flat",
                          highlightbackground="#7f1d1d", highlightthickness=1)
    info_frame.pack(padx=30, fill="x")

    def info_row(icon, label, value):
        row = tk.Frame(info_frame, bg="#2a0a0a")
        row.pack(fill="x", padx=16, pady=6)
        tk.Label(row, text=icon, font=font_label,
                 bg="#2a0a0a", fg="#fca5a5", width=2).pack(side="left")
        tk.Label(row, text=label, font=font_label,
                 bg="#2a0a0a", fg="#fca5a5").pack(side="left")
        tk.Label(row, text=value, font=font_info,
                 bg="#2a0a0a", fg="#FAF5F5").pack(side="left", padx=(6, 0))

    info_row("📞", "Numéro d'urgence :", "150")
    info_row("🏥", "Contact hôpital :", "+212 XXX XXX XXX")

    tk.Frame(root, bg="#7f1d1d", height=1).pack(fill="x", padx=30, pady=(12, 6))

    # ── Message ──────────────────────────────────────────────
    tk.Label(
        root,
        text="Veuillez contacter immédiatement\nles services d'urgence.",
        font=font_msg, bg="#1a0a0a", fg="#fbbf24",
        justify="center"
    ).pack(pady=(2, 16))

    # ── Boutons ──────────────────────────────────────────────
    btn_frame = tk.Frame(root, bg="#1a0a0a")
    btn_frame.pack(pady=(0, 20))

    called_var = tk.BooleanVar(value=False)

    def simulate_call():
        """Simulation d'appel — affiche une confirmation dans le bouton."""
        if not called_var.get():
            called_var.set(True)
            btn_call.config(text="✅ Appel en cours… (150)", state="disabled",
                            bg="#15803d", activebackground="#15803d")

    def close_window():
        root.destroy()

    btn_call = tk.Button(
        btn_frame,
        text="📞  Appeler (150)",
        font=font_btn,
        bg="#dc2626", fg="#090808",
        activebackground="#b91c1c", activeforeground="#fcf9f9",
        relief="flat", bd=0,
        padx=18, pady=10,
        cursor="hand2",
        command=simulate_call
    )
    btn_call.grid(row=0, column=0, padx=10)

    btn_close = tk.Button(
        btn_frame,
        text="✖  Fermer",
        font=font_btn,
        bg="#374151", fg="#040404",
        activebackground="#4b5563", activeforeground="#ffffff",
        relief="flat", bd=0,
        padx=18, pady=10,
        cursor="hand2",
        command=close_window
    )
    btn_close.grid(row=0, column=1, padx=10)

    # ── Bande rouge en bas ───────────────────────────────────
    tk.Frame(root, bg="#dc2626", height=4).pack(fill="x", side="bottom")

    root.mainloop()


# ── Test autonome ────────────────────────────────────────────
if __name__ == "__main__":
    open_sos()

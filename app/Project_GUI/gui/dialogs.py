# gui/dialogs.py
"""
@file dialogs.py
@brief Enthält benutzerdefinierte Dialoge (z.B. SSH-Verbindungsdialog).
"""

import tkinter as tk
from ttkbootstrap import Style, ttk

class CustomSSHDialog(tk.Toplevel):
    """
    @class CustomSSHDialog
    @brief Einfacher Dialog, um Hostname, Benutzername und Passwort für SSH abzufragen.
    """
    def __init__(self, parent, saved_hostname, saved_username, saved_password):
        super().__init__(parent)
        self.title("SSH-Verbindung")
        self.geometry("400x220")

        self.style = Style(theme="darkly")
        self.transient(parent)
        self.grab_set()

        self.result = None

        self.hostname_var = tk.StringVar(value=saved_hostname)
        self.username_var = tk.StringVar(value=saved_username)
        self.password_var = tk.StringVar(value=saved_password)

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Hostname:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        hostname_entry = ttk.Entry(self, textvariable=self.hostname_var)
        hostname_entry.grid(row=0, column=1, padx=10, pady=10, sticky="we")

        ttk.Label(self, text="Benutzername:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        username_entry = ttk.Entry(self, textvariable=self.username_var)
        username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="we")

        ttk.Label(self, text="Passwort:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        password_entry = ttk.Entry(self, textvariable=self.password_var, show="*")
        password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="we")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 20))

        ok_button = ttk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.grid(row=0, column=0, padx=5)

        cancel_button = ttk.Button(button_frame, text="Abbrechen", command=self.on_cancel)
        cancel_button.grid(row=0, column=1, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_ok(self):
        self.result = (
            self.hostname_var.get(),
            self.username_var.get(),
            self.password_var.get()
        )
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

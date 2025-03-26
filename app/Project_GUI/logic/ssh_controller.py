# logic/ssh_controller.py
"""
@file ssh_controller.py
@brief Stellt eine SSH-Verbindung her und ermöglicht das Senden von Kommandos.
"""

import paramiko
from tkinter import messagebox

class SSHController:
    """
    @class SSHController
    @brief Kapselt eine SSH-Verbindung mittels Paramiko zum Ausführen von Befehlen.
    """
    def __init__(self):
        self.client = None

    def connect(self, hostname, username, password):
        """
        @fn connect(hostname, username, password)
        @brief Baut eine SSH-Verbindung auf.
        @param hostname: Hostname oder IP
        @param username: Benutzername
        @param password: Passwort
        @return True bei Erfolg, sonst False
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname, username=username, password=password)
            print(f"Verbunden mit {hostname}")
            self.client.exec_command("sudo pigpiod")
            return True
        except Exception as e:
            print(f"SSH-Verbindung fehlgeschlagen: {e}")
            messagebox.showerror("Verbindung fehlgeschlagen", str(e))
            return False

    def send_command(self, cmd):
        """
        @fn send_command(cmd)
        @brief Führt ein Kommando auf dem SSH-Server aus und gibt die Ausgabe zurück.
        @param cmd: Shell-Kommando
        @return Ausgabe des Befehls (String)
        """
        if not self.client:
            print("SSH-Client ist nicht verbunden.")
            return ""
        try:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            out = stdout.read().decode()
            err = stderr.read().decode()
            if err.strip():
                print(f"Fehler: {err.strip()}")
            return out
        except Exception as e:
            print(f"Fehler beim Ausführen des SSH-Kommandos: {e}")
            return ""

    def close(self):
        """
        @fn close()
        @brief Beendet die SSH-Verbindung.
        """
        if self.client:
            self.client.close()
            print("SSH-Verbindung geschlossen.")
            self.client = None

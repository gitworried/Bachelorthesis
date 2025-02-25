# sensor_gui/logic/ssh_controller.py

import paramiko
from tkinter import messagebox

class SSHController:
    def __init__(self):
        self.client = None

    def connect(self, hostname, username, password):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname, username=username, password=password)
            print(f"Connected to {hostname}")
            # Attempt to start pigpiod
            stdin, stdout, stderr = self.client.exec_command("sudo pigpiod")
            return True
        except Exception as e:
            print(f"SSH connection failed: {e}")
            messagebox.showerror("Connection Failed", str(e))
            return False

    def send_command(self, cmd):
        if not self.client:
            print("SSH client is not connected")
            return ""
        try:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            out = stdout.read().decode()
            err = stderr.read().decode()
            if err.strip():
                print(f"Error: {err.strip()}")
            return out
        except Exception as e:
            print(f"SSH command error: {e}")
            return ""

    def close(self):
        if self.client:
            self.client.close()
            print("SSH connection closed")
            self.client = None

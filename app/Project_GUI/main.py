# main.py
"""
@file main.py
@brief Startpunkt der GUI-Anwendung. Erstellt das Hauptfenster und startet die Tk-Hauptschleife.
"""

import tkinter as tk
from gui.main_window import SensorGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

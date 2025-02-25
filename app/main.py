# sensor_gui/main.py

import tkinter as tk
from gui.main_window import SensorGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

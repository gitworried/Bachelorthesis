# plots/live_plots.py
"""
@file live_plots.py
@brief Ein Beispielmodul für Live-Plots von Temperatur, Feuchtigkeit und Druck mit matplotlib in Tkinter.
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from logic.utils import get_sensor_color
from logic.data_processing import style_plot

class LivePlot:
    """
    @class LivePlot
    @brief Stellt drei Subplots (Temperatur, Feuchtigkeit, Druck) in einem Tk-Frame dar.
    """
    def __init__(self, parent):
        """
        @fn __init__(...)
        @brief Konstruktor: Erzeugt Subplots und bindet sie in das Tk-UI ein.
        @param parent: tk-Widget (z.B. Frame)
        """
        self.frame = tk.Frame(parent)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.fig, (self.ax_temp, self.ax_feuchte, self.ax_druck) = plt.subplots(3, 1, figsize=(10, 6))
        self.fig.subplots_adjust(hspace=0.5, left=0.1, right=0.95, top=0.95, bottom=0.08)

        style_plot(self.ax_temp, "Temperatur", "°C")
        style_plot(self.ax_feuchte, "Feuchtigkeit", "%")
        style_plot(self.ax_druck, "Druck", "hPa")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

    def update_plots(self, zeit_daten, temp_daten, feuchte_daten, druck_daten):
        """
        @fn update_plots(zeit_daten, temp_daten, feuchte_daten, druck_daten)
        @brief Aktualisiert die Subplots mit neuen Daten.
        @param zeit_daten: Liste/Array mit Zeitwerten
        @param temp_daten: Liste/Array mit Temperaturwerten
        @param feuchte_daten: Liste/Array mit Feuchtigkeitswerten
        @param druck_daten: Liste/Array mit Druckwerten
        """
        self.ax_temp.clear()
        self.ax_feuchte.clear()
        self.ax_druck.clear()

        style_plot(self.ax_temp, "Temperatur", "°C")
        style_plot(self.ax_feuchte, "Feuchtigkeit", "%")
        style_plot(self.ax_druck, "Druck", "hPa")

        self.ax_temp.plot(zeit_daten, temp_daten, color=get_sensor_color("°C"))
        self.ax_feuchte.plot(zeit_daten, feuchte_daten, color=get_sensor_color("%"))
        self.ax_druck.plot(zeit_daten, druck_daten, color=get_sensor_color("hPa"))

        self.ax_temp.set_xlim(left=0)
        self.ax_feuchte.set_xlim(left=0)
        self.ax_druck.set_xlim(left=0)

        self.canvas.draw_idle()

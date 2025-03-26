# gui/bme280_tab.py
"""
@file bme280_tab.py
@brief Ein Tab zur Anzeige von BME280-Daten (Temperatur, Feuchtigkeit, Druck) 
       sowie zugehörigen Live-Plots. Enthält auch Steuerungs-Bereiche für Heizung und Lüfter.
"""

import tkinter as tk
from ttkbootstrap import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config.settings import THEME_COLORS
from logic.data_processing import style_plot

class BME280Tab(ttk.Frame):
    """
    @class BME280Tab
    @brief Zeigt BME280-Werte (Temperatur, Feuchtigkeit, Druck) + Plots an.
    """
    def __init__(self, parent, temperature_data, humidity_data, pressure_data, time_data):
        """
        @fn __init__(...)
        @param parent: z.B. Notebook
        @param temperature_data, humidity_data, pressure_data: deque
        @param time_data: deque
        """
        super().__init__(parent, padding=10, style='TLabelframe')
        self.parent = parent
        self.temperature_data = temperature_data
        self.humidity_data    = humidity_data
        self.pressure_data    = pressure_data
        self.time_data        = time_data

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sensordaten-Bereich
        self.data_frame = ttk.LabelFrame(self, text="Sensordaten", padding=10)
        self.data_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.columnconfigure(1, weight=1)
        self.data_frame.columnconfigure(2, weight=1)
        self.data_frame.rowconfigure(0, weight=1)

        self.temp_label = self.create_sensor_box(self.data_frame, "Temperatur", 0)
        self.humidity_label = self.create_sensor_box(self.data_frame, "Feuchtigkeit", 1)
        self.pressure_label = self.create_sensor_box(self.data_frame, "Druck", 2)

        # Steuerbereich rechts
        self.control_frame = ttk.LabelFrame(self, text="Steuerungsbereich", padding=10)
        self.control_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.control_frame.columnconfigure(0, weight=1)

        # Plot-Bereich unten
        self.plot_frame = ttk.LabelFrame(self, text="Live-Plots", padding=10)
        self.plot_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.plot_frame.rowconfigure(0, weight=1)
        self.plot_frame.columnconfigure(0, weight=1)

        self.fig, (self.ax_temp, self.ax_humidity, self.ax_pressure) = plt.subplots(3, 1, figsize=(12, 6))
        self.fig.patch.set_facecolor(THEME_COLORS["frame_bg_color"])

        style_plot(self.ax_temp,     "Temperatur", "°C")
        style_plot(self.ax_humidity, "Feuchtigkeit",    "%")
        style_plot(self.ax_pressure, "Druck",    "hPa")
        self.fig.subplots_adjust(hspace=0.6, left=0.15, right=0.9, top=0.95, bottom=0.1)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        self.loading_label = tk.Label(
            self.plot_frame,
            text="Lade...",
            font=("Helvetica", 16),
            bg=THEME_COLORS["frame_bg_color"],
            fg=THEME_COLORS["text_color"]
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def create_sensor_box(self, parent, title, column):
        """
        @fn create_sensor_box(parent, title, column)
        @brief Erzeugt ein LabelFrame (z.B. "Temperatur") mit einem Label, das den Messwert anzeigt.
        """
        box = ttk.LabelFrame(parent, text=title, padding=10)
        box.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
        label = tk.Label(
            box,
            text="Lade...",
            font=("Helvetica", 16, "bold"),
            anchor='center',
            bg=THEME_COLORS["frame_bg_color"],
            fg=THEME_COLORS["text_color"]
        )
        label.pack(fill='both', expand=True)
        return label

    def remove_loading_label(self):
        """
        @fn remove_loading_label()
        @brief Entfernt das "Lade..."-Overlay, wenn Daten vorliegen.
        """
        if self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None

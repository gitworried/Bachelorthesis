# GUI/gui/bme280_tab.py

import tkinter as tk
from ttkbootstrap import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config.settings import THEME_COLORS
from logic.data_processing import style_plot

class BME280Tab(ttk.Frame):
    def __init__(self, parent, temperature_data, humidity_data, pressure_data, time_data):
        super().__init__(parent, padding=10, style='TLabelframe')
        self.parent = parent
        self.temperature_data = temperature_data
        self.humidity_data    = humidity_data
        self.pressure_data    = pressure_data
        self.time_data        = time_data

        # Grid layout: row 0 => sensor & control, row 1 => plot
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sensor Data Frame
        self.data_frame = ttk.LabelFrame(self, text="Sensor Data", padding=10)
        self.data_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.columnconfigure(1, weight=1)
        self.data_frame.columnconfigure(2, weight=1)
        self.data_frame.rowconfigure(0, weight=1)

        self.temp_label = self.create_sensor_box(self.data_frame, "Temperature", 0)
        self.humidity_label = self.create_sensor_box(self.data_frame, "Humidity", 1)
        self.pressure_label = self.create_sensor_box(self.data_frame, "Pressure", 2)

        # Control Frame to the right
        self.control_frame = ttk.LabelFrame(self, text="Control Panel", padding=10)
        self.control_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.control_frame.columnconfigure(0, weight=1)

        # Plot Frame below
        self.plot_frame = ttk.LabelFrame(self, text="Live Plots", padding=10)
        self.plot_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.plot_frame.rowconfigure(0, weight=1)
        self.plot_frame.columnconfigure(0, weight=1)

        self.fig, (self.ax_temp, self.ax_humidity, self.ax_pressure) = plt.subplots(3, 1, figsize=(12, 6))
        self.fig.patch.set_facecolor(THEME_COLORS["frame_bg_color"])

        style_plot(self.ax_temp,     "Temperature", "°C")
        style_plot(self.ax_humidity, "Humidity",    "%")
        style_plot(self.ax_pressure, "Pressure",    "hPa")
        self.fig.subplots_adjust(hspace=0.6, left=0.15, right=0.9, top=0.95, bottom=0.1)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        # "Loading..." label
        self.loading_label = tk.Label(
            self.plot_frame,
            text="Loading...",
            font=("Helvetica", 16),
            bg=THEME_COLORS["frame_bg_color"],
            fg=THEME_COLORS["text_color"]
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def create_sensor_box(self, parent, title, column):
        box = ttk.LabelFrame(parent, text=title, padding=10)
        box.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
        label = tk.Label(
            box,
            text="Loading...",
            font=("Helvetica", 16, "bold"),
            anchor='center',
            bg=THEME_COLORS["frame_bg_color"],
            fg=THEME_COLORS["text_color"]
        )
        label.pack(fill='both', expand=True)
        return label

    def remove_loading_label(self):
        if self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None

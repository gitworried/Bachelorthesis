# plots/live_plots.py

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from logic.utils import style_plot
from config.settings import PLOT_STYLES

class LivePlot:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # Adjusted figure size and margins
        self.fig, (self.ax_temp, self.ax_humidity, self.ax_pressure) = plt.subplots(3, 1, figsize=(10, 6))
        self.fig.patch.set_facecolor(PLOT_STYLES["background_color"])
        self.fig.subplots_adjust(hspace=0.5, left=0.1, right=0.95, top=0.95, bottom=0.08)

        style_plot(self.ax_temp, "Temperature", "°C")
        style_plot(self.ax_humidity, "Humidity", "%")
        style_plot(self.ax_pressure, "Pressure", "hPa")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

    def update_plots(self, time_data, temp_data, humidity_data, pressure_data):
        self.ax_temp.clear()
        self.ax_humidity.clear()
        self.ax_pressure.clear()

        style_plot(self.ax_temp, "Temperature", "°C")
        style_plot(self.ax_humidity, "Humidity", "%")
        style_plot(self.ax_pressure, "Pressure", "hPa")

        # Plot data
        self.ax_temp.plot(time_data, temp_data, color=PLOT_STYLES["temperature_color"])
        self.ax_humidity.plot(time_data, humidity_data, color=PLOT_STYLES["humidity_color"])
        self.ax_pressure.plot(time_data, pressure_data, color=PLOT_STYLES["pressure_color"])

        # Set x-axis limits
        self.ax_temp.set_xlim(left=0)
        self.ax_humidity.set_xlim(left=0)
        self.ax_pressure.set_xlim(left=0)

        # Draw the updated canvas
        self.canvas.draw_idle()

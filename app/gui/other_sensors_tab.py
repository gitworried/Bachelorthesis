# sensor_gui/gui/other_sensors_tab.py

import tkinter as tk
from ttkbootstrap import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config.settings import THEME_COLORS
from logic.data_processing import style_plot, moving_average
from logic.utils import get_sensor_color

class OtherSensorsTab(ttk.Frame):
    def __init__(self, parent, other_sensor_vars, other_sensor_data, time_data_other, other_sensor_conf):
        super().__init__(parent, style='TLabelframe')
        self.parent = parent
        self.other_sensor_vars = other_sensor_vars
        self.other_sensor_data = other_sensor_data
        self.time_data_other   = time_data_other
        self.other_sensor_conf = other_sensor_conf

        self.other_sensors_notebook = ttk.Notebook(self, style='TNotebook')
        self.other_sensors_notebook.pack(fill='both', expand=True, padx=5, pady=5)

        self.other_sensors_tabs = []

    def update_active_sensors(self, active_sensors):
        for tab_id in self.other_sensors_notebook.tabs():
            self.other_sensors_notebook.forget(tab_id)

        self.other_sensors_tabs = []
        if len(active_sensors) == 0:
            return

        chunked = [active_sensors[i:i+3] for i in range(0, len(active_sensors), 3)]
        for chunk_index, chunk in enumerate(chunked):
            frame = ttk.Frame(self.other_sensors_notebook, style='TLabelframe')
            frame.rowconfigure(0, weight=0)
            frame.rowconfigure(1, weight=1)
            frame.columnconfigure(0, weight=1)

            data_frame = ttk.LabelFrame(frame, text="Sensor Data", padding=10)
            data_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

            for i in range(len(chunk)):
                data_frame.columnconfigure(i, weight=1)

            sensor_labels = {}
            sensor_colors = {}

            for i, sensor_key in enumerate(chunk):
                unit = self.other_sensor_conf[sensor_key]["unit"]
                color = get_sensor_color(unit)
                box = ttk.LabelFrame(data_frame, text=self.other_sensor_conf[sensor_key]["name"], padding=10)
                box.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
                label = tk.Label(
                    box,
                    text="Loading...",
                    font=("Helvetica", 16, "bold"),
                    bg=THEME_COLORS["frame_bg_color"],
                    fg=THEME_COLORS["text_color"]
                )
                label.pack(fill='both', expand=True)

                sensor_labels[sensor_key] = label
                sensor_colors[sensor_key] = color

            plot_frame = ttk.LabelFrame(frame, text="Live Plots", padding=10)
            plot_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            plot_frame.rowconfigure(0, weight=1)
            plot_frame.columnconfigure(0, weight=1)

            fig, axes = plt.subplots(len(chunk), 1, figsize=(12, 3 * len(chunk)), sharex=False)
            if len(chunk) == 1:
                axes = [axes]
            fig.patch.set_facecolor(THEME_COLORS["frame_bg_color"])

            for ax, s_key in zip(axes, chunk):
                unit = self.other_sensor_conf[s_key]["unit"]
                style_plot(ax, self.other_sensor_conf[s_key]["name"], unit)

            fig.subplots_adjust(hspace=0.6, left=0.15, right=0.9, top=0.95, bottom=0.1)

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

            self.other_sensors_tabs.append({
                'frame': frame,
                'sensors': chunk,
                'labels': sensor_labels,
                'colors': sensor_colors,
                'fig': fig,
                'axes': axes,
                'canvas': canvas
            })

            self.other_sensors_notebook.add(frame, text=f"Sensors {chunk_index + 1}")

    def update_other_sensor_data(self):
        """Called periodically to redraw sensor data + plots."""
        for tab_info in self.other_sensors_tabs:
            chunk = tab_info['sensors']
            labels = tab_info['labels']
            colors = tab_info['colors']
            fig = tab_info['fig']
            axes = tab_info['axes']
            canvas = tab_info['canvas']

            for ax, sensor_key in zip(axes, chunk):
                ax.clear()
                unit = self.other_sensor_conf[sensor_key]["unit"]
                style_plot(ax, self.other_sensor_conf[sensor_key]["name"], unit)

                data_arr = self.other_sensor_data[sensor_key]
                if len(data_arr) > 0:
                    current_val = data_arr[-1]
                    labels[sensor_key].config(text=f"{current_val:.2f} {unit}")
                    smooth = moving_average(data_arr)
                    n = len(smooth)
                    xs = list(self.time_data_other)[-n:]
                    c = colors[sensor_key]
                    ax.plot(xs, smooth, color=c)

            fig.subplots_adjust(hspace=0.6, left=0.15, right=0.9, top=0.95, bottom=0.1)
            canvas.draw_idle()

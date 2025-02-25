# sensor_gui/logic/data_processing.py

import numpy as np
from config.settings import THEME_COLORS

def moving_average(data, window_size=5):
    if len(data) < window_size:
        return list(data)
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def style_plot(ax, y_label, y_unit):
    ax.set_facecolor(THEME_COLORS["frame_bg_color"])
    ax.tick_params(colors=THEME_COLORS["text_color"])
    ax.xaxis.label.set_color(THEME_COLORS["text_color"])
    ax.yaxis.label.set_color(THEME_COLORS["text_color"])
    ax.grid(color=THEME_COLORS["grid_color"], linestyle="--", linewidth=0.5)
    ax.set_ylabel(f"{y_label} ({y_unit})", color=THEME_COLORS["text_color"], labelpad=30)
    ax.set_xlabel("Elapsed Time [s]", color=THEME_COLORS["text_color"])
    label = ax.yaxis.get_label()
    label.set_rotation(20)
    label.set_verticalalignment('center')
    ax.yaxis.set_label_coords(-0.11, 0.5)

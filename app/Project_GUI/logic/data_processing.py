# logic/data_processing.py
"""
@file data_processing.py
@brief Enthält Hilfsfunktionen zur Datenverarbeitung und zum Plot-Layout (Styling).
"""

import numpy as np
from config.settings import THEME_COLORS

def moving_average(daten, fenster=5):
    """
    @fn moving_average(daten, fenster)
    @brief Berechnet den gleitenden Mittelwert über das angegebene Fenster.
    @param daten: Array oder Liste von Werten
    @param fenster: Größe des Mittelwertfensters
    @return Liste mit gemittelten Werten
    """
    if len(daten) < fenster:
        return list(daten)
    return np.convolve(daten, np.ones(fenster)/fenster, mode='valid')

def style_plot(ax, y_label, einheit):
    """
    @fn style_plot(ax, y_label, einheit)
    @brief Setzt Hintergrund- und Achsenfarbe, Gitternetz sowie Achsenbeschriftung.
    @param ax: matplotlib-Achse
    @param y_label: Beschriftung (z.B. "Temperatur")
    @param einheit: Einheit (z.B. "°C")
    """
    ax.set_facecolor(THEME_COLORS["frame_bg_color"])
    ax.tick_params(colors=THEME_COLORS["text_color"])
    ax.xaxis.label.set_color(THEME_COLORS["text_color"])
    ax.yaxis.label.set_color(THEME_COLORS["text_color"])
    ax.grid(color=THEME_COLORS["grid_color"], linestyle="--", linewidth=0.5)
    ax.set_ylabel(f"{y_label} ({einheit})", color=THEME_COLORS["text_color"], labelpad=30)
    ax.set_xlabel("Verstrichene Zeit [s]", color=THEME_COLORS["text_color"])
    beschriftung = ax.yaxis.get_label()
    beschriftung.set_rotation(20)
    beschriftung.set_verticalalignment('center')
    ax.yaxis.set_label_coords(-0.11, 0.5)

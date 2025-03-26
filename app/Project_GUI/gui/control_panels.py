# gui/control_panels.py
"""
@file control_panels.py
@brief Enthält GUI-Panels für Heizung (An/Aus, Sollwert) und Lüfter (An/Aus, Geschwindigkeit).
"""

import tkinter as tk
from ttkbootstrap import ttk
from config.settings import GLOBAL_BUTTON_STYLE, GLOBAL_ENTRY_STYLE, GLOBAL_COMBOBOX_STYLE, TOGGLE_BOOTSTYLE

MAX_GESCHWINDIGKEIT = 5

class HeaterControlPanel(ttk.LabelFrame):
    """
    @class HeaterControlPanel
    @brief Panel mit Checkbutton für Heizung An/Aus und Eingabefeld für Solltemperatur.
    """
    def __init__(self, parent, toggle_heater_callback, set_heater_callback):
        """
        @fn __init__(...)
        @param parent: Übergeordnetes Widget
        @param toggle_heater_callback: Funktion, die Heizung An/Aus schaltet
        @param set_heater_callback: Funktion, die den Sollwert setzt
        """
        super().__init__(parent, text="Heizungssteuerung", padding=20)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)

        self.heater_var = tk.BooleanVar(value=False)
        self.heater_check = ttk.Checkbutton(
            self,
            text="Heizung An/Aus",
            variable=self.heater_var,
            bootstyle=TOGGLE_BOOTSTYLE,
            command=toggle_heater_callback,
            width=12
        )
        self.heater_check.grid(row=0, column=0, padx=5, pady=5, sticky="we")

        self.temp_set_entry = ttk.Entry(
            self,
            style=GLOBAL_ENTRY_STYLE,
            width=15
        )
        self.temp_set_entry.insert(0, "40")  # Standardwert
        self.temp_set_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        # Knopf mit kürzerer Beschriftung
        self.set_button = ttk.Button(
            self,
            text="Anwenden",  # Kürzerer Text
            style=GLOBAL_BUTTON_STYLE,
            command=set_heater_callback,
            width=10
        )
        self.set_button.grid(row=0, column=2, padx=5, pady=5, sticky="we")

    def get_heater_state(self):
        """
        @fn get_heater_state()
        @brief Gibt True/False zurück, ob die Heizung aktiv ist.
        """
        return self.heater_var.get()

    def set_heater_state(self, state: bool):
        """
        @fn set_heater_state(state)
        @brief Aktiviert/Deaktiviert den Heater-Checkbutton programmatisch.
        @param state: bool
        """
        self.heater_var.set(state)

    def get_temperature_value(self):
        """
        @fn get_temperature_value()
        @brief Liest den Text aus dem Eingabefeld.
        @return str
        """
        return self.temp_set_entry.get()


class FanControlPanel(ttk.LabelFrame):
    """
    @class FanControlPanel
    @brief Panel für den Lüfter mit An/Aus-Checkbutton und Combobox zur Geschwindigkeitswahl.
    """
    def __init__(self, parent, toggle_fan_callback, set_fan_speed_callback):
        """
        @fn __init__(...)
        @param parent: Übergeordnetes Widget
        @param toggle_fan_callback: Funktion für Lüfter An/Aus
        @param set_fan_speed_callback: Funktion, die den Lüfter-Speed setzt
        """
        super().__init__(parent, text="Lüftersteuerung", padding=20)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)

        self.fan_on_var = tk.BooleanVar(value=False)
        self.fan_on_check = ttk.Checkbutton(
            self,
            text="Lüfter An/Aus",
            variable=self.fan_on_var,
            bootstyle=TOGGLE_BOOTSTYLE,
            command=toggle_fan_callback,
            width=12
        )
        self.fan_on_check.grid(row=0, column=0, padx=5, pady=5, sticky="we")

        self.fan_speed_var = tk.StringVar()
        self.fan_speed_combobox = ttk.Combobox(
            self,
            textvariable=self.fan_speed_var,
            values=[str(i) for i in range(MAX_GESCHWINDIGKEIT + 1)],
            style=GLOBAL_COMBOBOX_STYLE,
            state='readonly',
            width=15
        )
        self.fan_speed_combobox.set("Lüftergeschwindigkeit wählen")
        self.fan_speed_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        # Knopf mit kürzerer Beschriftung
        self.set_fan_button = ttk.Button(
            self,
            text="Anwenden",  # Kürzerer Text
            style=GLOBAL_BUTTON_STYLE,
            command=set_fan_speed_callback,
            width=10
        )
        self.set_fan_button.grid(row=0, column=2, padx=5, pady=5, sticky="we")

    def get_fan_state(self):
        """
        @fn get_fan_state()
        @brief Gibt True/False zurück, ob der Lüfter an ist.
        """
        return self.fan_on_var.get()

    def set_fan_state(self, state: bool):
        """
        @fn set_fan_state(state)
        @brief Aktiviert/Deaktiviert den Lüfter-Checkbutton programmatisch.
        @param state: bool
        """
        self.fan_on_var.set(state)

    def get_selected_speed(self):
        """
        @fn get_selected_speed()
        @brief Gibt den gewählten Wert aus der Combobox als String zurück.
        """
        return self.fan_speed_var.get()

    def reset_speed_selection(self):
        """
        @fn reset_speed_selection()
        @brief Setzt die Combobox zurück auf "Lüftergeschwindigkeit wählen".
        """
        self.fan_speed_var.set("Lüftergeschwindigkeit wählen")

# sensor_gui/gui/control_panels.py

import tkinter as tk
from ttkbootstrap import ttk
from config.settings import GLOBAL_BUTTON_STYLE, GLOBAL_ENTRY_STYLE, GLOBAL_COMBOBOX_STYLE, TOGGLE_BOOTSTYLE

MAX_SPEED = 5

class HeaterControlPanel(ttk.LabelFrame):
    def __init__(self, parent, toggle_heater_callback, set_heater_callback):
        super().__init__(parent, text="Heater Controls", padding=20)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)

        self.heater_var = tk.BooleanVar(value=False)
        self.heater_check = ttk.Checkbutton(
            self,
            text="Heater On/Off",
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
        self.temp_set_entry.insert(0, "40")  # default
        self.temp_set_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        self.set_button = ttk.Button(
            self,
            text="Set Heater",
            style=GLOBAL_BUTTON_STYLE,
            command=set_heater_callback,
            width=10
        )
        self.set_button.grid(row=0, column=2, padx=5, pady=5, sticky="we")

    def get_heater_state(self):
        return self.heater_var.get()

    def set_heater_state(self, state: bool):
        self.heater_var.set(state)

    def get_temperature_value(self):
        return self.temp_set_entry.get()


class FanControlPanel(ttk.LabelFrame):
    def __init__(self, parent, toggle_fan_callback, set_fan_speed_callback):
        super().__init__(parent, text="Fan Controls", padding=20)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)

        self.fan_on_var = tk.BooleanVar(value=False)
        self.fan_on_check = ttk.Checkbutton(
            self,
            text="Fan On/Off",
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
            values=[str(i) for i in range(MAX_SPEED + 1)],
            style=GLOBAL_COMBOBOX_STYLE,
            state='readonly',
            width=15
        )
        self.fan_speed_combobox.set("Select Fan Speed")
        self.fan_speed_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        self.set_fan_button = ttk.Button(
            self,
            text="Set Fan Speed",
            style=GLOBAL_BUTTON_STYLE,
            command=set_fan_speed_callback,
            width=10
        )
        self.set_fan_button.grid(row=0, column=2, padx=5, pady=5, sticky="we")

    def get_fan_state(self):
        return self.fan_on_var.get()

    def set_fan_state(self, state: bool):
        self.fan_on_var.set(state)

    def get_selected_speed(self):
        return self.fan_speed_var.get()

    def reset_speed_selection(self):
        self.fan_speed_var.set("Select Fan Speed")

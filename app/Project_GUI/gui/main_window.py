# gui/main_window.py
"""
@file main_window.py
@brief Hauptfenster der GUI-Anwendung mit Tabs für BME280, andere Sensoren, 
       SSH-Verwaltung, Heizungssteuerung und Einbindung eines virtuellen Environments.

@note Um sicherzustellen, dass alle erforderlichen Bibliotheken aus einem Virtual Environment
      genutzt werden, wird vor jedem Skriptstart lokal oder per SSH das jeweilige venv aktiviert.
      Bitte ggf. die Pfade zu LOCAL_VENV_ACTIVATE und REMOTE_VENV_ACTIVATE anpassen.
"""

import os
import time
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import deque

from ttkbootstrap import Style, ttk
from config.settings import (
    THEME_COLORS, GLOBAL_BUTTON_STYLE, GLOBAL_TOGGLE_STYLE, GLOBAL_ENTRY_STYLE,
    GLOBAL_COMBOBOX_STYLE, TOGGLE_BOOTSTYLE, load_settings, save_settings,
    SAVE_DEFAULT_FOLDER, RESET_PIN, HEATER_PIN, FAN_PIN
)
from logic.ssh_controller import SSHController
from logic.sensors import SensorsManager
from logic.utils import get_sensor_color
from logic.data_processing import style_plot, moving_average
from gui.bme280_tab import BME280Tab
from gui.other_sensors_tab import OtherSensorsTab
from gui.control_panels import HeaterControlPanel, FanControlPanel, MAX_GESCHWINDIGKEIT
from gui.dialogs import CustomSSHDialog

###############################################################################
# Angepasste Pfade zur Aktivierung der Virtual Environments:
LOCAL_VENV_ACTIVATE = "/pfad/zum/lokalen/venv/bin/activate"
REMOTE_VENV_ACTIVATE = "/pfad/zum/remote/venv/bin/activate"
###############################################################################

LOCAL_HEATING_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "control", "heating.py")
REMOTE_HEATING_SCRIPT = "/home/Eiffel/GUI/ssh_control/heating.py"

LOCAL_SETPOINT_FILE  = "/tmp/heater_setpoint.txt"
LOCAL_BME_FILE       = "/tmp/bme_data.csv"
REMOTE_SETPOINT_FILE = "/tmp/heater_setpoint.txt"
REMOTE_BME_FILE      = "/tmp/bme_data.csv"

class SensorGUI:
    """
    @class SensorGUI
    @brief Hauptklasse, die das gesamte GUI aufbaut und steuert.
    """
    def __init__(self, root):
        """
        @fn __init__(root)
        @brief Konstruktor: Initialisiert GUI, lädt Einstellungen, startet Hintergrund-Threads
               und richtet alle Panels (BME280, Andere Sensoren, Heizung, Lüfter) ein.
        @param root: tk.Tk()-Instanz
        """
        self.root = root
        self.root.title("Moderner BME280-Monitor")
        self.root.geometry("1200x800")

        self.style = Style(theme="darkly")
        self.configure_styles()

        # Einstellungen laden
        self.settings = load_settings()
        self.save_data = tk.BooleanVar(value=self.settings["save_data"])
        self.saved_hostname = self.settings["hostname"]
        self.saved_username = self.settings["username"]
        self.saved_password = self.settings["password"]
        self.save_directory = self.settings["save_directory"]
        self.save_filename  = self.settings["save_filename"]
        if not os.path.isdir(self.save_directory):
            self.save_directory = SAVE_DEFAULT_FOLDER

        self.data_source = tk.StringVar(value="Local")
        self.ssh_controller = SSHController()
        self.sensor_manager = SensorsManager()

        self.recording_running = tk.BooleanVar(value=False)

        # BME280-Datenspeicher
        self.elapsed_time     = 0
        self.temperature_data = deque(maxlen=500)
        self.humidity_data    = deque(maxlen=500)
        self.pressure_data    = deque(maxlen=500)
        self.time_data        = deque(maxlen=500)

        # Andere Sensoren
        self.other_sensor_data = {}
        self.time_data_other   = deque(maxlen=500)
        self.other_sensor_vars = {}
        for s_key, s_conf in self.sensor_manager.get_available_other_sensors().items():
            self.other_sensor_vars[s_key] = tk.BooleanVar(value=False)
            self.other_sensor_data[s_key] = deque(maxlen=500)

        self.create_menu_bar()

        # Notebook
        self.notebook = ttk.Notebook(self.root, style='TNotebook')
        self.notebook.pack(fill='both', expand=True)

        # BME-Tab
        self.bme280_tab = BME280Tab(
            self.notebook,
            self.temperature_data,
            self.humidity_data,
            self.pressure_data,
            self.time_data
        )
        self.notebook.add(self.bme280_tab, text="BME280")

        # Steuerungspanels (Heizung, Lüfter) im BME-Tab
        self.heater_panel = HeaterControlPanel(
            self.bme280_tab.control_frame,
            self.toggle_heater,
            self.set_heater_temperature
        )
        self.heater_panel.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.fan_panel = FanControlPanel(
            self.bme280_tab.control_frame,
            self.toggle_fan,
            self.set_fan_speed
        )
        self.fan_panel.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # Tab für andere Sensoren (zunächst leer)
        self.other_sensors_tab = OtherSensorsTab(
            self.notebook,
            other_sensor_vars=self.other_sensor_vars,
            other_sensor_data=self.other_sensor_data,
            time_data_other=self.time_data_other,
            other_sensor_conf=self.sensor_manager.get_available_other_sensors()
        )

        # Hintergrund-Threads starten
        threading.Thread(target=self.collect_bme_data_csv, daemon=True).start()
        threading.Thread(target=self.collect_other_sensor_data, daemon=True).start()

        # Periodische GUI-Updates
        self.update_sensor_data()
        self.start_heating_script_threaded(measure_only=True)

    def configure_styles(self):
        """
        @fn configure_styles()
        @brief Definiert Stile für Frames, Buttons, Einträge etc.
        """
        self.style.configure('TLabelframe',
            bordercolor=THEME_COLORS["primary_color"],
            background=THEME_COLORS["frame_bg_color"]
        )
        self.style.configure('TLabelframe.Label',
            foreground=THEME_COLORS["text_color"],
            background=THEME_COLORS["frame_bg_color"]
        )
        self.style.configure(GLOBAL_BUTTON_STYLE,
            font=("Helvetica", 12),
            padding=10,
            foreground=THEME_COLORS["text_color"],
            background=THEME_COLORS["primary_color"]
        )
        self.style.map(GLOBAL_BUTTON_STYLE,
            background=[('active', THEME_COLORS["active_button"]),
                        ('disabled', THEME_COLORS["primary_color"])]
        )
        self.style.configure(GLOBAL_TOGGLE_STYLE,
            font=("Helvetica", 12),
            background=THEME_COLORS["primary_color"],
            foreground=THEME_COLORS["text_color"]
        )
        self.style.configure(GLOBAL_ENTRY_STYLE,
            font=("Helvetica", 12),
            fieldbackground=THEME_COLORS["background_color"],
            background=THEME_COLORS["background_color"],
            foreground=THEME_COLORS["text_color"]
        )
        self.style.configure(GLOBAL_COMBOBOX_STYLE,
            font=("Helvetica", 12),
            fieldbackground=THEME_COLORS["background_color"],
            background=THEME_COLORS["background_color"],
            foreground=THEME_COLORS["text_color"]
        )

    # -------------------------------------------------------------------------
    # MENÜ / MENÜFUNKTIONEN
    # -------------------------------------------------------------------------
    def create_menu_bar(self):
        """
        @fn create_menu_bar()
        @brief Erstellt das Hauptmenü mit Datenquellenauswahl (Lokal/SSH), Reset und Quit etc.
        """
        menu_bar = tk.Menu(self.root,
            background=THEME_COLORS["primary_color"],
            foreground=THEME_COLORS["text_color"],
            activebackground=THEME_COLORS["primary_color"],
            activeforeground='white'
        )
        main_menu = tk.Menu(menu_bar, tearoff=0,
            background=THEME_COLORS["primary_color"],
            foreground='white',
            activebackground=THEME_COLORS["primary_color"],
            activeforeground='white'
        )
        main_menu.add_command(label="Verbinden (SSH)", command=self.connect_to_ssh)

        data_source_menu = tk.Menu(main_menu, tearoff=0,
            background=THEME_COLORS["primary_color"],
            foreground='white',
            activebackground=THEME_COLORS["primary_color"],
            activeforeground='white'
        )
        data_source_menu.add_radiobutton(label="Lokal", variable=self.data_source, value="Local")
        data_source_menu.add_radiobutton(label="SSH",   variable=self.data_source, value="SSH")
        main_menu.add_cascade(label="Datenquelle", menu=data_source_menu)

        main_menu.add_command(label="System resetten", command=self.reset_system)
        main_menu.add_command(label="Beenden", command=self.on_close)
        menu_bar.add_cascade(label="Menü", menu=main_menu)

        # Sensoren-Menü
        sensors_menu = tk.Menu(menu_bar, tearoff=0,
            background=THEME_COLORS["primary_color"],
            foreground='white',
            activebackground=THEME_COLORS["primary_color"],
            activeforeground='white'
        )
        other_sensors_sub = tk.Menu(sensors_menu, tearoff=0,
            background=THEME_COLORS["primary_color"],
            foreground='white',
            activebackground=THEME_COLORS["primary_color"],
            activeforeground='white'
        )
        for s_key, s_conf in self.sensor_manager.get_available_other_sensors().items():
            other_sensors_sub.add_checkbutton(
                label=s_conf["name"],
                variable=self.other_sensor_vars[s_key],
                onvalue=True, offvalue=False,
                command=self.update_other_sensors_notebook
            )
        sensors_menu.add_cascade(label="Andere Sensoren", menu=other_sensors_sub)
        menu_bar.add_cascade(label="Sensoren", menu=sensors_menu)

        # Einstellungen-Menü
        settings_menu = tk.Menu(menu_bar, tearoff=0,
            background=THEME_COLORS["primary_color"],
            foreground='white',
            activebackground=THEME_COLORS["primary_color"],
            activeforeground='white'
        )
        settings_menu.add_checkbutton(label="Sensordaten speichern", variable=self.save_data, command=self.save_current_settings)
        settings_menu.add_command(label="Speicherort festlegen", command=self.set_save_location)
        settings_menu.add_checkbutton(label="Aufzeichnung starten", variable=self.recording_running, command=self.toggle_recording)
        menu_bar.add_cascade(label="Einstellungen", menu=settings_menu)

        self.root.config(menu=menu_bar)

    def reset_system(self):
        """
        @fn reset_system()
        @brief Sendet ein kurzes HIGH-Signal an RESET_PIN (lokal oder SSH).
        """
        if self.data_source.get() == "SSH":
            if self.ssh_controller.client:
                def run_reset_ssh():
                    self.ssh_controller.send_command(f"pigs modes {RESET_PIN} w")
                    self.ssh_controller.send_command(f"pigs w {RESET_PIN} 1")
                    time.sleep(1)
                    self.ssh_controller.send_command(f"pigs w {RESET_PIN} 0")
                threading.Thread(target=run_reset_ssh, daemon=True).start()
            else:
                print("SSH nicht verbunden. Reset nicht möglich.")
        else:
            def run_local_reset():
                try:
                    subprocess.run(["pigs", "modes", str(RESET_PIN), "w"])
                    subprocess.run(["pigs", "w", str(RESET_PIN), "1"])
                    time.sleep(1)
                    subprocess.run(["pigs", "w", str(RESET_PIN), "0"])
                except FileNotFoundError:
                    print("'pigs' ist lokal nicht installiert.")
                except subprocess.CalledProcessError as e:
                    print(f"Fehler beim lokalen Reset: {e}")
            threading.Thread(target=run_local_reset, daemon=True).start()

        print("System-Reset initiiert.")

    def update_other_sensors_notebook(self):
        """
        @fn update_other_sensors_notebook()
        @brief Fügt den Tab "Andere Sensoren" hinzu oder entfernt ihn, abhängig von den aktiven Sensoren.
        """
        active_sensors = [k for k, v in self.other_sensor_vars.items() if v.get()]
        if len(active_sensors) == 0:
            existing_tabs = {self.notebook.tab(i, "text"): i for i in range(self.notebook.index("end"))}
            if "Andere Sensoren" in existing_tabs:
                self.notebook.forget(existing_tabs["Andere Sensoren"])
        else:
            existing_tabs = {self.notebook.tab(i, "text"): i for i in range(self.notebook.index("end"))}
            if "Andere Sensoren" not in existing_tabs:
                self.notebook.add(self.other_sensors_tab, text="Andere Sensoren")
            self.other_sensors_tab.update_active_sensors(active_sensors)

    def connect_to_ssh(self):
        """
        @fn connect_to_ssh()
        @brief Öffnet einen Dialog für SSH-Daten und stellt eine Verbindung her, falls möglich.
        """
        if self.data_source.get() == "Local":
            messagebox.showerror("Lokalmodus", "Bitte zuerst Datenquelle auf SSH stellen.")
            return
        dialog = CustomSSHDialog(self.root, self.saved_hostname, self.saved_username, self.saved_password)
        self.root.wait_window(dialog)
        if dialog.result:
            hostname, username, password = dialog.result
            self.saved_hostname = hostname
            self.saved_username = username
            self.saved_password = password
            self.save_current_settings()

            if self.ssh_controller.connect(hostname, username, password):
                print(f"SSH verbunden mit {hostname}")
            else:
                messagebox.showerror("Verbindungsfehler", f"Keine Verbindung zu {hostname}")

    def save_current_settings(self):
        """
        @fn save_current_settings()
        @brief Speichert aktuelle GUI-Einstellungen (SSH-Daten, Speicherpfade etc.) in settings.json.
        """
        self.settings["save_data"]      = self.save_data.get()
        self.settings["hostname"]       = self.saved_hostname
        self.settings["username"]       = self.saved_username
        self.settings["password"]       = self.saved_password
        self.settings["save_directory"] = self.save_directory
        self.settings["save_filename"]  = self.save_filename
        save_settings(self.settings)

    def set_save_location(self):
        """
        @fn set_save_location()
        @brief Öffnet einen Dialog zum Auswählen einer Speicherdatei.
        """
        pfad = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown-Dateien", "*.md"), ("Alle Dateien", "*.*")],
            initialdir=self.save_directory,
            initialfile=self.save_filename,
            title="Speicherort festlegen"
        )
        if pfad:
            self.save_directory = os.path.dirname(pfad)
            self.save_filename  = os.path.basename(pfad)
            self.save_current_settings()

    def toggle_recording(self):
        """
        @fn toggle_recording()
        @brief Wird aufgerufen, wenn "Aufzeichnung starten" aktiviert/deaktiviert wird.
        """
        if self.recording_running.get():
            self.save_data.set(True)
            self.save_current_settings()
        else:
            print("Aufzeichnung gestoppt.")

    # -------------------------------------------------------------------------
    # HEIZUNGSFUNKTIONEN
    # -------------------------------------------------------------------------
    def toggle_heater(self):
        """
        @fn toggle_heater()
        @brief Schaltet die Heizung An/Aus (abhängig vom Checkbutton).
        """
        zustand = self.heater_panel.get_heater_state()
        if zustand:
            print("Heizung AN => Skript starten, falls nicht bereits aktiv.")
            self.start_heating_script_threaded(measure_only=False)
        else:
            print("Heizung AUS => Setpoint-Datei entfernen => duty=0.")
            self.remove_setpoint_file()

    def set_heater_temperature(self):
        """
        @fn set_heater_temperature()
        @brief Liest den Sollwert aus dem Entry-Feld und aktualisiert die Setpoint-Datei.
        """
        val_str = self.heater_panel.get_temperature_value().strip()
        if not val_str:
            print("Kein Sollwert => Standard 20°C. Heizung ein.")
            self.heater_panel.set_heater_state(True)
            self.start_heating_script_threaded(measure_only=False)
            self.remove_setpoint_file()
            return

        try:
            val = float(val_str)
        except ValueError:
            messagebox.showerror("Ungültige Eingabe", f"'{val_str}' ist keine Zahl.")
            return

        if val < 0 or val > 80:
            messagebox.showerror("Außerhalb des Bereichs", "Solltemperatur muss zwischen 0 und 80°C liegen.")
            return

        print(f"Setze Heizung auf {val} °C")
        self.heater_panel.set_heater_state(True)
        self.start_heating_script_threaded(measure_only=False)
        self.write_setpoint_file(val)

    def start_heating_script_threaded(self, measure_only=False):
        """
        @fn start_heating_script_threaded(measure_only=False)
        @brief Startet das heating.py-Skript lokal oder per SSH, unter Aktivierung des venv.
        @param measure_only: True => kein Setpoint => 20°C, nur Messung
        """
        def run_script():
            if self.data_source.get() == "SSH":
                cmd = f"source {REMOTE_VENV_ACTIVATE} && nohup python {REMOTE_HEATING_SCRIPT} &"
                self.ssh_controller.send_command(cmd)
                print("heating.py via SSH gestartet (venv aktiviert).")
            else:
                try:
                    subprocess.Popen([
                        "/bin/bash", "-c",
                        f"source {LOCAL_VENV_ACTIVATE} && python {LOCAL_HEATING_SCRIPT}"
                    ])
                    print("heating.py lokal gestartet (venv aktiviert).")
                except FileNotFoundError:
                    print("Lokales heating.py nicht gefunden oder Python fehlt.")

            if measure_only:
                self.remove_setpoint_file()

        threading.Thread(target=run_script, daemon=True).start()

    def write_setpoint_file(self, val: float):
        """
        @fn write_setpoint_file(val)
        @brief Schreibt den Sollwert in /tmp/heater_setpoint.txt (lokal oder SSH).
        """
        if self.data_source.get() == "SSH":
            cmd = f"echo '{val}' > {REMOTE_SETPOINT_FILE}"
            threading.Thread(target=lambda: self.ssh_controller.send_command(cmd), daemon=True).start()
        else:
            try:
                with open(LOCAL_SETPOINT_FILE, "w") as f:
                    f.write(str(val))
            except Exception as e:
                print(f"Fehler beim Schreiben des Setpoints: {e}")

    def remove_setpoint_file(self):
        """
        @fn remove_setpoint_file()
        @brief Löscht /tmp/heater_setpoint.txt, sodass im heating.py-Skript None gelesen wird.
        """
        if self.data_source.get() == "SSH":
            cmd = f"rm -f {REMOTE_SETPOINT_FILE}"
            threading.Thread(target=lambda: self.ssh_controller.send_command(cmd), daemon=True).start()
        else:
            try:
                os.remove(LOCAL_SETPOINT_FILE)
            except FileNotFoundError:
                pass

    # -------------------------------------------------------------------------
    # LÜFTERFUNKTIONEN
    # -------------------------------------------------------------------------
    fan_speed = 0
    def toggle_fan(self):
        """
        @fn toggle_fan()
        @brief Lüfter An/Aus (Checkbutton).
        """
        zustand = self.fan_panel.get_fan_state()
        if zustand:
            if self.fan_speed > 0:
                print(f"Lüfter AN => duty auf {self.fan_speed}")
            else:
                print("Bitte zuerst eine Lüftergeschwindigkeit wählen.")
                self.fan_panel.set_fan_state(False)
        else:
            print("Lüfter AUS => duty=0")
            self.fan_speed = 0
            self.fan_panel.reset_speed_selection()

    def set_fan_speed(self):
        """
        @fn set_fan_speed()
        @brief Liest den gewählten Lüfter-Speed aus der Combobox und speichert ihn intern.
        """
        sp_str = self.fan_panel.get_selected_speed()
        if sp_str == "Lüftergeschwindigkeit wählen":
            print("Keine Lüftergeschwindigkeit gewählt.")
            return
        try:
            sp = int(sp_str)
            if sp < 0 or sp > MAX_GESCHWINDIGKEIT:
                raise ValueError
            self.fan_speed = sp
            print(f"Lüfter => duty={sp}")
            self.fan_panel.set_fan_state(True)
        except ValueError:
            print("Ungültige Lüftergeschwindigkeit.")

    # -------------------------------------------------------------------------
    # BME-DATEN ERFASSEN
    # -------------------------------------------------------------------------
    def collect_bme_data_csv(self):
        """
        @fn collect_bme_data_csv()
        @brief Hintergrundthread: Liest alle 1s die letzte Zeile aus /tmp/bme_data.csv (lokal oder SSH),
               um aktuelle Temperatur-, Feuchtigkeits- und Druckwerte darzustellen.
        """
        while True:
            time.sleep(1.0)
            if self.data_source.get() == "SSH":
                zeile = self.ssh_controller.send_command("tail -n 1 /tmp/bme_data.csv")
                if not zeile:
                    continue
                zeile = zeile.strip()
            else:
                if not os.path.exists(LOCAL_BME_FILE):
                    continue
                zeile = self.read_last_line_local(LOCAL_BME_FILE)
                if not zeile:
                    continue

            parts = zeile.split(",")
            if len(parts) < 4:
                continue

            try:
                temp = float(parts[1])
                feuchte = float(parts[2])
                druck = float(parts[3])
                if temp < -50 or temp > 120:
                    print(f"Messwert ignoriert (außerhalb sinnvoller Grenzen): {temp:.2f} °C")
                    continue
                self.temperature_data.append(temp)
                self.humidity_data.append(feuchte)
                self.pressure_data.append(druck)
                self.time_data.append(self.elapsed_time)
                self.elapsed_time += 1
            except ValueError:
                pass

    def read_last_line_local(self, pfad):
        """
        @fn read_last_line_local(pfad)
        @brief Liest die letzte Zeile einer lokalen Datei aus.
        @param pfad: Pfad zur Datei
        @return Letzte Zeile als String oder ""
        """
        try:
            with open(pfad, "rb") as f:
                f.seek(-200, os.SEEK_END)
                lines = f.read().decode(errors='ignore').strip().split("\n")
            return lines[-1] if lines else ""
        except OSError:
            return ""

    # -------------------------------------------------------------------------
    # ANDERE SENSOREN AUSLESEN
    # -------------------------------------------------------------------------
    def collect_other_sensor_data(self):
        """
        @fn collect_other_sensor_data()
        @brief Hintergrundthread: Liest andere Sensoren (lokal oder SSH) per aggregator 
               oder dedizierte Skripte aus, unter Nutzung des jeweiligen venv.
        """
        import random
        while True:
            aktive_sensoren = [k for k, v in self.other_sensor_vars.items() if v.get()]
            if len(aktive_sensoren) == 0:
                time.sleep(1)
                continue

            if self.data_source.get() == "SSH" and not self.ssh_controller.client:
                print("SSH-Modus, aber keine Verbindung => Überspringe andere Sensoren.")
                time.sleep(1)
                continue

            for s_key in aktive_sensoren:
                conf = self.sensor_manager.get_available_other_sensors()[s_key]
                script_path = conf["script_path"]

                val = None
                if script_path:
                    # Remote venv?
                    if self.data_source.get() == "SSH":
                        cmd = f"source {REMOTE_VENV_ACTIVATE} && python {script_path}"
                        out = self.ssh_controller.send_command(cmd)
                        out = out.strip()
                        try:
                            val = float(out)
                        except ValueError:
                            val = None
                    else:
                        # Lokales venv
                        try:
                            ret = subprocess.check_output([
                                "/bin/bash", "-c",
                                f"source {LOCAL_VENV_ACTIVATE} && python {script_path}"
                            ])
                            val = float(ret.decode().strip())
                        except Exception as e:
                            print(f"Fehler beim lokalen Ausführen von {script_path}: {e}")
                            val = None
                else:
                    # Falls kein Skriptpfad hinterlegt => Dummy-Werte
                    if conf["unit"] == "°C":
                        val = random.uniform(30, 60)
                    elif conf["unit"] == "Pa":
                        val = random.uniform(1000, 3000)
                    else:
                        val = random.uniform(1, 10)

                if val is not None:
                    self.other_sensor_data[s_key].append(val)

            self.time_data_other.append(len(self.time_data_other))
            time.sleep(1)

    # -------------------------------------------------------------------------
    # PERIODISCHE GUI-UPDATES
    # -------------------------------------------------------------------------
    def update_sensor_data(self):
        """
        @fn update_sensor_data()
        @brief Wird alle 1s per .after() aufgerufen. Aktualisiert GUI-Labels und Plots.
        """
        if len(self.temperature_data) > 0:
            self.bme280_tab.temp_label.config(text=f"{self.temperature_data[-1]:.2f} °C")
        if len(self.humidity_data) > 0:
            self.bme280_tab.humidity_label.config(text=f"{self.humidity_data[-1]:.2f} %")
        if len(self.pressure_data) > 0:
            self.bme280_tab.pressure_label.config(text=f"{self.pressure_data[-1]:.2f} hPa")

        if len(self.time_data) > 0 and self.bme280_tab.loading_label:
            self.bme280_tab.remove_loading_label()

        self.update_bme280_plots()

        if self.recording_running.get() and self.save_data.get():
            self.save_sensor_data()

        self.other_sensors_tab.update_other_sensor_data()
        self.root.after(1000, self.update_sensor_data)

    def update_bme280_plots(self):
        """
        @fn update_bme280_plots()
        @brief Aktualisiert die Plots für Temperatur, Feuchtigkeit und Druck.
        """
        ax_t = self.bme280_tab.ax_temp
        ax_h = self.bme280_tab.ax_humidity
        ax_p = self.bme280_tab.ax_pressure

        ax_t.clear()
        ax_h.clear()
        ax_p.clear()

        style_plot(ax_t, "Temperatur", "°C")
        style_plot(ax_h, "Feuchtigkeit", "%")
        style_plot(ax_p, "Druck", "hPa")

        if len(self.temperature_data) > 0:
            ax_t.plot(self.time_data, self.temperature_data, color=THEME_COLORS["temperature_color"])
        if len(self.humidity_data) > 0:
            ax_h.plot(self.time_data, self.humidity_data, color=THEME_COLORS["humidity_color"])
        if len(self.pressure_data) > 0:
            ax_p.plot(self.time_data, self.pressure_data, color=THEME_COLORS["pressure_color"])

        self.bme280_tab.canvas.draw_idle()

    def save_sensor_data(self):
        """
        @fn save_sensor_data()
        @brief Schreibt den aktuellsten Messwert in die gewählte Datei (Markdown/CSV).
        """
        pfad_ziel = os.path.join(self.save_directory, self.save_filename)
        if not os.path.exists(pfad_ziel):
            with open(pfad_ziel, "w") as f:
                f.write("# Sensordaten\n\n**Datenquelle:** {}\n\n".format(self.data_source.get()))
                f.write("## Alle Sensor-Daten\n\n")
                f.write("| Zeit (s) | Temperatur (°C) | Feuchtigkeit (%) | Druck (hPa) |\n")
                f.write("|----------|-----------------|------------------|-------------|\n")

        if len(self.time_data) == 0:
            return

        i = len(self.time_data) - 1
        t_s = time.time()
        t_lauf = self.time_data[i]
        temp = self.temperature_data[i]
        feuchte = self.humidity_data[i]
        druck = self.pressure_data[i]
        with open(pfad_ziel, "a") as f:
            f.write(f"{t_s}, {t_lauf}, {temp:.2f}, {feuchte:.2f}, {druck:.2f}\n")

    def on_close(self):
        """
        @fn on_close()
        @brief Wird beim Schließen des Fensters aufgerufen. Beendet heating.py, 
               löscht die BME-CSV, trennt SSH und zerstört das Hauptfenster.
        """
        print("GUI wird geschlossen => heating.py beenden, /tmp/bme_data.csv entfernen, Heizung/Lüfter aus.")
        if self.data_source.get() == "SSH":
            self.ssh_controller.send_command("pkill -f heating.py")
            self.ssh_controller.send_command(f"rm -f {REMOTE_BME_FILE}")
        else:
            subprocess.run(["pkill", "-f", "heating.py"])
            try:
                os.remove(LOCAL_BME_FILE)
            except FileNotFoundError:
                pass

        if self.ssh_controller.client:
            self.ssh_controller.close()
        self.root.destroy()

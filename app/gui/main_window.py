# sensor_gui/gui/main_window.py

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
from gui.control_panels import HeaterControlPanel, FanControlPanel, MAX_SPEED
from gui.dialogs import CustomSSHDialog

LOCAL_HEATING_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "control", "heating.py")
REMOTE_HEATING_SCRIPT = "/home/Eiffel/GUI/ssh_control/heating.py"

LOCAL_SETPOINT_FILE = "/tmp/heater_setpoint.txt"
LOCAL_BME_FILE      = "/tmp/bme_data.csv"
REMOTE_SETPOINT_FILE= "/tmp/heater_setpoint.txt"
REMOTE_BME_FILE     = "/tmp/bme_data.csv"


class SensorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern BME280 Monitor")
        self.root.geometry("1200x800")

        self.style = Style(theme="darkly")
        self.configure_styles()

        # Load user settings
        self.settings = load_settings()
        self.save_data = tk.BooleanVar(value=self.settings["save_data"])
        self.saved_hostname = self.settings["hostname"]
        self.saved_username = self.settings["username"]
        self.saved_password = self.settings["password"]
        self.save_directory = self.settings["save_directory"]
        self.save_filename  = self.settings["save_filename"]
        if not os.path.isdir(self.save_directory):
            self.save_directory = SAVE_DEFAULT_FOLDER

        # Local or SSH
        self.data_source = tk.StringVar(value="Local")
        self.ssh_controller = SSHController()
        self.sensor_manager = SensorsManager()

        self.recording_running = tk.BooleanVar(value=False)

        # BME data (core sensor)
        self.elapsed_time     = 0
        self.temperature_data = deque(maxlen=500)
        self.humidity_data    = deque(maxlen=500)
        self.pressure_data    = deque(maxlen=500)
        self.time_data        = deque(maxlen=500)

        # "Other sensors"
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

        # BME tab
        self.bme280_tab = BME280Tab(
            self.notebook,
            self.temperature_data,
            self.humidity_data,
            self.pressure_data,
            self.time_data
        )
        self.notebook.add(self.bme280_tab, text="BME280")

        # Panels
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

        # "Other Sensors" tab
        self.other_sensors_tab = OtherSensorsTab(
            self.notebook,
            other_sensor_vars=self.other_sensor_vars,
            other_sensor_data=self.other_sensor_data,
            time_data_other=self.time_data_other,
            other_sensor_conf=self.sensor_manager.get_available_other_sensors()
        )

        # Start background threads
        threading.Thread(target=self.collect_bme_data_csv, daemon=True).start()
        threading.Thread(target=self.collect_other_sensor_data, daemon=True).start()

        # Periodic GUI updates
        self.update_sensor_data()
        self.start_heating_script_threaded(measure_only=True)

    def configure_styles(self):
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

    # ---------------- MENU ----------------
    def create_menu_bar(self):
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
        main_menu.add_command(label="Connect", command=self.connect_to_ssh)

        data_source_menu = tk.Menu(main_menu, tearoff=0,
            background=THEME_COLORS["primary_color"],
            foreground='white',
            activebackground=THEME_COLORS["primary_color"],
            activeforeground='white'
        )
        data_source_menu.add_radiobutton(label="Local", variable=self.data_source, value="Local")
        data_source_menu.add_radiobutton(label="SSH",   variable=self.data_source, value="SSH")
        main_menu.add_cascade(label="Data Source", menu=data_source_menu)

        main_menu.add_command(label="Reset System", command=self.reset_system)
        main_menu.add_command(label="Quit", command=self.on_close)
        menu_bar.add_cascade(label="Menu", menu=main_menu)

        # "Sensors" menu
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
        # Populate sub-checkbuttons for each "other sensor"
        for s_key, s_conf in self.sensor_manager.get_available_other_sensors().items():
            other_sensors_sub.add_checkbutton(
                label=s_conf["name"],
                variable=self.other_sensor_vars[s_key],
                onvalue=True, offvalue=False,
                command=self.update_other_sensors_notebook
            )
        sensors_menu.add_cascade(label="Other Sensors", menu=other_sensors_sub)
        menu_bar.add_cascade(label="Sensors", menu=sensors_menu)

        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0,
            background=THEME_COLORS["primary_color"],
            foreground='white',
            activebackground=THEME_COLORS["primary_color"],
            activeforeground='white'
        )
        settings_menu.add_checkbutton(label="Save Sensor Data", variable=self.save_data, command=self.save_current_settings)
        settings_menu.add_command(label="Set Save Location", command=self.set_save_location)
        settings_menu.add_checkbutton(label="Start Recording", variable=self.recording_running, command=self.toggle_recording)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        self.root.config(menu=menu_bar)

    def reset_system(self):
        """Reset the system by toggling the RESET_PIN."""
        if self.data_source.get() == "SSH":
            if self.ssh_controller.client:
                def run_reset_ssh():
                    self.ssh_controller.send_command(f"pigs modes {RESET_PIN} w")  # Set pin as output
                    self.ssh_controller.send_command(f"pigs w {RESET_PIN} 1")      # pin HIGH
                    time.sleep(1)
                    self.ssh_controller.send_command(f"pigs w {RESET_PIN} 0")      # pin LOW
                threading.Thread(target=run_reset_ssh, daemon=True).start()
            else:
                print("SSH not connected for reset.")
        else:
            def run_local_reset():
                try:
                    subprocess.run(["pigs", "modes", str(RESET_PIN), "w"])
                    subprocess.run(["pigs", "w", str(RESET_PIN), "1"])
                    time.sleep(1)
                    subprocess.run(["pigs", "w", str(RESET_PIN), "0"])
                except FileNotFoundError:
                    print("Local 'pigs' not installed.")
                except subprocess.CalledProcessError as e:
                    print(f"Reset error: {e}")
            threading.Thread(target=run_local_reset, daemon=True).start()

        print("System reset triggered.")

    def update_other_sensors_notebook(self):
        active_sensors = [k for k, v in self.other_sensor_vars.items() if v.get()]
        if len(active_sensors) == 0:
            # remove the "Other Sensors" tab if it exists
            existing_tabs = {self.notebook.tab(i, "text"): i for i in range(self.notebook.index("end"))}
            if "Other Sensors" in existing_tabs:
                self.notebook.forget(existing_tabs["Other Sensors"])
        else:
            # if not present, add
            existing_tabs = {self.notebook.tab(i, "text"): i for i in range(self.notebook.index("end"))}
            if "Other Sensors" not in existing_tabs:
                self.notebook.add(self.other_sensors_tab, text="Other Sensors")
            self.other_sensors_tab.update_active_sensors(active_sensors)

    def connect_to_ssh(self):
        if self.data_source.get() == "Local":
            messagebox.showerror("Local Mode", "Switch Data Source to SSH first.")
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
                print(f"SSH connected to {hostname}")
            else:
                messagebox.showerror("Connection Failed", f"Cannot connect to {hostname}")

    def save_current_settings(self):
        self.settings["save_data"]      = self.save_data.get()
        self.settings["hostname"]       = self.saved_hostname
        self.settings["username"]       = self.saved_username
        self.settings["password"]       = self.saved_password
        self.settings["save_directory"] = self.save_directory
        self.settings["save_filename"]  = self.save_filename
        save_settings(self.settings)

    def set_save_location(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")],
            initialdir=self.save_directory,
            initialfile=self.save_filename,
            title="Set Save Location"
        )
        if filepath:
            self.save_directory = os.path.dirname(filepath)
            self.save_filename  = os.path.basename(filepath)
            self.save_current_settings()

    def toggle_recording(self):
        if self.recording_running.get():
            self.save_data.set(True)
            self.save_current_settings()
        else:
            print("Stopped recording")

    # ----------------- HEATER -----------------
    def toggle_heater(self):
        st = self.heater_panel.get_heater_state()
        if st:
            print("Heater ON => ensure script is running.")
            self.start_heating_script_threaded(measure_only=False)
        else:
            print("Heater OFF => remove setpoint => set heater duty=0.")
            self.remove_setpoint_file()

    def set_heater_temperature(self):
        val_str = self.heater_panel.get_temperature_value().strip()
        if not val_str:
            print("No temperature => revert to default=20, heater ON.")
            self.heater_panel.set_heater_state(True)
            self.start_heating_script_threaded(measure_only=False)
            self.remove_setpoint_file()
            return

        try:
            val = float(val_str)
        except ValueError:
            messagebox.showerror("Invalid Input", f"'{val_str}' is not a valid number.")
            return

        if val < 0 or val > 80:
            messagebox.showerror("Out of Range", "Heater must be 0..80 °C.")
            return

        print(f"Setting heater temperature to {val} °C")
        self.heater_panel.set_heater_state(True)
        self.start_heating_script_threaded(measure_only=False)
        self.write_setpoint_file(val)
        print(f"Heater set to {val} °C")

    def start_heating_script_threaded(self, measure_only=False):
        def run_script():
            if self.data_source.get() == "SSH":
                # run remote
                cmd = f"nohup python3 {REMOTE_HEATING_SCRIPT} &"
                self.ssh_controller.send_command(cmd)
                print("Started heating.py on remote Pi (SSH).")
            else:
                # local
                try:
                    subprocess.Popen(["python3", LOCAL_HEATING_SCRIPT])
                    print("Started local heating.py.")
                except FileNotFoundError:
                    print("Local script not found or python missing.")
            if measure_only:
                self.remove_setpoint_file()

        threading.Thread(target=run_script, daemon=True).start()

    def write_setpoint_file(self, val: float):
        if self.data_source.get() == "SSH":
            cmd = f"echo '{val}' > {REMOTE_SETPOINT_FILE}"
            threading.Thread(target=lambda: self.ssh_controller.send_command(cmd), daemon=True).start()
        else:
            try:
                with open(LOCAL_SETPOINT_FILE, "w") as f:
                    f.write(str(val))
            except Exception as e:
                print(f"Error writing setpoint: {e}")

    def remove_setpoint_file(self):
        if self.data_source.get() == "SSH":
            cmd = f"rm -f {REMOTE_SETPOINT_FILE}"
            threading.Thread(target=lambda: self.ssh_controller.send_command(cmd), daemon=True).start()
        else:
            try:
                os.remove(LOCAL_SETPOINT_FILE)
            except FileNotFoundError:
                pass

    # ---------------- FAN ----------------
    fan_speed = 0
    def toggle_fan(self):
        st = self.fan_panel.get_fan_state()
        if st:
            if self.fan_speed > 0:
                print(f"Fan ON => duty ~some nonzero~")
            else:
                print("Pick a fan speed first.")
                self.fan_panel.set_fan_state(False)
        else:
            print("Fan OFF => duty=0")
            self.fan_speed = 0
            self.fan_panel.reset_speed_selection()

    def set_fan_speed(self):
        sp_str = self.fan_panel.get_selected_speed()
        if sp_str == "Select Fan Speed":
            print("No fan speed selected.")
            return
        try:
            sp = int(sp_str)
            if sp < 0 or sp > MAX_SPEED:
                raise ValueError
            self.fan_speed = sp
            print(f"Fan => duty => {sp}")
            self.fan_panel.set_fan_state(True)
        except ValueError:
            print("Invalid fan speed input.")

    # ---------------- BME CSV -----------
    def collect_bme_data_csv(self):
        """Read local or remote BME data from /tmp/bme_data.csv every 1s, parse last line, store it."""
        while True:
            time.sleep(1.0)
            if self.data_source.get() == "SSH":
                line = self.ssh_controller.send_command("tail -n 1 /tmp/bme_data.csv")
                if not line:
                    continue
                line = line.strip()
            else:
                if not os.path.exists(LOCAL_BME_FILE):
                    continue
                line = self.read_last_line_local(LOCAL_BME_FILE)
                if not line:
                    continue

            parts = line.split(",")
            if len(parts) < 4:
                continue

            try:
                temp = float(parts[1])
                hum  = float(parts[2])
                pres = float(parts[3])
                if temp < -50 or temp > 120:
                    print(f"Ignoring out-of-range temp: {temp:.2f} °C")
                    continue

                self.temperature_data.append(temp)
                self.humidity_data.append(hum)
                self.pressure_data.append(pres)
                self.time_data.append(self.elapsed_time)
                self.elapsed_time += 1
            except ValueError:
                pass

    def read_last_line_local(self, fp):
        try:
            with open(fp, "rb") as f:
                f.seek(-200, os.SEEK_END)
                lines = f.read().decode(errors='ignore').strip().split("\n")
            return lines[-1] if lines else ""
        except OSError:
            return ""

    # ---------------- OTHER SENSORS -----------
    def collect_other_sensor_data(self):
        """Continuously read data for 'other sensors' that are toggled on."""
        import random
        while True:
            # Check which sensors are active
            active_sensors = [k for k, v in self.other_sensor_vars.items() if v.get()]
            if len(active_sensors) == 0:
                time.sleep(1)
                continue

            # If SSH mode but not connected
            if self.data_source.get() == "SSH" and not self.ssh_controller.client:
                print("SSH mode, but not connected => skipping other sensors.")
                time.sleep(1)
                continue

            # For each active sensor, run the script (if any) and store the result
            for s_key in active_sensors:
                conf = self.sensor_manager.get_available_other_sensors()[s_key]
                script_path = conf["script_path"]

                val = None
                if script_path:
                    # If there's a script, run it
                    if self.data_source.get() == "SSH":
                        out = self.ssh_controller.send_command(f"python3 {script_path}")
                        out = out.strip()
                        try:
                            val = float(out)
                        except ValueError:
                            val = None
                    else:
                        # Local
                        try:
                            ret = subprocess.check_output(["python3", script_path])
                            val = float(ret.decode().strip())
                        except Exception as e:
                            print(f"Error running local script {script_path}: {e}")
                            val = None
                else:
                    if conf["unit"] == "°C":
                        val = random.uniform(30, 60)
                    elif conf["unit"] == "Pa":
                        val = random.uniform(1000, 3000)
                    else:
                        val = random.uniform(1, 10)

                if val is not None:
                    self.other_sensor_data[s_key].append(val)

            # Increment time_data_other for plotting
            self.time_data_other.append(len(self.time_data_other))
            time.sleep(1)

    # refresh bme + other sensors
    def update_sensor_data(self):
        # BME
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
        ax_t = self.bme280_tab.ax_temp
        ax_h = self.bme280_tab.ax_humidity
        ax_p = self.bme280_tab.ax_pressure

        ax_t.clear()
        ax_h.clear()
        ax_p.clear()

        style_plot(ax_t, "Temperature", "°C")
        style_plot(ax_h, "Humidity", "%")
        style_plot(ax_p, "Pressure", "hPa")

        if len(self.temperature_data) > 0:
            ax_t.plot(self.time_data, self.temperature_data, color=THEME_COLORS["temperature_color"])
        if len(self.humidity_data) > 0:
            ax_h.plot(self.time_data, self.humidity_data, color=THEME_COLORS["humidity_color"])
        if len(self.pressure_data) > 0:
            ax_p.plot(self.time_data, self.pressure_data, color=THEME_COLORS["pressure_color"])

        self.bme280_tab.canvas.draw_idle()

    def save_sensor_data(self):
        rec_path = os.path.join(self.save_directory, self.save_filename)
        if not os.path.exists(rec_path):
            with open(rec_path, "w") as f:
                f.write("# Sensor Data\n\n**Data Source:** {}\n\n".format(self.data_source.get()))
                f.write("## All Sensors Data\n\n")
                f.write("| Time (s) | Temperature (°C) | Humidity (%) | Pressure (hPa) |\n")
                f.write("|----------|------------------|--------------|----------------|\n")

        if len(self.time_data) == 0:
            return

        i = len(self.time_data) - 1
        t_s = time.time()
        time_s = self.time_data[i]
        T = self.temperature_data[i]
        H = self.humidity_data[i]
        P = self.pressure_data[i]
        with open(rec_path, "a") as f:
            f.write(f"{t_s}, {time_s}, {T:.2f}, {H:.2f}, {P:.2f}\n")

    def on_close(self):
        """Stop scripts, remove CSV, turn heater/fan off, etc."""
        print("Closing GUI => kill script & remove CSV => set heater/fan=0.")
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

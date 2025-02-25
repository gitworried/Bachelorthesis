# sensor_gui/logic/sensors.py

class SensorsManager:
    def __init__(self):
        self.other_sensors = {
            # ----------------------------------------------------------------
            # MCP for Velocity
            # ----------------------------------------------------------------
            "MCP9600_Airflow": {
                "name": "MCP9600 Airflow",
                "unit": "m/s",
                "script_path": "/home/Eiffel/GUI/ssh_control/MCP9600_Airflow.py",
                "measure_type": "airflow"
            },        
            # ----------------------------------------------------------------
            # MCP for Temperature
            # ----------------------------------------------------------------
            "MCP9600_Env": {
                "name": "MCP9600 Environment",
                "unit": "°C",
                "script_path": "/home/Eiffel/GUI/ssh_control/MCP9600_Env.py",
                "measure_type": "temperature"
            },

            # ----------------------------------------------------------------
            # SDP810 for Temperature
            # ----------------------------------------------------------------
            "SDP810_Temperature": {
                "name": "SDP810 Temperature",
                "unit": "°C",
                "script_path": "/home/Eiffel/GUI/ssh_control/sdp810_temp.py",
                "measure_type": "temperature"
            },
            # ----------------------------------------------------------------
            # SDP810 for Pressure
            # ----------------------------------------------------------------
            "SDP810_Pressure": {
                "name": "SDP810 Pressure",
                "unit": "Pa",
                "script_path": "/home/Eiffel/GUI/ssh_control/sdp810_pressure.py",
                "measure_type": "pressure"
            },

            # ----------------------------------------------------------------
            # Velocity sensor derived from MCP9600_Env + SDP810_Pressure
            # => No script_path (compute in code).
            # ----------------------------------------------------------------
            "Combined_Velocity": {
                "name": "Derived Velocity (SDP810+MCP9600)",
                "unit": "m/s",
                "script_path": None,
                "measure_type": "velocity"
            }
        }

    def get_available_other_sensors(self):
        return self.other_sensors

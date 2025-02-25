# sensor_gui/logic/temperature_controller.py

class TemperatureController:
    def __init__(self, set_pwm_callback, heater_gpio):
        self.set_pwm_callback = set_pwm_callback
        self.heater_gpio = heater_gpio
        self.target_temp = None
        self.heater_on = False

    def set_target_temperature(self, temp):
        """Set the desired target temperature. If None, control is disabled and heater off."""
        self.target_temp = temp
        if temp is None:
            # Turn heater off if no target
            self.set_pwm_callback(self.heater_gpio, 0)
            self.heater_on = False

    def update_control(self, current_temp):
        """Adjust heater PWM based on current temperature and target."""
        if self.target_temp is None:
            # No control if no target set
            return

        upper_threshold = self.target_temp + 1
        lower_threshold = self.target_temp - 1

        if self.heater_on and current_temp > upper_threshold:
            # Turn heater off
            self.heater_on = False
            self.set_pwm_callback(self.heater_gpio, 0)

        elif (not self.heater_on) and current_temp < lower_threshold:
            # Turn heater on (full power)
            self.heater_on = True
            self.set_pwm_callback(self.heater_gpio, 255)
        # Otherwise, stay in current state.

# logic/temperature_controller.py
"""
@file temperature_controller.py
@brief Einfache Klasse zur Steuerung der Heizung anhand eines Sollwerts (PWM).
       Es wird ein Hystereseverhalten angewendet, um die Heizung ein- oder auszuschalten.
"""

class TemperatureController:
    """
    @class TemperatureController
    @brief Führt eine Hysterese-Steuerung durch. Schaltet die Heizung an/aus,
           abhängig von current_temp und target_temp.
    """
    def __init__(self, set_pwm_callback, heater_gpio):
        """
        @fn __init__(set_pwm_callback, heater_gpio)
        @brief Konstruktor.
        @param set_pwm_callback: Funktion(gpio_pin, dutycycle), um PWM zu setzen.
        @param heater_gpio: GPIO-Pin für die Heizung.
        """
        self.set_pwm_callback = set_pwm_callback
        self.heater_gpio = heater_gpio
        self.target_temp = None
        self.heater_on = False

    def set_target_temperature(self, temp):
        """
        @fn set_target_temperature(temp)
        @brief Setzt die Solltemperatur. Wenn None, wird die Heizung ausgeschaltet.
        @param temp: float oder None
        """
        self.target_temp = temp
        if temp is None:
            self.set_pwm_callback(self.heater_gpio, 0)
            self.heater_on = False

    def update_control(self, current_temp):
        """
        @fn update_control(current_temp)
        @brief Zyklische Methode. Wenn current_temp < (target-1), schaltet die Heizung an.
               Wenn current_temp > (target+1), schaltet sie aus.
        @param current_temp: float
        """
        if self.target_temp is None:
            return

        obere_schwelle = self.target_temp + 1
        untere_schwelle = self.target_temp - 1

        if self.heater_on and current_temp > obere_schwelle:
            self.heater_on = False
            self.set_pwm_callback(self.heater_gpio, 0)
        elif (not self.heater_on) and current_temp < untere_schwelle:
            self.heater_on = True
            self.set_pwm_callback(self.heater_gpio, 255)

class EnvironmentControl:

    def __init__(
            self,
            fan,
            atomizer,
            fridge,
            heater,
            led_green,
            led_red,
            led_orange,
            led_yellow,
            config
    ):
        self._fan = fan
        self._atomizer = atomizer
        self._fridge = fridge
        self._heater = heater
        self._config = config
        self._led_green = led_green
        self._led_red = led_red
        self._led_orange = led_orange
        self._led_yellow = led_yellow

    def control(self, temperature: float, humidity: float):
        self._control_fan(humidity)
        self._control_atomizer(humidity)
        self._control_fridge(temperature)
        self._control_heater(temperature)

    def _control_fan(self, humidity: float):
        if humidity >= (self._config.get_target_humidity() + self._config.get_humidity_tolerance()):
            self._fan.value(1)
            self._led_yellow.value(1)
        if humidity <= (self._config.get_target_humidity() - self._config.get_humidity_tolerance() / 2):
            self._fan.value(0)
            self._led_yellow.value(0)

    def _control_atomizer(self, humidity: float):
        if humidity <= (self._config.get_target_humidity() - self._config.get_humidity_tolerance()):
            self._atomizer.value(1)
            self._led_orange.value(1)
        if humidity >= (self._config.get_target_humidity() + self._config.get_humidity_tolerance() / 2):
            self._atomizer.value(0)
            self._led_orange.value(0)

    def _control_fridge(self, temperature: float):
        if temperature >= (self._config.get_target_temperature() + self._config.get_temperature_tolerance()):
            self._fridge.value(1)
            self._led_green.value(1)
        if temperature <= (self._config.get_target_temperature() - self._config.get_temperature_tolerance() / 2):
            self._fridge.value(0)
            self._led_green.value(0)

    def _control_heater(self, temperature: float):
        if temperature <= (self._config.get_target_temperature() - self._config.get_temperature_tolerance()):
            self._heater.value(1)
            self._led_red.value(1)
        if temperature >= (self._config.get_target_temperature() + self._config.get_temperature_tolerance() / 2):
            self._heater.value(0)
            self._led_red.value(0)

    def get_fan_state(self) -> bool:
        return bool(self._fan.value())

    def get_atomizer_state(self) -> bool:
        return bool(self._atomizer.value())

    def get_fridge_status(self) -> bool:
        return bool(self._fridge.value())

    def get_heater_status(self) -> bool:
        return bool(self._heater.value())

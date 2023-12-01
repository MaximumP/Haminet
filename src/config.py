import ujson
import os


class Config:
    _target_temperature: float
    _temperature_tolerance: float
    _target_humidity: float
    _humidity_tolerance: float
    _config_file: str

    def __init__(self, config_file: str = None):
        self._config_file = config_file
        self._target_temperature = 50
        self._target_humidity = 55
        self._temperature_tolerance = 2
        self._humidity_tolerance = 5
        if config_file:
            if config_file in os.listdir():
                self._read_config_file()
            else:
                self._write_config_file()

    def get_target_temperature(self):
        return self._target_temperature

    def set_target_temperature(self, value: float):
        if self._target_temperature != value:
            self._target_temperature = value
            self._write_config_file()

    def get_target_humidity(self):
        return self._target_humidity

    def set_target_humidity(self, value: float):
        if self._target_humidity != value:
            self._target_humidity = value
            self._write_config_file()

    def get_temperature_tolerance(self):
        return self._temperature_tolerance

    def set_temperature_tolerance(self, value: float):
        if self._temperature_tolerance != value:
            self._temperature_tolerance = value
            self._write_config_file()

    def get_humidity_tolerance(self):
        return self._humidity_tolerance

    def set_humidity_tolerance(self, value: float):
        if self._humidity_tolerance != value:
            self._humidity_tolerance = value
            self._write_config_file()

    def _read_config_file(self):
        with open(self._config_file, "r") as config_file:
            config = ujson.loads(config_file.read())
        if config:
            self._target_temperature = config.get("target_temperature")
            self._target_humidity = config.get("target_humidity")
            self._humidity_tolerance = config.get("humidity_tolerance")
            self._temperature_tolerance = config.get("temperature_tolerance")
            print("read config file")

    def _write_config_file(self):
        json = ujson.dumps({
            "target_temperature": self._target_temperature,
            "target_humidity": self._target_humidity,
            "humidity_tolerance": self._humidity_tolerance,
            "temperature_tolerance": self._temperature_tolerance
        })
        with open(self._config_file, "w") as config_file:
            config_file.write(json)
        print("created config file")

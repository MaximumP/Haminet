from unittest.mock import Mock, MagicMock

import pytest

from config import Config
from environment_control import EnvironmentControl


def get_control_mock() -> Mock:
    mock = Mock()
    mock.value = Mock()
    return mock


@pytest.mark.parametrize(
    "temperature, humidity, config_values, expected",
    [
        (
            24,
            70,
            {
                "target_temperature": 22,
                "temperature_tolerance": 2,
                "target_humidity": 70,
                "humidity_tolerance": 5
            },
            {
                "fan": None,
                "atomizer": None,
                "fridge": 1,
                "heater": 0
            }
        ),        (
            24,
            86,
            {
                "target_temperature": 22,
                "temperature_tolerance": 2,
                "target_humidity": 70,
                "humidity_tolerance": 5
            },
            {
                "fan": 1,
                "atomizer": 0,
                "fridge": 1,
                "heater": 0
            }
        ),
    ]
)
def test_control(temperature, humidity, config_values, expected):
    fan_mock = get_control_mock()
    atomizer_mock = get_control_mock()
    fridge_mock = get_control_mock()
    heater_mock = get_control_mock()
    config = Config()
    config.set_target_temperature(config_values["target_temperature"])
    config.set_temperature_tolerance(config_values["temperature_tolerance"])
    config.set_target_humidity(config_values["target_humidity"])
    config.set_humidity_tolerance(config_values["humidity_tolerance"])

    subject = EnvironmentControl(
        fan_mock,
        atomizer_mock,
        fridge_mock,
        heater_mock,
        get_control_mock(),
        get_control_mock(),
        get_control_mock(),
        get_control_mock(),
        config
    )
    subject.control(temperature, humidity)

    if expected["fan"] is None:
        fan_mock.value.assert_not_called()
    else:
        fan_mock.value.assert_called_with(expected["fan"])

    if expected["atomizer"] is None:
        atomizer_mock.value.assert_not_called()
    else:
        atomizer_mock.value.assert_called_with(expected["atomizer"])

    if expected["fridge"] is None:
        fridge_mock.value.assert_not_called()
    else:
        fridge_mock.value.assert_called_with(expected["fridge"])

    if expected["heater"] is None:
        heater_mock.value.assert_not_called()
    else:
        heater_mock.value.assert_called_with(expected["heater"])

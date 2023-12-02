from machine import Pin, Timer
from dht import DHT22
from config import Config
from debounce import DebouncedSwitch
from output import Pager
from environment_control import EnvironmentControl

dht = DHT22(Pin(22))
timer = Timer(-1)
up = Pin(12, Pin.IN, Pin.PULL_DOWN)
down = Pin(13, Pin.IN, Pin.PULL_DOWN)
edit = Pin(14, Pin.IN, Pin.PULL_DOWN)
enter = Pin(11, Pin.IN, Pin.PULL_DOWN)
page_button = Pin(15, Pin.IN, Pin.PULL_DOWN)

config = Config("config.json")
environment_control = EnvironmentControl(
    fan=Pin(16, mode=Pin.OUT, value=0),
    atomizer=Pin(17, mode=Pin.OUT, value=0),
    fridge=Pin(18, mode=Pin.OUT, value=0),
    heater=Pin(19, mode=Pin.OUT, value=0),
    config=config
)
pager = Pager(dht, config, environment_control)


def next_page(_=0):
    pager.next_page()


tmp_humidifier = Pin(20, Pin.OUT, value=0)
page_handler = DebouncedSwitch(page_button, next_page)
up_handler = DebouncedSwitch(up, lambda l: pager.cursor_up())
down_handler = DebouncedSwitch(down, lambda l: pager.cursor_down())
edit_handler = DebouncedSwitch(edit, lambda l: pager.edit())
enter_handler = DebouncedSwitch(enter, lambda l: tmp_humidifier.value(not tmp_humidifier.value()))


def main():
    while True:
        try:
            dht.measure()
            environment_control.control(dht.temperature(), dht.humidity())
            pager.display()
        except OSError as e:
            print(e)


main()

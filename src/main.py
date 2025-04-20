from time import sleep

from machine import Pin
from dht import DHT22
from config import Config
from debounce import DebouncedSwitch
from output import Pager
from environment_control import EnvironmentControl

up = Pin(17, Pin.IN, Pin.PULL_DOWN)
down = Pin(21, Pin.IN, Pin.PULL_DOWN)
edit = Pin(18, Pin.IN, Pin.PULL_DOWN)
# enter = Pin(11, Pin.IN, Pin.PULL_DOWN)
page_button = Pin(16, Pin.IN, Pin.PULL_DOWN)
dht_enable = Pin(15, Pin.OUT, value=1)
config = Config("config.json")
environment_control = EnvironmentControl(
    fan=Pin(12, mode=Pin.OUT, value=0),
    atomizer=Pin(20, mode=Pin.OUT, value=0),
    fridge=Pin(14, mode=Pin.OUT, value=0),
    heater=Pin(28, mode=Pin.OUT, value=0),
    led_green=Pin(0, Pin.OUT, value=0),
    led_red=Pin(1, Pin.OUT, value=0),
    led_orange=Pin(4, Pin.OUT, value=0),
    led_yellow=Pin(6, Pin.OUT, value=0),
    config=config,
)
dht = DHT22(Pin(22, Pin.PULL_UP))
pager = Pager(dht, config, environment_control)

page_handler = DebouncedSwitch(page_button, lambda l: pager.next_page())
up_handler = DebouncedSwitch(up, lambda l: pager.cursor_up())
down_handler = DebouncedSwitch(down, lambda l: pager.cursor_down())
edit_handler = DebouncedSwitch(edit, lambda l: pager.edit())


def reset_dht():
    dht_enable.value(0)
    sleep(1)
    dht_enable.value(1)
    print("Recovered")


def main():
    while True:
        try:
            dht.measure()
            print(f"Measured: {dht.temperature()} {dht.humidity()}")
            environment_control.control(dht.temperature(), dht.humidity())
            pager.display()
        except OSError as e:
            print("Failure")
            reset_dht()
            print(e)


main()

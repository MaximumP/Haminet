from time import sleep

from machine import Pin, Timer
from dht import DHT22
from config import Config
from debounce import DebouncedSwitch

from output import Pager
from environment_control import EnvironmentControl

dht = DHT22(Pin(22, Pin.PULL_UP))
timer = Timer(-1)
up = Pin(17, Pin.IN, Pin.PULL_DOWN)
down = Pin(19, Pin.IN, Pin.PULL_DOWN)
edit = Pin(18, Pin.IN, Pin.PULL_DOWN)
# enter = Pin(11, Pin.IN, Pin.PULL_DOWN)
page_button = Pin(16, Pin.IN, Pin.PULL_DOWN)

config = Config("config.json")
environment_control = EnvironmentControl(
    fan=Pin(12, mode=Pin.OUT, value=0),
    atomizer=Pin(13, mode=Pin.OUT, value=0),
    fridge=Pin(14, mode=Pin.OUT, value=0),
    heater=Pin(15, mode=Pin.OUT, value=0),
    led_green=Pin(0, Pin.OUT, value=0),
    led_red=Pin(1, Pin.OUT, value=0),
    led_orange=Pin(4, Pin.OUT, value=0),
    led_yellow=Pin(6, Pin.OUT, value=0),
    config=config,
)
pager = Pager(dht, config, environment_control)

page_handler = DebouncedSwitch(page_button, lambda l: pager.next_page())
up_handler = DebouncedSwitch(up, lambda l: pager.cursor_up())
down_handler = DebouncedSwitch(down, lambda l: pager.cursor_down())
edit_handler = DebouncedSwitch(edit, lambda l: pager.edit())


def main():
    while True:
        try:
            dht.measure()
        except OSError as e:
            dht.temperature = lambda: 32
            dht.humidity = lambda: 50
            dht.measure = lambda: None
            print(e)
        try:
            environment_control.control(dht.temperature(), dht.humidity())
            pager.display()
        except OSError as e:
            print(e)


def start_up():
    environment_control._led_orange.value(1)
    sleep(0.5)
    environment_control._led_red.value(1)
    sleep(0.5)
    environment_control._led_green.value(1)
    sleep(0.5)
    environment_control._led_yellow.value(1)
    sleep(0.5)

    environment_control._led_orange.value(0)
    sleep(0.5)
    environment_control._led_red.value(0)
    sleep(0.5)
    environment_control._led_green.value(0)
    sleep(0.5)
    environment_control._led_yellow.value(0)


# start_up()
main()

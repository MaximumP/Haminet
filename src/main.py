from time import sleep

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
# enter = Pin(11, Pin.IN, Pin.PULL_DOWN)
page_button = Pin(15, Pin.IN, Pin.PULL_DOWN)

config = Config("config.json")
environment_control = EnvironmentControl(
    fan=Pin(16, mode=Pin.OUT, value=0),
    atomizer=Pin(11, mode=Pin.OUT, value=0),
    fridge=Pin(17, mode=Pin.OUT, value=0),
    heater=Pin(18, mode=Pin.OUT, value=0),
    config=config
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
            environment_control.control(dht.temperature(), dht.humidity())
            pager.display()
        except OSError as e:
            print(e)


def start_up():
    environment_control.led_orange.value(1)
    sleep(.5)
    environment_control.led_red.value(1)
    sleep(.5)
    environment_control.led_green.value(1)
    sleep(.5)
    environment_control.led_yellow.value(1)
    sleep(.5)

    environment_control.led_orange.value(0)
    sleep(.5)
    environment_control.led_red.value(0)
    sleep(.5)
    environment_control.led_green.value(0)
    sleep(.5)
    environment_control.led_yellow.value(0)


# start_up()
main()

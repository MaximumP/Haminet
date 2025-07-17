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
dht_enable = Pin(1, Pin.OUT, value=1)
page_button = Pin(16, Pin.IN, Pin.PULL_DOWN)
error: Exception | None = None

config = Config("config.json")
environment_control = EnvironmentControl(
    fan=Pin(12, mode=Pin.OUT, value=0),
    atomizer=Pin(13, mode=Pin.OUT, value=0),
    fridge=Pin(14, mode=Pin.OUT, value=0),
    heater=Pin(15, mode=Pin.OUT, value=0),
    config=config,
)
pager = Pager(dht, config, environment_control)


def button_handler(pin: Pin):
    global error
    if error:
        error = None
        return
    if pin == up:
        pager.cursor_up()
    if pin == down:
        pager.cursor_down()
    if pin == edit:
        pager.edit()
    if pin == page_button:
        pager.next_page()


tim = Timer()


def measure(pin: Pin | None = None):
    global error
    try:
        print("measure")
        dht.measure()
    except OSError as e:
        tim.deinit()
        error = e
        print(e)


def reset_dht():
    dht_enable.value(0)
    sleep(1)
    dht_enable.value(1)
    sleep(3)
    tim.init(mode=Timer.PERIODIC, period=3000, callback=measure)
    print("Recovered")


page_handler = DebouncedSwitch(page_button, button_handler)
up_handler = DebouncedSwitch(up, button_handler)
down_handler = DebouncedSwitch(down, button_handler)
edit_handler = DebouncedSwitch(edit, button_handler)


def main():
    global error
    tmp = 0.0
    humidity = 0.0
    print("startup wait")
    sleep(1)
    measure()
    tim.init(mode=Timer.PERIODIC, period=3000, callback=measure)
    print("startup completed")
    while True:
        tmp = dht.temperature()
        humidity = dht.humidity()
        try:
            environment_control.control(tmp, humidity)
            if error:
                pager.error(error)
                error = None
                reset_dht()
            else:
                pager.display()
        except OSError as e:
            print(e)


main()

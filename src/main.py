from time import sleep

from framebuf import RGB565, FrameBuffer
from typing import Callable
from micropython import schedule
from machine import Pin, Timer
from dht import DHT22
from config import Config
from debounce import DebouncedSwitch

from display.pages import ConfigPage, ErrorPage, OverviewPage
from output import Pager
from environment_control import EnvironmentControl

dht = DHT22(Pin(22, Pin.PULL_UP))
timer = Timer(-1)
up = Pin(17, Pin.IN, Pin.PULL_DOWN)
down = Pin(21, Pin.IN, Pin.PULL_DOWN)
edit = Pin(18, Pin.IN, Pin.PULL_DOWN)
# enter = Pin(11, Pin.IN, Pin.PULL_DOWN)
page_button = Pin(16, Pin.IN, Pin.PULL_DOWN)
dht_enable = Pin(13, Pin.OUT, value=1)
error: Exception | None = None

config = Config("config.json")
environment_control = EnvironmentControl(
    fan=Pin(12, mode=Pin.OUT, value=0),
    atomizer=Pin(15, mode=Pin.OUT, value=0),
    fridge=Pin(14, mode=Pin.OUT, value=0),
    heater=Pin(28, mode=Pin.OUT, value=0),
    config=config,
)
buffer = bytearray(176 * 220 * 2)  # 2 bytes per pixel (RGB565)
framebuffer = FrameBuffer(buffer, 176, 220, RGB565)
overview_page = OverviewPage(framebuffer, 176, 220)
config_page = ConfigPage(framebuffer, 176, 220, config)
error_page = ErrorPage(framebuffer, 176, 220)
pages = [
    overview_page,
    config_page,
    error_page
]
pager = Pager(environment_control, pages, framebuffer)


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


class Scheduler:

    def __init__(self, dht: DHT22, dht_enable: Pin, fan_control):
        self._dht_enable = dht_enable
        self._timer = Timer()
        self._dht = dht
        cb = self._timer_cb
        self._measure_cb = self._measure
        self._fan_control = fan_control
        self._log_cb = self._log
        self._timer.init(mode=Timer.PERIODIC, period=1000, callback=cb)

    def _log(self, message: str):
        print(message)

    def _timer_cb(self, timer):
        self._increment_counter = self._increment_counter + 1
        if self._increment_counter % 3 == 0:
            schedule(self._log_cb, "Scheduled measure")
            schedule(self._measure_cb, None)
        if self._increment_counter % 60 == 0:
            schedule(self._log_cb, "Schedule fan control")
            schedule(self._fan_control, self._increment_counter)
            self._increment_counter = 0

    def _measure(self):
        try:
            if self._dht_enable.value() == 0:
                self._dht.measure()
            else:
                self._dht_enable.value(1)
        except OSError as e:
            print(e)
            self._dht_enable.value(0)

tim = Timer()
timer_cnt = 0



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
        overview_page.set_data(
            dht.temperature(),
            dht.humidity(),
            config.get_target_temperature(),
            config.get_humidity_tolerance()
        )
        tmp = dht.temperature()
        humidity = dht.humidity()
        try:
            environment_control.control(tmp, humidity)
            if error:
                error_page.set_data(error)
                pager.set_page(error_page)
                error = None
                reset_dht()
        except OSError as e:
            print(e)

        pager.display()


main()

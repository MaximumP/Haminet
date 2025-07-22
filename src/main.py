from framebuf import RGB565, FrameBuffer
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
fan = Pin(12, mode=Pin.OUT, value=0)

config = Config("config.json")
environment_control = EnvironmentControl(
    fan=fan,
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
pager = Pager(environment_control, pages, framebuffer, buffer)


def button_handler(pin: Pin):
    if pin == up:
        pager.cursor_up()
    if pin == down:
        pager.cursor_down()
    if pin == edit:
        pager.edit()
    if pin == page_button:
        pager.next_page()


class Scheduler:
    _err_cnt = 0

    def __init__(self, dht: DHT22, dht_enable: Pin, fan_control):
        self._increment_counter = 0
        self._dht_enable = dht_enable
        self._timer = Timer()
        self._dht = dht
        cb = self._timer_cb
        self._fan_control = fan_control
        self._timer.init(mode=Timer.PERIODIC, period=1000, callback=cb)

    def reset_counter(self):
        self._increment_counter = 0

    def counter(self):
        return self._increment_counter

    def _timer_cb(self, timer):
        self._increment_counter = self._increment_counter + 1
        if self._increment_counter % 3 == 0:
            schedule(self._measure, None)
        if self._increment_counter % 60 == 0:
            schedule(self._fan_control, self)

    def _measure(self, args):
        try:
            if self._dht_enable.value() == 1:
                self._dht.measure()
            else:
                self._dht_enable.value(1)
        except OSError as e:
            self._err_cnt = self._err_cnt + 1
            print(f"{e} {self._err_cnt}")
            self._dht_enable.value(0)


page_handler = DebouncedSwitch(page_button, button_handler)
up_handler = DebouncedSwitch(up, button_handler)
down_handler = DebouncedSwitch(down, button_handler)
edit_handler = DebouncedSwitch(edit, button_handler)

def fan_control(scheduler: Scheduler):
    if fan.value() == 1:
        if (config.get_fan_on_interval() * 60) <= scheduler.counter():
            print("Fan off")
            fan.value(0)
            scheduler.reset_counter()
    else:
        if (config.get_fan_off_interval() * 60) <= scheduler.counter():
            print("Fan on")
            fan.value(1)
            scheduler.reset_counter()


def main():
    tmp = 0.0
    humidity = 0.0
    scheduler = Scheduler(dht, dht_enable, fan_control)
    log = True
    while True:
        if scheduler.counter() % 10 == 0:
            if log:
                print(f"Temperature:\t\t {dht.temperature()}")
                print(f"Humidity:\t\t {dht.humidity()}")
                print(f"Target temperature:\t {config.get_target_temperature()}")
                print(f"Target humidity:\t {config.get_target_humidity()}")
                print(f"Fan state:\t\t {environment_control.get_fan_state()}")
                print(f"Fan on intervall:\t {config.get_fan_on_interval()}")
                print(f"Fan off intervall:\t {config.get_fan_off_interval()}\n")
                log = False
        else:
            log = True
        overview_page.set_data(
            dht.temperature(),
            dht.humidity(),
            config.get_target_temperature(),
            config.get_target_humidity(),
            environment_control.get_fan_state(),
            config.get_fan_on_interval(),
            config.get_fan_off_interval(),
            scheduler.counter()
        )
        tmp = dht.temperature()
        humidity = dht.humidity()
        try:
            environment_control.control(tmp, humidity)
        except OSError as e:
            print(e)

        pager.display()


main()

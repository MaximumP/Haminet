from dht import DHT22
import framebuf
from machine import SPI, Pin
from config import Config
from display.ili9225 import COLOR_BLUE, COLOR_GREEN, ILI9225
from display.pages import Page
from environment_control import EnvironmentControl

COLOR_BLACK = 0x0000  # 0,   0,   0
COLOR_WHITE = 0xFFFF  # 255, 255, 255
COLOR_RED = 0xF800  # 255,   0,   0
COLOR_YELLOW = 0xFFE0  # 255, 255,   0


class Pager:
    _page = 0
    _cursor = 0
    _edit_mode = False
    _edit_value = 0
    _clear = False
    _config: Config
    _environment: EnvironmentControl
    _display: ILI9225

    def __init__(
        self,
        environment: EnvironmentControl,
        pages: list[Page],
        framebuffer: framebuf.FrameBuffer,
        buffer: bytearray,
    ):
        self._environment = environment
        self._display_led = Pin(7, Pin.OUT, value=1)
        spi = SPI(0, baudrate=40000000, sck=Pin(2), mosi=Pin(3))
        self._display = ILI9225(spi, 5, 8, 9, framebuffer, buffer)
        self._pages = pages

    def next_page(self):
        self._clear = True
        if self._page == 0:
            self._page = 1
        else:
            self._page = 0
            self._edit_mode = False
            self._edit_value = 0

    def cursor_up(self):
        self._pages[self._page].handle_button_up()
        # if self._page == 0:
        #     return
        # if self._edit_mode:
        #     self._edit_value += 0.5
        #     return
        # if self._cursor > 0:
        #     self._cursor -= 1
        # else:
        #     self._cursor = 3

    def cursor_down(self):
        self._pages[self._page].handle_button_down()
        # if self._page == 0:
        #     return
        # if self._edit_mode:
        #     self._edit_value -= 0.5
        #     return
        # if self._cursor < 3:
        #     self._cursor += 1
        # else:
        #     self._cursor = 0

    def set_page(self, page: Page):
        try:
            index = self._pages.index(page)
            self._page = index
        except ValueError as e:
            print(e)

    def edit(self):
        self._pages[self._page].handle_button_enter()
        # if self._page == 0:
        #     return

        # self._edit_mode = not self._edit_mode
        # if self._edit_mode:
        #     if self._cursor == 0:
        #         self._edit_value = self._config.get_target_temperature()
        #     elif self._cursor == 1:
        #         self._edit_value = self._config.get_temperature_tolerance()
        #     elif self._cursor == 2:
        #         self._edit_value = self._config.get_target_humidity()
        #     elif self._cursor == 3:
        #         self._edit_value = self._config.get_humidity_tolerance()
        # else:
        #     if self._cursor == 0:
        #         self._config.set_target_temperature(self._edit_value)
        #     elif self._cursor == 1:
        #         self._config.set_temperature_tolerance(self._edit_value)
        #     elif self._cursor == 2:
        #         self._config.set_target_humidity(self._edit_value)
        #     elif self._cursor == 3:
        #         self._config.set_humidity_tolerance(self._edit_value)
        #     self._edit_value = 0

    def display(self):
        self._pages[self._page].render()
        self._display.update()

    def toggle_power(self):
        self._display_led.value(not self._display_led.value())

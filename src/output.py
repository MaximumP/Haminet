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


    def __init__(self, environment: EnvironmentControl, pages: list[Page], framebuffer: framebuf.FrameBuffer):
        self._environment = environment
        self._display_led = Pin(7, Pin.OUT, value=1)
        spi = SPI(0, baudrate=40000000, sck=Pin(2), mosi=Pin(3))
        self._display = ILI9225(spi, 5, 8, 9, framebuffer)
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
        if self._page == 0:
            return
        if self._edit_mode:
            self._edit_value += 0.5
            return
        if self._cursor > 0:
            self._cursor -= 1
        else:
            self._cursor = 3

    def cursor_down(self):
        if self._page == 0:
            return
        if self._edit_mode:
            self._edit_value -= 0.5
            return
        if self._cursor < 3:
            self._cursor += 1
        else:
            self._cursor = 0

    def set_page(self, page: Page):
        try:
            index = self._pages.index(page)
            self._page = index
        except ValueError as e:
            print(e)

    def edit(self):
        if self._page == 0:
            return

        self._edit_mode = not self._edit_mode
        if self._edit_mode:
            if self._cursor == 0:
                self._edit_value = self._config.get_target_temperature()
            elif self._cursor == 1:
                self._edit_value = self._config.get_temperature_tolerance()
            elif self._cursor == 2:
                self._edit_value = self._config.get_target_humidity()
            elif self._cursor == 3:
                self._edit_value = self._config.get_humidity_tolerance()
        else:
            if self._cursor == 0:
                self._config.set_target_temperature(self._edit_value)
            elif self._cursor == 1:
                self._config.set_temperature_tolerance(self._edit_value)
            elif self._cursor == 2:
                self._config.set_target_humidity(self._edit_value)
            elif self._cursor == 3:
                self._config.set_humidity_tolerance(self._edit_value)
            self._edit_value = 0

    def display(self):
        self._pages[self._page].render()
        self._display.update()
        # if self._page == 0:
        #     self._overview_page.set_data(
        #         self._dht.temperature(),
        #         self._dht.humidity(),
        #         self._config._target_temperature,
        #         self._config._target_humidity
        #     )
        #     self._overview_page.render()
        #     self._display.update()
        # else:
        #     self._config_page.set_data(self._cursor)
        #     self._config_page.render()
        #     self._display.update()
        # if self._clear:
        #     self._clear = False
        #     self._display.fill(COLOR_BLACK)
        # if self._page == 0:
        #     self._display_overview_page()
        # else:
        #     self._display_edit_page()

    # def error(self, message: Exception):
    #     self._error_page.set_data(message)
    #     self._error_page.render()
    #     self._display.update()

    def toggle_power(self):
        self._display_led.value(not self._display_led.value())

    # def _display_overview_page(self):
    #     temperature = f"{self._dht.temperature():.1f}"
    #     humidity = f"{self._dht.humidity():.1f} %"
    #     temp_color = (
    #         COLOR_RED
    #         if self._environment.get_fridge_status()
    #         or self._environment.get_heater_status()
    #         else COLOR_GREEN
    #     )
    #     # Clear
    #     self._display.rect(x=0, y=0, width=self._display._width, height=self._display._height, color=COLOR_BLACK)

    #     x, y = self._display.scaled_text(string=temperature, x=5, y=5, c=temp_color, s=2)
    #     self._display.ellipse(x=x + 8, y=5, xr=4, yr=4, color=temp_color)
    #     # Line 2
    #     self._display.text(
    #         string=f"{self._config._target_temperature} +- {self._config.get_temperature_tolerance()}",
    #         x=5,
    #         y=25,
    #         color=COLOR_WHITE,
    #     )

    #     humidity_color = (
    #         COLOR_RED
    #         if self._environment.get_atomizer_state()
    #         else COLOR_BLUE
    #     )
    #     # Line 3
    #     self._display.scaled_text(string=humidity, x=5, y=45, c=humidity_color, s=2)
    #     # Line 4
    #     self._display.text(
    #         string=f"{self._config.get_target_humidity()} +- {self._config.get_humidity_tolerance()}",
    #         x=5,
    #         y=65,
    #         color=COLOR_WHITE,
    #     )
    #     self._display.update()

    #     # y_offset -= line_height_medium + 5
    #     # display.fillRectangle(5, y_offset, icons.width * 3, icons.height, COLOR_BLACK)
    #     # if self._environment.get_fan_state():
    #     #    icons.text(5, y_offset, "0", COLOR_WHITE)

    #     # if self._environment.get_atomizer_state():
    #     #    icons.text(5, y_offset, "1", COLOR_BLUE)

    #     # if self._environment.get_fridge_status():
    #     #    icons.text(10 + icons.width, y_offset, "2", COLOR_TURQUOISE)

    #     # if self._environment.get_heater_status():
    #     #    icons.text(10 + icons.width, y_offset, "3", COLOR_RED)

    # def _display_edit_page(self):
    #     # Clear
    #     self._display.rect(x=0, y=0, width=self._display._width, height=self._display._height, color=COLOR_BLACK)

    #     self._display.scaled_text(string=f"Temperatur: {self._edit_value if self._edit_mode and self._cursor == 0 else self._config.get_target_temperature()}", x=5 , y=5, c=self._get_font_color(0), s=1)
    #     self._display.scaled_text(string=f"Toleranz: {self._edit_value if self._edit_mode and self._cursor == 1 else self._config.get_temperature_tolerance()}", x=5, y=25, c=self._get_font_color(1), s=1)
    #     self._display.rect(0, 40, width=self._display._width, height=1, color=COLOR_WHITE,fill=True)
    #     self._display.scaled_text(string=f"Luftfeuchtigkeit: {self._edit_value if self._edit_mode and self._cursor == 2 else self._config.get_target_humidity()}", x=5, y=60, c=self._get_font_color(2), s=1)
    #     self._display.scaled_text(string=f"Toleranz: {self._edit_value if self._edit_mode and self._cursor == 3 else self._config.get_humidity_tolerance()}", x=5, y=80, c=self._get_font_color(3), s=1)
    #     self._display.update()

    # def _get_font_color(self, cursor: int):
    #     if self._cursor == 0 and cursor == 0:
    #         return COLOR_YELLOW if self._edit_mode else COLOR_BLUE
    #     if self._cursor == 1 and cursor == 1:
    #         return COLOR_YELLOW if self._edit_mode else COLOR_GREEN
    #     if self._cursor == 2 and cursor == 2:
    #         return COLOR_YELLOW if self._edit_mode else COLOR_GREEN
    #     if self._cursor == 3 and cursor == 3:
    #         return COLOR_YELLOW if self._edit_mode else COLOR_GREEN

    #     return COLOR_WHITE


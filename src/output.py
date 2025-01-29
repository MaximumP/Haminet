from machine import SPI, Pin
from config import Config
from display.TFT_22_ILI9225 import (
    TFT_22_ILI9225 as Display,
    COLOR_BLUE,
    COLOR_TURQUOISE,
)
from display.adafruit_gfx import GFX
from display.fonts.Icons16x16 import Icons16x16
from display.fonts.Terminal6x8 import Terminal6x8
from display.fonts.TimesNR16x16 import TimesNR16x16
from display.fonts.TimesNR39x37 import TimesNR39x37
from display.glcFont import glcFont
from environment_control import EnvironmentControl

COLOR_BLACK = 0x0000  # 0,   0,   0
COLOR_WHITE = 0xFFFF  # 255, 255, 255
COLOR_GREEN = 0x07E0  # 0, 255,   0
COLOR_RED = 0xF800  # 255,   0,   0
COLOR_YELLOW = 0xFFE0  # 255, 255,   0

spi = SPI(0, baudrate=40000000, sck=Pin(2), mosi=Pin(3))
display = Display(spi, dc=Pin(8), cs=Pin(5), rst=Pin(9))
display.clear()
display.setOrientation(0)
font_small = glcFont(display, Terminal6x8, eraseMode=True)
font_medium = glcFont(display, TimesNR16x16, eraseMode=True)
font_big = glcFont(display, TimesNR39x37, eraseMode=True)
icons = glcFont(display, Icons16x16, eraseMode=True)
gfx = GFX(
    176,
    220,
    display.drawPixel,
    hline=display.fastHline,
    vline=display.fastVline,
    fill_rect=display.fillRectangle,
)
display.setBackgroundColor(0x0000)


class Pager:
    _page = 0
    _cursor = 0
    _edit_mode = False
    _edit_value = 0
    _clear = False
    _dht = None
    _config: Config = None
    _environment: EnvironmentControl

    def __init__(self, dht, config: Config, environment: EnvironmentControl):
        self._dht = dht
        self._config = config
        self._environment = environment
        self._display_led = Pin(7, Pin.OUT, value=1)

    def next_page(self):
        self._clear = True
        if self._page == 0:
            self._page = 1
        else:
            self._page = 0
            self._edit_mode = False
            self._edit_value = None

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
            self._edit_value = None

    def display(self):
        if self._clear:
            self._clear = False
            display.clear()
        if self._page == 0:
            self._display_overview_page()
        else:
            self._display_edit_page()

    def toggle_power(self):
        self._display_led.value(not self._display_led.value())

    def _display_overview_page(self):
        line_height_medium = font_medium.height + 4
        line_height_big = font_big.height + 2
        temperature = f"{self._dht.temperature():.1f}"
        humidity = f"{self._dht.humidity():.1f}"
        y_offset = display.height - line_height_big
        temp_color = (
            COLOR_RED
            if self._environment.get_fridge_status()
            or self._environment.get_heater_status()
            else COLOR_GREEN
        )
        font_big.text(5, y_offset, temperature, temp_color)
        x = font_big.getTextWidth(temperature) + 10
        font_medium.text(
            x, y_offset + (font_big.height - font_medium.height), "~", temp_color
        )
        y_offset -= line_height_medium
        font_medium.text(
            5,
            y_offset,
            f"({self._config.get_target_temperature()} +- {self._config.get_temperature_tolerance()})",
            COLOR_WHITE,
        )
        y_offset -= line_height_big + 5
        humidity_color = (
            COLOR_RED
            if self._environment.get_atomizer_state()
            or self._environment.get_fan_state()
            else COLOR_GREEN
        )
        font_big.text(5, y_offset, humidity, humidity_color)
        x = font_big.getTextWidth(humidity) + 10
        font_medium.text(
            x,
            y_offset + (font_big.height - int(font_medium.height * 1.5)),
            "%",
            humidity_color,
        )
        y_offset -= line_height_medium
        font_medium.text(
            5,
            y_offset,
            f"({self._config.get_target_humidity()} +- {self._config.get_humidity_tolerance()})",
            COLOR_WHITE,
        )
        y_offset -= line_height_medium + 5
        # if self._environment.state_changed():
        display.fillRectangle(5, y_offset, icons.width * 3, icons.height, COLOR_BLACK)
        if self._environment.get_fan_state():
            icons.text(5, y_offset, "0", COLOR_WHITE)

        if self._environment.get_atomizer_state():
            icons.text(5, y_offset, "1", COLOR_BLUE)

        if self._environment.get_fridge_status():
            icons.text(10 + icons.width, y_offset, "2", COLOR_TURQUOISE)

        if self._environment.get_heater_status():
            icons.text(10 + icons.width, y_offset, "3", COLOR_RED)

    def _display_edit_page(self):
        edit_lines = [
            {
                "text": f"Temperatur: {self._edit_value if self._edit_mode and self._cursor == 0 else self._config.get_target_temperature()}",
                "color": self._get_font_color(0),
            },
            {
                "text": f"Toleranz: {self._edit_value if self._edit_mode and self._cursor == 1 else self._config.get_temperature_tolerance()}",
                "color": self._get_font_color(1),
            },
            {"text": "", "color": COLOR_WHITE},
            {"text": "", "color": COLOR_WHITE},
            {
                "text": f"Luftfeuchtigkeit: {self._edit_value if self._edit_mode and self._cursor == 2 else self._config.get_target_humidity()}",
                "color": self._get_font_color(2),
            },
            {
                "text": f"Toleranz: {self._edit_value if self._edit_mode and self._cursor == 3 else self._config.get_humidity_tolerance()}",
                "color": self._get_font_color(3),
            },
        ]
        self._print_to_display(edit_lines)

    def _get_font_color(self, cursor: int):
        if self._cursor == 0 and cursor == 0:
            return COLOR_YELLOW if self._edit_mode else COLOR_GREEN
        if self._cursor == 1 and cursor == 1:
            return COLOR_YELLOW if self._edit_mode else COLOR_GREEN
        if self._cursor == 2 and cursor == 2:
            return COLOR_YELLOW if self._edit_mode else COLOR_GREEN
        if self._cursor == 3 and cursor == 3:
            return COLOR_YELLOW if self._edit_mode else COLOR_GREEN

        return COLOR_WHITE

    def _print_to_display(self, lines, font=font_small):
        line_height = font.height + 6
        line = display.height - line_height
        for idx, text_line in enumerate(lines):
            y_offset = line - line_height * idx
            if self._edit_mode and self._cursor == line:
                display.fillRectangle(
                    5,
                    y_offset,
                    display.height,
                    font.height,
                    display.getBackgroundColor(),
                )
            font.text(5, y_offset, text_line.get("text"), text_line.get("color"))

from framebuf import FrameBuffer
from config import Config
from display.fonts.petme128_8x8 import font as petme
from random import randint
import errno

from display.ili9225 import (
    COLOR_BLACK,
    COLOR_MAGENTA,
    COLOR_WHITE,
    COLOR_RED,
    COLOR_GREEN as COLOR_BLUE,
    COLOR_LIGHTGREEN as COLOR_LIGHTBLUE,
    COLOR_BLUE as COLOR_GREEN,
    COLOR_LIGHTBLUE as COLOR_LIGHTGREEN,
)


class Page:
    _framebuffer: FrameBuffer
    _width: int
    _height: int
    _cleared: bool = False

    def __init__(self, framebuffer: FrameBuffer, width: int, height: int):
        self._framebuffer = framebuffer
        self._width = width
        self._height = height

    def clear(self):
        self._framebuffer.rect(0, 0, self._width, self._height, COLOR_BLACK, True)
        self._cleared = True

    def scaled_text(self, string, x, y, c, s=2) -> tuple[int, int]:
        x0 = x
        y0 = y
        iterator = list(range(8)) * s
        iterator.sort()
        for char in string:
            char_index = (ord(char) - 32) * 8
            for column_offset in iterator:
                column = petme[char_index + column_offset]
                # todo loop s times
                for pixel_offset in range(8):
                    pixel = column >> pixel_offset
                    if pixel & 1:
                        y00 = pixel_offset * s + y0
                        for y_offset in range(s):
                            self._framebuffer.pixel(x0, y00 + y_offset, c)
                x0 = x0 + 1
        return (x0, y + 8 * s)

    def render(self):
        pass


class OverviewPage(Page):
    _temperature: float = 0.0
    _humidity: float = 0.0
    _target_temperature: float = 0.0
    _target_humidity: float = 0.0
    _fan_state: bool = False
    _fan_on_time: int = 0
    _fan_off_time: int = 0
    _counter: int = 0
    _blink: bool = True

    def set_data(
        self,
        temperature: float,
        humidity: float,
        target_temperature: float,
        target_humidity: float,
        fan_state: bool,
        fan_on_time: int,
        fan_off_time: int,
        counter: int
    ):
        self._temperature = temperature
        self._humidity = humidity
        self._target_temperature = target_temperature
        self._target_humidity = target_humidity
        self._fan_state = fan_state
        self._fan_on_time = fan_on_time
        self._fan_off_time = fan_off_time
        self._counter = counter

    def _remaining_time(self, minutes: int, seconds: int):
        # Convert total time in seconds
        total_seconds = minutes * 60 - seconds

        # Handle negative values
        if total_seconds < 0:
            return "0:00"

        # Convert back to minutes and seconds
        m = total_seconds // 60
        s = total_seconds % 60

        return f"{m}:{s:02}"

    def render(self):
        self.clear()

        color = COLOR_GREEN if self._blink else COLOR_BLACK
        self._blink = not self._blink
        self._framebuffer.rect(self._width - 15, 5, 10, 10, color, True)

        self._framebuffer.text("Temperatur", 2, 2, COLOR_WHITE)
        x, y = self.scaled_text(f"{self._temperature:.1f}", 5, 16, COLOR_GREEN)
        self._framebuffer.ellipse(x + 8, 16, 4, 4, COLOR_GREEN, False)
        self._framebuffer.text("Soll", 5, 42, COLOR_WHITE)
        self._framebuffer.text(f"{self._target_temperature:.1f}", 5, 54, COLOR_LIGHTGREEN)

        offset = int(self._height / 3)
        self._framebuffer.text(
            "Feuchtigkeit", 2, offset, COLOR_WHITE
        )

        self.scaled_text(
            f"{self._humidity:.1f} %", 5, offset + 16, COLOR_BLUE
        )
        self._framebuffer.text("Soll", 5, offset + 42, COLOR_WHITE)
        self._framebuffer.text(f"{self. _target_humidity:.1f}", 5, offset + 54, COLOR_LIGHTBLUE)
        self._cleared = False

        offset = 2 * int(self._height / 3)
        self._framebuffer.text(
            "Luefter", 2, offset, COLOR_WHITE
        )
        time = self._fan_on_time if self._fan_state else self._fan_off_time
        #print(f"off: {self._fan_off_time} on: {self._fan_on_time}, time: {time}, state: {self._fan_state}")
        self._framebuffer.text(
            f"Luefter {'aus' if self._fan_state else 'an'} in {self._remaining_time(time, self._counter)}",
            5,
            offset + 2 * 16, COLOR_WHITE
        )

class ConfigPage(Page):
    _config: Config
    _cursor: int = 0

    def __init__(self, framebuffer: FrameBuffer, width: int, height: int, config: Config):
        self._config = config
        super().__init__(framebuffer, width, height)

    def set_data(self, cursor: int):
        self._cursor = cursor

    def render(self):
        self.clear()
        self._framebuffer.text("Konfiguration", 2, 2, COLOR_WHITE)
        self._framebuffer.text("Soll Temperatur", 5, 16, COLOR_WHITE)
        self._framebuffer.text(f"{self._config.get_target_temperature()}", 5, 30, COLOR_GREEN)

class ErrorPage(Page):
    _error: Exception | None = None

    def set_data(
        self,
        error: Exception | None
    ): 
        self._error = error

    def render(self):
        self.clear()
        self.scaled_text("Error", 2, 2, COLOR_RED)
        if isinstance(self._error, OSError) and isinstance(self._error.errno, int):
            self._framebuffer.text(str(self._error.errno), 5, 20, COLOR_RED)
            self._framebuffer.text(errno.errorcode[self._error.errno], 5, 40, COLOR_RED)
        else:
            self._framebuffer.text(self._error, 5, 16, COLOR_RED)



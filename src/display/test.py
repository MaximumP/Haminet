from framebuf import FrameBuffer, RGB565
from machine import Pin, SPI
from time import sleep


class ILI9225:
    def __init__(
        self,
        spi: SPI,
        chip_select_pin: int,
        data_command_pin: int,
        reset_pin: int,
        width=176,
        height=220,
    ):
        self._spi = spi
        self._chip_select = Pin(chip_select_pin, Pin.OUT, value=1)
        self._data_command = Pin(data_command_pin, Pin.OUT, value=0)
        self._reset = Pin(reset_pin, Pin.OUT, value=1)
        self._width = width
        self._height = height

        self._buffer = bytearray(width * height * 2)  # 2 bytes per pixel (RGB565)
        self._fb = FrameBuffer(self._buffer, self._width, self._height, RGB565)

        self._init_display()

    def _init_display(self):
        """Initialize the display."""
        self._reset_display()

        # Driver Output Control
        self.write_command(0x01)
        self.write_data(0x031C)

        # AC Driving Control
        self.write_command(0x02)
        self.write_data(0x0100)

        # Entry Mode
        self.write_command(0x03)
        self.write_data(0x1030)

        # Power control
        self.write_command(0x10)
        self.write_data(0x0000)  # SAP, BT[3:0], AP, DSTB, SLP, STB
        self.write_command(0x11)
        self.write_data(0x0000)  # DC1[2:0], DC0[2:0], VC[2:0]
        self.write_command(0x12)
        self.write_data(0x0000)  # VREG1OUT voltage
        self.write_command(0x13)
        self.write_data(0x0000)  # VDV[4:0] for VCOM amplitude
        self.write_command(0x14)
        self.write_data(0x0000)  # VCM[4:0] for VCOMH

        # Power-on sequence
        sleep(0.05)
        self.write_command(0x11)
        self.write_data(0x0018)  # Reference voltage (VC[2:0])=1.65V
        sleep(0.05)
        self.write_command(0x12)
        self.write_data(0x6121)  # Power control
        self.write_command(0x13)
        self.write_data(0x006F)  # VDV[4:0]=01111
        self.write_command(0x14)
        self.write_data(0x495F)  # VCM=1.02V
        self.write_command(0x10)
        self.write_data(0x0800)  # SAP=0x08
        sleep(0.05)

        # Driver output control
        self.write_command(0x01)
        self.write_data(0x011C)  # Driver output control

        # LCD driving control
        self.write_command(0x02)
        self.write_data(0x0100)

        # Entry mode
        self.write_command(0x03)
        self.write_data(0x1030)  # BGR=1, I/D=3 (increment in X and Y)

        # Display control
        self.write_command(0x07)
        self.write_data(0x1017)  # D1=1, D0=1 (Display ON)

        # Frame cycle control
        self.write_command(0x0B)
        self.write_data(0x0000)  # Frame cycle control

        # Interface control
        self.write_command(0x0C)
        self.write_data(0x0000)

        # GRAM horizontal and vertical address
        self.write_command(0x20)
        self.write_data(0x0000)  # X address
        self.write_command(0x21)
        self.write_data(0x0000)  # Y address

        # Adjust GAMMA
        gamma_settings = [
            (0x50, 0x0400),
            (0x51, 0x060C),
            (0x52, 0x0C06),
            (0x53, 0x0105),
            (0x54, 0x0A0E),
            (0x55, 0x0301),
            (0x56, 0x0700),
            (0x57, 0x0700),
            (0x58, 0x0007),
            (0x59, 0x0007),
        ]
        for cmd, data in gamma_settings:
            self.write_command(cmd)
            self.write_data(data)

        # Set GRAM area
        self.write_command(0x36)
        self.write_data(0x00AF)  # Horizontal GRAM start address
        self.write_command(0x37)
        self.write_data(0x0000)  # Horizontal GRAM end address
        self.write_command(0x38)
        self.write_data(0x00DB)  # Vertical GRAM start address
        self.write_command(0x39)
        self.write_data(0x0000)  # Vertical GRAM end address

        # Start display
        self.write_command(0x07)
        self.write_data(0x1017)

    def write_command(self, command: int):
        self._data_command.value(0)
        self._chip_select.value(0)
        self._spi.write(bytearray([command]))
        self._chip_select.value(1)

    def write_data(self, data: bytearray | int):
        self._data_command.value(1)
        self._chip_select.value(0)
        if isinstance(data, int):
            self._spi.write(bytearray([data]))
        else:
            self._spi.write(data)
        self._chip_select.value(1)

    def set_window(self, x0, y0, x1, y1):
        """Set the window region for drawing."""
        self.write_command(0x36)  # Horizontal address start position
        self.write_data(x0)
        self.write_command(0x37)  # Horizontal address end position
        self.write_data(x1)
        self.write_command(0x38)  # Vertical address start position
        self.write_data(y0)
        self.write_command(0x39)  # Vertical address end position
        self.write_data(y1)
        self.write_command(0x20)  # RAM address set (X)
        self.write_data(x0)
        self.write_command(0x21)  # RAM address set (Y)
        self.write_data(y0)

    def update(self):
        """Write the framebuffer content to the display."""
        self.set_window(0, 0, self._width - 1, self._height - 1)
        self.write_command(0x22)  # RAM write
        self.write_data(self._buffer)  # Write entire framebuffer

    def fill(self, color):
        """Fill the screen with the specified color."""
        self._fb.fill(color)

    def pixel(self, x, y, color):
        """Set a single pixel to the specified color."""
        self._fb.pixel(x, y, color)

    def text(self, string, x, y, color):
        """Draw text at the specified position."""
        self._fb.text(string, x, y, color)

    def _reset_display(self):
        self._reset.value(0)
        sleep(0.05)
        self._reset.value(1)
        sleep(0.05)


COLOR_BLACK = 0x0000  # 0,   0,   0
COLOR_WHITE = 0xFFFF  # 255, 255, 255
COLOR_BLUE = 0x001F  # 0,   0, 255
COLOR_GREEN = 0x07E0  # 0, 255,   0
COLOR_RED = 0xF800  # 255,   0,   0
COLOR_NAVY = 0x000F  # 0,   0, 128
COLOR_DARKBLUE = 0x0011  # 0,   0, 139
COLOR_DARKGREEN = 0x03E0  # 0, 128,   0
COLOR_DARKCYAN = 0x03EF  # 0, 128, 128
COLOR_CYAN = 0x07FF  # 0, 255, 255
COLOR_TURQUOISE = 0x471A  # 64, 224, 208
COLOR_INDIGO = 0x4810  # 75,   0, 130
COLOR_DARKRED = 0x8000  # 128,   0,   0
COLOR_OLIVE = 0x7BE0  # 128, 128,   0
COLOR_GRAY = 0x8410  # 128, 128, 128
COLOR_GREY = 0x8410  # 128, 128, 128
COLOR_SKYBLUE = 0x867D  # 135, 206, 235
COLOR_BLUEVIOLET = 0x895C  # 138,  43, 226
COLOR_LIGHTGREEN = 0x9772  # 144, 238, 144
COLOR_DARKVIOLET = 0x901A  # 148,   0, 211
COLOR_YELLOWGREEN = 0x9E66  # 154, 205,  50
COLOR_BROWN = 0xA145  # 165,  42,  42
COLOR_DARKGRAY = 0x7BEF  # 128, 128, 128
COLOR_DARKGREY = 0x7BEF  # 128, 128, 128
COLOR_SIENNA = 0xA285  # 160,  82,  45
COLOR_LIGHTBLUE = 0xAEDC  # 172, 216, 230
COLOR_GREENYELLOW = 0xAFE5  # 173, 255,  47
COLOR_SILVER = 0xC618  # 192, 192, 192
COLOR_LIGHTGRAY = 0xC618  # 192, 192, 192
COLOR_LIGHTCYAN = 0xE7FF  # 224, 255, 255
COLOR_VIOLET = 0xEC1D  # 238, 130, 238
COLOR_AZUR = 0xF7FF  # 240, 255, 255
COLOR_BEIGE = 0xF7BB  # 245, 245, 220
COLOR_MAGENTA = 0xF81F  # 255,   0, 255
COLOR_TOMATO = 0xFB08  # 255,  99,  71
COLOR_GOLD = 0xFEA0  # 255, 215,   0
COLOR_ORANGE = 0xFD20  # 255, 165,   0
COLOR_SNOW = 0xFFDF  # 255, 250, 250
COLOR_YELLOW = 0xFFE0  # 255, 255,   0

print("Print something to the display")
spi = SPI(0, baudrate=40000000, sck=Pin(2), mosi=Pin(3))
display = ILI9225(spi, 5, 8, 9)
display.fill(COLOR_VIOLET)
display.text("Hello ILI9225!", 10, 10, 0x0000)
display.update()
print("Now I should see it")
# display = Display(spi, dc=Pin(8), cs=Pin(5), rst=Pin(9))

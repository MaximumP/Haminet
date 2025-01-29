from framebuf import FrameBuffer, RGB565
from machine import Pin, SPI
from time import sleep

ILI9225_DRIVER_OUTPUT_CTRL = 0x01  # Driver Output Control
ILI9225_LCD_AC_DRIVING_CTRL = 0x02  # LCD AC Driving Control
ILI9225_ENTRY_MODE = 0x03  # Entry Mode
ILI9225_DISP_CTRL1 = 0x07  # Display Control 1
ILI9225_BLANK_PERIOD_CTRL1 = 0x08  # Blank Period Control
ILI9225_FRAME_CYCLE_CTRL = 0x0B  # Frame Cycle Control
ILI9225_INTERFACE_CTRL = 0x0C  # Interface Control
ILI9225_OSC_CTRL = 0x0F  # Osc Control
ILI9225_POWER_CTRL1 = 0x10  # Power Control 1
ILI9225_POWER_CTRL2 = 0x11  # Power Control 2
ILI9225_POWER_CTRL3 = 0x12  # Power Control 3
ILI9225_POWER_CTRL4 = 0x13  # Power Control 4
ILI9225_POWER_CTRL5 = 0x14  # Power Control 5
ILI9225_VCI_RECYCLING = 0x15  # VCI Recycling
ILI9225_RAM_ADDR_SET1 = 0x20  # Horizontal GRAM Address Set
ILI9225_RAM_ADDR_SET2 = 0x21  # Vertical GRAM Address Set
ILI9225_GRAM_DATA_REG = 0x22  # GRAM Data Register
ILI9225_GATE_SCAN_CTRL = 0x30  # Gate Scan Control Register
ILI9225_VERTICAL_SCROLL_CTRL1 = 0x31  # Vertical Scroll Control 1 Register
ILI9225_VERTICAL_SCROLL_CTRL2 = 0x32  # Vertical Scroll Control 2 Register
ILI9225_VERTICAL_SCROLL_CTRL3 = 0x33  # Vertical Scroll Control 3 Register
ILI9225_PARTIAL_DRIVING_POS1 = 0x34  # Partial Driving Position 1 Register
ILI9225_PARTIAL_DRIVING_POS2 = 0x35  # Partial Driving Position 2 Register
ILI9225_HORIZONTAL_WINDOW_ADDR1 = 0x36  # Horizontal Address Start Position
ILI9225_HORIZONTAL_WINDOW_ADDR2 = 0x37  # Horizontal Address End Position
ILI9225_VERTICAL_WINDOW_ADDR1 = 0x38  # Vertical Address Start Position
ILI9225_VERTICAL_WINDOW_ADDR2 = 0x39  # Vertical Address End Position
ILI9225_GAMMA_CTRL1 = 0x50  # Gamma Control 1
ILI9225_GAMMA_CTRL2 = 0x51  # Gamma Control 2
ILI9225_GAMMA_CTRL3 = 0x52  # Gamma Control 3
ILI9225_GAMMA_CTRL4 = 0x53  # Gamma Control 4
ILI9225_GAMMA_CTRL5 = 0x54  # Gamma Control 5
ILI9225_GAMMA_CTRL6 = 0x55  # Gamma Control 6
ILI9225_GAMMA_CTRL7 = 0x56  # Gamma Control 7
ILI9225_GAMMA_CTRL8 = 0x57  # Gamma Control 8
ILI9225_GAMMA_CTRL9 = 0x58  # Gamma Control 9
ILI9225_GAMMA_CTRL10 = 0x59  # Gamma Control 10

ILI9225C_INVOFF = 0x20
ILI9225C_INVON = 0x21

ILI9225_START_BYTE = 0x005C


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
        self.writeRegister(
            ILI9225_DRIVER_OUTPUT_CTRL, 0x031C
        )  # set the display line number and display direction
        self.writeRegister(ILI9225_LCD_AC_DRIVING_CTRL, 0x0100)  # set 1 line inversion
        self.writeRegister(
            ILI9225_ENTRY_MODE, 0x0010
        )  # set GRAM write direction and BGR=1.
        self.writeRegister(
            ILI9225_BLANK_PERIOD_CTRL1, 0x0808
        )  # set the back porch and front porch

        self.writeRegister(ILI9225_INTERFACE_CTRL, 0x0000)  # CPU interface
        self.writeRegister(ILI9225_OSC_CTRL, 0x0801)  # set Osc  /*0e01*/
        self.writeRegister(ILI9225_RAM_ADDR_SET1, 0x0000)  # RAM Address
        self.writeRegister(ILI9225_RAM_ADDR_SET2, 0x0000)  # RAM Address
        # Power On sequence
        sleep(0.05)
        self.writeRegister(ILI9225_POWER_CTRL1, 0x0A00)  # set SAP,DSTB,STB
        self.writeRegister(ILI9225_POWER_CTRL2, 0x1038)  # set APON,PON,AON,VCI1EN,VC
        sleep(0.05)
        self.writeRegister(ILI9225_POWER_CTRL3, 0x1121)  # set BT,DC1,DC2,DC3
        self.writeRegister(ILI9225_POWER_CTRL4, 0x0066)  # set GVDD
        self.writeRegister(ILI9225_POWER_CTRL5, 0x5F60)  # set VCOMH/VCOML voltage

        # Set GRAM area
        self.writeRegister(ILI9225_GATE_SCAN_CTRL, 0x0000)
        self.writeRegister(ILI9225_VERTICAL_SCROLL_CTRL1, 0x00DB)
        self.writeRegister(ILI9225_VERTICAL_SCROLL_CTRL2, 0x0000)
        self.writeRegister(ILI9225_VERTICAL_SCROLL_CTRL3, 0x0000)
        self.writeRegister(ILI9225_PARTIAL_DRIVING_POS1, 0x00DB)
        self.writeRegister(ILI9225_PARTIAL_DRIVING_POS2, 0x0000)
        self.writeRegister(ILI9225_HORIZONTAL_WINDOW_ADDR1, 0x00AF)
        self.writeRegister(ILI9225_HORIZONTAL_WINDOW_ADDR2, 0x0000)
        self.writeRegister(ILI9225_VERTICAL_WINDOW_ADDR1, 0x00DB)
        self.writeRegister(ILI9225_VERTICAL_WINDOW_ADDR2, 0x0000)

        # Adjust GAMMA curve
        self.writeRegister(ILI9225_GAMMA_CTRL1, 0x4000)
        self.writeRegister(ILI9225_GAMMA_CTRL2, 0x060B)
        self.writeRegister(ILI9225_GAMMA_CTRL3, 0x0C0A)
        self.writeRegister(ILI9225_GAMMA_CTRL4, 0x0105)
        self.writeRegister(ILI9225_GAMMA_CTRL5, 0x0A0C)
        self.writeRegister(ILI9225_GAMMA_CTRL6, 0x0B06)
        self.writeRegister(ILI9225_GAMMA_CTRL7, 0x0004)
        self.writeRegister(ILI9225_GAMMA_CTRL8, 0x0501)
        self.writeRegister(ILI9225_GAMMA_CTRL9, 0x0E00)
        self.writeRegister(ILI9225_GAMMA_CTRL10, 0x000E)

        sleep(0.05)

        self.writeRegister(ILI9225_DISP_CTRL1, 0x1017)

    def writeRegister(self, command, value):
        self._chip_select(0)
        self._data_command(0)
        self._spi.write(command.to_bytes(2, "big"))
        self._data_command(1)
        self._spi.write(value.to_bytes(2, "big"))
        self._chip_select(1)
        # self.write_command(command)
        # self.write_data(value)

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

    def ellipse(
        self, x: int, y: int, xr: int, yr: int, color: int, fill: bool = False
    ) -> None:
        self._fb.ellipse(x, y, xr, yr, color, fill)

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


# def color565(r, g, b):
#    """Return RGB565 color value.
#    Args:
#        r (int): Red value.
#        g (int): Green value.
#        b (int): Blue value.
#    """
#    return (r & 0xF8) << 8 | (b & 0xFC) << 3 | g >> 3
#
#
# print("Print something to the display")
# spi = SPI(0, baudrate=40000000, sck=Pin(2), mosi=Pin(3))
# display = ILI9225(spi, 5, 8, 9)
# display.fill(COLOR_BLACK)
# display.text("Hello ILI9225!", 10, 10, COLOR_RED)
# display.text("Temperatur 31", 10, 20, color565(0, 255, 0))
# display.update()
# display._fb.rect(10, 35, 100, 100, COLOR_BEIGE)
# display.update()
# for i in range(15):
#    display.fill(COLOR_BLACK)
#    display._fb.rect(
#        3 * i, 5 * i, 10, 10, [COLOR_GREEN, COLOR_RED, COLOR_BLUE][i % 3], True
#    )
#    display.update()
# print("Now I should see it")
# display = Display(spi, dc=Pin(8), cs=Pin(5), rst=Pin(9))

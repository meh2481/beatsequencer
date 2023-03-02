"""Module for interfacing with the display"""
import displayio
import board
import busio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text import label

displayio.release_displays()

WIDTH = 128
HEIGHT = 64

class Display:
    def __init__(self, player_name):
        # Init SSD1306 display
        self.i2c_display = busio.I2C(board.GP27, board.GP26, frequency=1000000)  # Up frequency to 1MHz, which is max for i2c
        self.display_bus = displayio.I2CDisplay(self.i2c_display, device_address=0x3c)
        self.display = adafruit_displayio_ssd1306.SSD1306(self.display_bus, width=WIDTH, height=HEIGHT)
        # Make the display context
        self.splash = displayio.Group()
        self.display.show(self.splash)

        # Draw black background
        color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0x0
        self.bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.splash.append(self.bg_sprite)

        # Display welcome text
        text1 = "Hello,"
        self.text_area = label.Label(terminalio.FONT, text=text1, color=0xFFFFFF, x=0, y=4)
        self.splash.append(self.text_area)
        text2 = player_name
        self.text_area2 = label.Label(
            terminalio.FONT, text=text2, scale=2, color=0xFFFFFF, x=0, y=24
        )
        self.splash.append(self.text_area2)

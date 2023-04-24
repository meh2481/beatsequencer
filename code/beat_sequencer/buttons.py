"""Board buttons and neopixel grids."""

import digitalio
import board
from adafruit_debouncer import Debouncer
import time
import neopixel

MIN_BRIGHTNESS = 0.0125
START_BRIGHTNESS = 0.05

NEOPIXEL_TOP_OFF = (0, 255, 0)
NEOPIXEL_TOP_ON = (255, 255, 0)


class Buttons:
    def __init__(self):
        self._callback = None
        # The board's bottom neopixel strand
        neopixel_pin = board.GP9
        neopixel_count = 32
        self.neopixel_brightness = START_BRIGHTNESS
        neopixel_auto_write = False
        self.board_neopixel = neopixel.NeoPixel(neopixel_pin, neopixel_count, brightness=self.neopixel_brightness, auto_write=neopixel_auto_write)
        self.board_neopixel.fill((0, 0, 0))
        self.board_neopixel.show()

        # The board's top neopixel strand
        neopixel_pin2 = board.GP25
        neopixel_count2 = 4
        self.board_neopixel_top = neopixel.NeoPixel(
            neopixel_pin2, neopixel_count2, brightness=self.neopixel_brightness, auto_write=neopixel_auto_write)
        self.board_neopixel_top.fill(NEOPIXEL_TOP_OFF)
        self.board_neopixel_top.show()

        self.OUTPUT_PINS = []
        # Init pins 10-15 as outputs
        for i in range(10, 16):
            pin = digitalio.DigitalInOut(getattr(board, "GP" + str(i)))
            pin.direction = digitalio.Direction.OUTPUT
            pin.value = False
            self.OUTPUT_PINS.append(pin)

        # Init pins 18-19 as outputs
        for i in range(18, 20):
            pin = digitalio.DigitalInOut(getattr(board, "GP" + str(i)))
            pin.direction = digitalio.Direction.OUTPUT
            pin.value = False
            self.OUTPUT_PINS.append(pin)

        self.INPUT_PINS = []
        # Init pins 20-24 as inputs
        for i in range(20, 25):
            pin = digitalio.DigitalInOut(getattr(board, "GP" + str(i)))
            pin.direction = digitalio.Direction.INPUT
            pin.pull = digitalio.Pull.DOWN
            self.INPUT_PINS.append(pin)

        self.BUTTONS = [
            [False, False, False, False, False, False, False, False],
            [False, False, False, False, False, False, False, False],
            [False, False, False, False, False, False, False, False],
            [False, False, False, False, False, False, False, False],
            [False, False, False, False, False, False, False, False],
        ]

        self.DEBOUNCED_BUTTONS = [
            [Debouncer(lambda: self.BUTTONS[0][0]), Debouncer(lambda: self.BUTTONS[0][1]), Debouncer(lambda: self.BUTTONS[0][2]), Debouncer(lambda: self.BUTTONS[0][3]), Debouncer(
                lambda: self.BUTTONS[0][4]), Debouncer(lambda: self.BUTTONS[0][5]), Debouncer(lambda: self.BUTTONS[0][6]), Debouncer(lambda: self.BUTTONS[0][7])],
            [Debouncer(lambda: self.BUTTONS[1][0]), Debouncer(lambda: self.BUTTONS[1][1]), Debouncer(lambda: self.BUTTONS[1][2]), Debouncer(lambda: self.BUTTONS[1][3]), Debouncer(
                lambda: self.BUTTONS[1][4]), Debouncer(lambda: self.BUTTONS[1][5]), Debouncer(lambda: self.BUTTONS[1][6]), Debouncer(lambda: self.BUTTONS[1][7])],
            [Debouncer(lambda: self.BUTTONS[2][0]), Debouncer(lambda: self.BUTTONS[2][1]), Debouncer(lambda: self.BUTTONS[2][2]), Debouncer(lambda: self.BUTTONS[2][3]), Debouncer(
                lambda: self.BUTTONS[2][4]), Debouncer(lambda: self.BUTTONS[2][5]), Debouncer(lambda: self.BUTTONS[2][6]), Debouncer(lambda: self.BUTTONS[2][7])],
            [Debouncer(lambda: self.BUTTONS[3][0]), Debouncer(lambda: self.BUTTONS[3][1]), Debouncer(lambda: self.BUTTONS[3][2]), Debouncer(lambda: self.BUTTONS[3][3]), Debouncer(
                lambda: self.BUTTONS[3][4]), Debouncer(lambda: self.BUTTONS[3][5]), Debouncer(lambda: self.BUTTONS[3][6]), Debouncer(lambda: self.BUTTONS[3][7])],
            [Debouncer(lambda: self.BUTTONS[4][0]), Debouncer(lambda: self.BUTTONS[4][1]), Debouncer(lambda: self.BUTTONS[4][2]), Debouncer(lambda: self.BUTTONS[4][3]), Debouncer(
                lambda: self.BUTTONS[4][4]), Debouncer(lambda: self.BUTTONS[4][5]), Debouncer(lambda: self.BUTTONS[4][6]), Debouncer(lambda: self.BUTTONS[4][7])],
        ]

    def update(self):
        # Cycle through output pins
        for out_idx, output_pin in enumerate(self.OUTPUT_PINS):
            output_pin.value = True
            time.sleep(0.00171)
            # Cycle through input pins
            for in_idx, input_pin in enumerate(self.INPUT_PINS):
                if input_pin.value:
                    self.BUTTONS[in_idx][out_idx] = True
                else:
                    self.BUTTONS[in_idx][out_idx] = False
            output_pin.value = False

        # Update debounced buttons
        for x in self.DEBOUNCED_BUTTONS:
            for y in x:
                y.update()

        # Check for button presses
        for y_idx, y in enumerate(self.DEBOUNCED_BUTTONS):
            for x_idx, x in enumerate(y):
                if x.rose:
                    if self._callback and y_idx < 4:
                        self._callback.button_pressed(x_idx, y_idx)
                elif x.fell:
                    if self._callback and y_idx < 4:
                        self._callback.button_released(x_idx, y_idx)

    def set_neopixel(self, x, y, col):
        # Second row and fourth row are reversed
        if y == 1 or y == 3:
            self.board_neopixel[y*8 + 7 - x] = col
        else:
            self.board_neopixel[y*8 + x] = col

    def set_neopixel_top(self, x, col):
        self.board_neopixel_top[x] = col

    def fill_neopixel(self, col):
        self.board_neopixel.fill(col)

    def show_board_neopixel(self):
        self.board_neopixel.show()

    def show_board_neopixel_top(self):
        self.board_neopixel_top.show()

    def set_brightness(self, brightness):
        self.neopixel_brightness = min(max(brightness, MIN_BRIGHTNESS), 1.0)
        self.board_neopixel.brightness = self.neopixel_brightness
        self.board_neopixel_top.brightness = self.neopixel_brightness
        self.show_board_neopixel()
        self.show_board_neopixel_top()

    def get_brightness(self):
        return self.neopixel_brightness

    def get_button_state(self, x, y):
        return self.DEBOUNCED_BUTTONS[y][x].value

    def get_button_rose(self, x, y):
        return self.DEBOUNCED_BUTTONS[y][x].rose

    def get_button_fell(self, x, y):
        return self.DEBOUNCED_BUTTONS[y][x].fell

    def set_callback(self, callback):
        self._callback = callback

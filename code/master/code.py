from beat_sequencer.startrek import StarTrek
from beat_sequencer.snake import Snake
from beat_sequencer.buttons import Buttons
from beat_sequencer.display import Display
from beat_sequencer.test import Test
from beat_sequencer.beat_sequencer import BeatSequencer
from beat_sequencer.sync_sequencer import SyncSequencer
import mc3416
import time
import audiocore
import audiobusio
import busio
import digitalio
import board
from beat_sequencer.config import PLAYER_NAME, PLAYER_NAMES, NEOPIXEL_TOP_OFF, NEOPIXEL_TOP_ON



OTHER_PLAYER_NAME = PLAYER_NAMES[0] if PLAYER_NAME == PLAYER_NAMES[1] else PLAYER_NAMES[1]


# Constants
MODE_BEAT_SEQUENCER = 0
MODE_SYNC_SEQUENCER = 1
MODE_SFX = 2
MODE_SNAKE = 3
MODE_TEST = 4
MODE_STARTUP = 5
MODES = [MODE_BEAT_SEQUENCER, MODE_SYNC_SEQUENCER, MODE_SFX, MODE_SNAKE, MODE_TEST]
MODE_NAMES = [
    'Beat Sequencer',
    'Sync Sequencer',
    'SFX',
    'Snake',
    'Test'
]
MODE_SUB_NAMES = [
    'Press the buttons to create a song',
    f'Create a song together with {OTHER_PLAYER_NAME}',
    "Press a button to play a sound effect",
    "Tilt the board to move the snake and get the fruit!",
    'Test'
]
cur_mode = MODE_STARTUP
SFX_PATH = '/sfx'
STARTUP_TIME = 0.5

# The board's LED
led_pin = board.GP28

# Turn on the LED while the program is running
led = digitalio.DigitalInOut(led_pin)
led.direction = digitalio.Direction.OUTPUT
led.value = True

display = Display(PLAYER_NAME)

# The board's accelerometer
i2c_accel = busio.I2C(board.GP1, board.GP0, frequency=1000000)
accelerometer = mc3416.MC3416(i2c_accel)

# Init i2s audio
i2s = audiobusio.I2SOut(board.GP7, board.GP8, board.GP6)

# Init uart
uart = busio.UART(board.GP16, board.GP17, baudrate=115200)

# Init buttons
buttons = Buttons()

# Init snake
snake = Snake(buttons, accelerometer, i2s, f'{SFX_PATH}/snake')

# Init startrek
startrek = StarTrek(i2s, f'{SFX_PATH}/startrek', buttons)

# Init test
test = Test(buttons, display, accelerometer)

# Init beat sequencer
beat_sequencer = BeatSequencer(i2s, f'{SFX_PATH}/sequencer', buttons, accelerometer)

# Init sync sequencer
sync_sequencer = SyncSequencer(i2s, f'{SFX_PATH}/sequencer', buttons, uart, accelerometer)

def mode_init(mode):
    global snake, startrek, display, cur_mode, mode_time

    cur_mode = mode
    mode_time = time.monotonic()
    if mode != MODE_STARTUP:
        display.clear()
        display.set_main_text(MODE_NAMES[cur_mode])
        display.set_sub_text(MODE_SUB_NAMES[cur_mode])
    buttons.set_callback(None)
    if mode == MODE_SNAKE:
        snake.init()
    elif mode == MODE_SFX:
        startrek.init()
    elif mode == MODE_TEST:
        test.init()
    elif mode == MODE_BEAT_SEQUENCER:
        beat_sequencer.init()
    elif mode == MODE_SYNC_SEQUENCER:
        sync_sequencer.init()


# Set up our mode
mode_init(cur_mode)
mode_time = time.monotonic()
# Loop forever
while True:
    # Update buttons
    buttons.update()

    if cur_mode == MODE_TEST:
        test.update()
    elif cur_mode == MODE_SNAKE:
        snake.update()
    elif cur_mode == MODE_SFX:
        startrek.update()
    elif cur_mode == MODE_BEAT_SEQUENCER:
        beat_sequencer.update()
    elif cur_mode == MODE_SYNC_SEQUENCER:
        sync_sequencer.update()
    elif cur_mode == MODE_STARTUP:
        if time.monotonic() - mode_time > STARTUP_TIME:
            cur_mode = MODE_SYNC_SEQUENCER
            display.set_main_text(f"Mode: {MODE_NAMES[cur_mode]}")
            # Init mode
            mode_init(cur_mode)

    # Switch modes if top left button is pressed
    if buttons.get_button_rose(5, 4):
        # Init mode
        mode_init((cur_mode + 1) % len(MODES))
        buttons.set_neopixel_top(1, NEOPIXEL_TOP_ON)
        buttons.show_board_neopixel_top()
    elif buttons.get_button_fell(5, 4):
        buttons.set_neopixel_top(1, NEOPIXEL_TOP_OFF)
        buttons.show_board_neopixel_top()

    if buttons.get_button_rose(6, 4):
        # Increase brightness with top right button
        buttons.set_neopixel_top(2, NEOPIXEL_TOP_ON)
        buttons.set_brightness(buttons.get_brightness() * 2)
    elif buttons.get_button_fell(6, 4):
        buttons.set_neopixel_top(2, NEOPIXEL_TOP_OFF)
        buttons.show_board_neopixel_top()
    if buttons.get_button_rose(7, 4):
        # Decrease brightness with bottom right button
        buttons.set_neopixel_top(3, NEOPIXEL_TOP_ON)
        buttons.set_brightness(buttons.get_brightness() / 2)
    elif buttons.get_button_fell(7, 4):
        buttons.set_neopixel_top(3, NEOPIXEL_TOP_OFF)
        buttons.show_board_neopixel_top()

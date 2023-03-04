from beat_sequencer.startrek import StarTrek
from beat_sequencer.snake import Snake
from beat_sequencer.buttons import Buttons
from beat_sequencer.sd_card import SDCard
from beat_sequencer.display import Display
import mc3416
import time
import audiocore
import audiobusio
import busio
import digitalio
import board
PLAYER_NAME = "Maxwell"


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
    'Play a beat',
    'Play a beat with sync',
    "Press a button to play a sound effect",
    "Tilt the board to move the snake and get the fruit!",
    'Test'
]
cur_mode = MODE_STARTUP
SD_PATH = '/sd'
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

# The SD card
SDCard(SD_PATH)

# Init i2s audio
i2s = audiobusio.I2SOut(board.GP7, board.GP8, board.GP6)

# Init uart
uart = busio.UART(board.GP16, board.GP17, baudrate=115200)

# Init buttons
buttons = Buttons()

DISPLAY_UPDATE_INTERVAL = 30
display_update_counter = 0

# Init snake
snake = Snake(buttons, accelerometer)

# Init startrek
startrek = StarTrek(i2s, f'{SD_PATH}/startrek', buttons)


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


# Set up our mode
mode_init(cur_mode)
mode_time = time.monotonic()
# Loop forever
while True:
    # Update buttons
    buttons.update()

    if cur_mode == MODE_TEST:
        # while i2s.playing:

        # Display current accelerometer values
        x_accel, y_accel, z_accel = accelerometer.acceleration
        display_update_counter += 1
        if display_update_counter >= DISPLAY_UPDATE_INTERVAL:
            # X is inverted y, Y is x, for our orientation on the PCB
            # +X right, +Y is up
            display.set_sub_text(f"X: {-y_accel}\nY: {x_accel}\nZ: {z_accel}", False)
            display_update_counter = 0
        time.sleep(0.005)
    elif cur_mode == MODE_SNAKE:
        snake.update()
    elif cur_mode == MODE_SFX:
        startrek.update()
    elif cur_mode == MODE_STARTUP:
        if time.monotonic() - mode_time > STARTUP_TIME:
            cur_mode = MODE_SFX
            display.set_main_text(f"Mode: {MODE_NAMES[cur_mode]}")
            # Init mode
            mode_init(cur_mode)

    # Switch modes if top left button is pressed
    if buttons.get_button_rose(5, 4):
        # Init mode
        mode_init((cur_mode + 1) % len(MODES))

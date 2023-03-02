PLAYER_NAME = "Maxwell"

import board
import digitalio
import busio
import audiobusio
import audiocore
import time
import mc3416
from beat_sequencer import startup
from beat_sequencer.display import Display
from beat_sequencer.sd_card import SDCard
from beat_sequencer.buttons import Buttons
from beat_sequencer.snake import Snake
from beat_sequencer.startrek import StarTrek

# Constants
MODE_BEAT_SEQUENCER = 0
MODE_SYNC_SEQUENCER = 1
MODE_SFX = 2
MODE_SNAKE = 3
MODE_TEST = 0
cur_mode = MODE_SFX
SD_PATH = '/sd'

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

# Load wav file
# wav_file = open(f"{SD_PATH}/PINBALL.wav", "rb")

# Init i2s audio
i2s = audiobusio.I2SOut(board.GP7, board.GP8, board.GP6)

# Init uart
uart = busio.UART(board.GP16, board.GP17, baudrate=115200)

# Init buttons
buttons = Buttons()

# Play wav file
# audio = audiocore.WaveFile(wav_file)
# i2s.play(audio)

DISPLAY_UPDATE_INTERVAL = 30
display_update_counter = 0

startup.startup(display)

# Init snake
snake = Snake(buttons, accelerometer)

# Init startrek
startrek = StarTrek(i2s, f'{SD_PATH}/startrek', buttons)

# Loop forever
while True:
    if cur_mode == MODE_TEST:
        # while i2s.playing:

        # Update buttons
        buttons.update()
        
        # Display current accelerometer values
        x_accel, y_accel, z_accel = accelerometer.acceleration
        display_update_counter += 1
        if display_update_counter >= DISPLAY_UPDATE_INTERVAL:
            # X is inverted y, Y is x, for our orientation on the PCB
            # +X right, +Y is up
            display.text_area2.text = f"X: {-y_accel}\nY: {x_accel}\nZ: {z_accel}"
            display_update_counter = 0
        time.sleep(0.005)
        # i2s.play(audio)
    elif cur_mode == MODE_SNAKE:
        snake.update()
    elif cur_mode == MODE_SFX:
        startrek.update()

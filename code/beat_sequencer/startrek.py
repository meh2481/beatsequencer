import audiocore
import os
import time
import random

# some color definitions
RED = (255, 0, 0)  # 0xFF0000
MAROON = (128, 0, 0)  # 0x800000
ORANGE = (255, 128, 0)  # 0xFF8000
YELLOW = (255, 255, 0)  # 0xFFFF00
OLIVE = (128, 128, 0)  # 0x808000
GREEN = (0, 128, 0)  # 0x008000
AQUA = (0, 255, 255)  # 0x00FFFF
TEAL = (0, 128, 128)  # 0x008080
BLUE = (0, 0, 255)  # 0x0000FF
NAVY = (0, 0, 128)  # 0x000080
PURPLE = (128, 0, 128)  # 0x800080
PINK = (255, 0, 128)  # 0xFF0080

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
OFF = BLACK

COLORS = [
    RED,
    MAROON,
    ORANGE,
    YELLOW,
    OLIVE,
    GREEN,
    AQUA,
    TEAL,
    BLUE,
    NAVY,
    PURPLE,
    PINK
]

class StarTrek():
    def __init__(self, i2s, sd_path, buttons):
        self.i2s = i2s
        self.sd_path = sd_path
        self.buttons = buttons
        self.audio = None
        self.audio_files = [ f'{sd_path}/{file}'
            for file in os.listdir(self.sd_path)
            if file.endswith('.wav')
        ]
        # Only pick the first 32 files
        self.audio_files = self.audio_files[:32]
        self.cur_file = 0
        buttons._callback = self
        # Initialize each LED to a random color
        self.pixel_colors = [[random.choice(COLORS) for _ in range(8)] for _ in range(4)]
        for x in range(8):
            for y in range(4):
                self.buttons.set_neopixel(x, y, self.pixel_colors[y][x])
        self.buttons.show_board_neopixel()
        # self.effect_origin = (0, 0)
        # self.effect_start_time = 0
        # self.effect_iter = 0
    
    def play_sound(self, path):
        if self.i2s.playing:
            self.i2s.stop()
        self.wav_file = open(path, "rb")
        self.audio = audiocore.WaveFile(self.wav_file)
        self.i2s.play(self.audio, loop=False)

    def update(self):
        self.buttons.update()
        time.sleep(0.005)
    
    def button_pressed(self, x, y):
        self.cur_file = y * 8 + x
        if self.cur_file >= len(self.audio_files):
            self.cur_file = 0
        self.play_sound(self.audio_files[self.cur_file])
        # Set this location to a new random color
        xcoord = self.cur_file % 8
        ycoord = self.cur_file // 8
        colors_copy = COLORS.copy()
        colors_copy.remove(self.pixel_colors[ycoord][xcoord])
        random_color = random.choice(colors_copy)
        self.pixel_colors[ycoord][xcoord] = random_color
        self.buttons.set_neopixel(xcoord, ycoord, random_color)
        self.buttons.show_board_neopixel()
    
    def button_released(self, x, y):
        pass

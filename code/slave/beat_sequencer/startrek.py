import audiocore
import os
import time
import random

from .config import STARTREK_COLORS

EFFECT_DELAY = 0.11
EFFECT_SPEEDUP = 0.85

class StarTrek():
    def __init__(self, i2s, sd_path, buttons):
        self.i2s = i2s
        self.sd_path = sd_path
        self.buttons = buttons
        self.audio = None
        self.audio_files = [
            f'{sd_path}/{file}'
            for file in os.listdir(self.sd_path)
            if file.endswith('.wav')
        ]
        # Only pick the first 32 files
        self.audio_files = self.audio_files[:32]
        # Initialize each LED to a random color
        self.pixel_colors = [
            [random.choice(STARTREK_COLORS) for _ in range(8)]
            for _ in range(4)
        ]
        self.effect_origin = (0, 0)
        self.effect_start_time = 0
        self.cur_effect_delay = EFFECT_DELAY
        self.effect_iter = 0

    def init(self):
        self.buttons.set_callback(self)
        for x in range(8):
            for y in range(4):
                self.buttons.set_neopixel(x, y, self.pixel_colors[y][x])
        self.buttons.show_board_neopixel()
        self.effect_origin = (0, 0)
        self.effect_start_time = 0
        self.cur_effect_delay = EFFECT_DELAY
        self.effect_iter = 0

    def play_sound(self, path):
        if self.i2s.playing:
            self.i2s.stop()
        self.wav_file = open(path, "rb")
        self.audio = audiocore.WaveFile(self.wav_file)
        self.i2s.play(self.audio, loop=False)

    def update(self):
        time.sleep(0.005)
        if self.effect_start_time == 0:
            return
        if time.monotonic() - self.effect_start_time > self.cur_effect_delay:
            self.effect_start_time = time.monotonic()
            # Set current ring to white
            for x in range(8):
                for y in range(4):
                    if (abs(x - self.effect_origin[0]) == self.effect_iter and abs(y - self.effect_origin[1]) <= self.effect_iter) or \
                          (abs(y - self.effect_origin[1]) == self.effect_iter and abs(x - self.effect_origin[0]) <= self.effect_iter):
                        self.buttons.set_neopixel(x, y, (255, 255, 255))
                    else:
                        self.buttons.set_neopixel(x, y, self.pixel_colors[y][x])
            if self.effect_iter == 8:
                self.effect_start_time = 0
                self.cur_effect_delay = EFFECT_DELAY
            # Speed up effect delay as it progresses
            self.cur_effect_delay *= EFFECT_SPEEDUP
            # Update board pixels
            self.buttons.show_board_neopixel()
            self.effect_iter += 1


    def button_pressed(self, x, y):
        cur_file = y * 8 + x
        if cur_file >= len(self.audio_files) or cur_file < 0:
            return
        self.play_sound(self.audio_files[cur_file])
        # Set this location to a new random color
        xcoord = cur_file % 8
        ycoord = cur_file // 8
        colors_copy = STARTREK_COLORS.copy()
        colors_copy.remove(self.pixel_colors[ycoord][xcoord])
        random_color = random.choice(colors_copy)
        self.pixel_colors[ycoord][xcoord] = random_color
        self.buttons.set_neopixel(xcoord, ycoord, random_color)
        # If there is an effect in progress, stop it
        if self.effect_start_time != 0:
            for x in range(8):
                for y in range(4):
                    self.buttons.set_neopixel(x, y, self.pixel_colors[y][x])
        self.buttons.show_board_neopixel()
        self.effect_origin = (xcoord, ycoord)
        self.effect_start_time = time.monotonic()
        self.cur_effect_delay = EFFECT_DELAY
        self.effect_iter = 1

    def button_released(self, x, y):
        pass

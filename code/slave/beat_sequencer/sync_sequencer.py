import os
import audiocore
import time
import audiomixer
import math

from .config import PATCH_COLORS, NEOPIXEL_TOP_OFF, NEOPIXEL_TOP_ON


NUM_PATCHES = 4
# START_TEMPO = 160
# MIN_TEMPO = 80
# MAX_TEMPO = 560

class SyncSequencer():
    def __init__(self, i2s, path, buttons, uart):
        self.i2s = i2s
        self.buttons = buttons
        self.uart = uart
        self.audio_files = [
            [
                f'{path}/{patch_dir}/{file}'
                for file in os.listdir(f'{path}/{patch_dir}')
            ]
            for patch_dir in os.listdir(path)
        ]
        self.samples = [
            [audiocore.WaveFile(file) for file in patch]
            for patch in self.audio_files
        ]
        # self.tempo = START_TEMPO
        self.mixer = audiomixer.Mixer(
            voice_count=4,
            sample_rate=22050,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True
        )
        self.patches = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.cur_volume = 1.0

    def init(self):
        self.buttons.set_callback(self)
        self.last_time = time.monotonic()
        self.step = -1  # Start before the first step
        if self.i2s.playing:
            self.i2s.stop()
        self.i2s.play(self.mixer, loop=False)
        # Set button colors
        self.buttons.fill_neopixel((0, 0, 0))
        for x in range(8):
            for y in range(4):
                if self.patches[y][x] != 0:
                    self.buttons.set_neopixel(x, y, PATCH_COLORS[self.patches[y][x] - 1])
        self.buttons.show_board_neopixel()

    def update(self):
        self.read_uart()
        # print("step: ", self.step)
        # cur_time = time.monotonic()
        # if cur_time - self.last_time > 60 / self.tempo:
        #     self.last_time = cur_time
        #     self.step += 1
        #     self.step %= 8
        # Pressing bottom left action button resets the board
        if self.buttons.get_button_rose(4, 4):
            self.patches = [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]
            self.init()
            self.buttons.set_neopixel_top(0, NEOPIXEL_TOP_ON)
            self.buttons.show_board_neopixel_top()
        elif self.buttons.get_button_fell(4, 4):
            self.buttons.set_neopixel_top(0, NEOPIXEL_TOP_OFF)
            self.buttons.show_board_neopixel_top()
        time.sleep(0.005)

    def button_pressed(self, x, y):
        self.patches[y][x] = (self.patches[y][x] + 1) % (NUM_PATCHES + 1)
        if self.patches[y][x] != 0:
            self.buttons.set_neopixel(x, y, PATCH_COLORS[self.patches[y][x] - 1])
            self.play_sound(self.samples[y][self.patches[y][x] - 1], y)
        else:
            self.buttons.set_neopixel(x, y, (0, 0, 0))
        self.buttons.show_board_neopixel()

    def button_released(self, x, y):
        pass

    def play_sound(self, sample, voice):
        self.mixer.play(sample, voice=voice)

    # def write_uart(self, data):
    #     self.uart.write(bytearray(f"{data}\r\n", "utf-8"))

    # def step_uart(self):
    #     self.write_uart(f'STEP {self.step}')

    def read_uart(self):
        data = self.uart.readline()
        if data is not None:
            # convert bytearray to string
            data_string = ''.join([chr(b) for b in data])
            print(data_string)
            command_list = data_string.split()
            if len(command_list) > 0:
                command = command_list[0]
                # if command == 'TEMPO':
                #     self.tempo = float(command_list[1])
                if command == 'STEP':
                    self.step = int(command_list[1])
                    self.step_func()

    def step_func(self):
        for y in range(4):
            if self.patches[y][self.step] != 0:
                self.play_sound(self.samples[y][self.patches[y][self.step] - 1], y)
        # Illuminate next column
        for y in range(4):
            self.buttons.set_neopixel(self.step, y, (255, 255, 255))
        # Turn off previous column
        prev_step = (self.step - 1) % 8
        for y in range(4):
            if self.patches[y][prev_step] != 0:
                self.buttons.set_neopixel(prev_step, y, PATCH_COLORS[self.patches[y][prev_step] - 1])
            else:
                self.buttons.set_neopixel(prev_step, y, (0, 0, 0))
        self.buttons.show_board_neopixel()

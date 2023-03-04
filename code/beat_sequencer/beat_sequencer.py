import os
import audiocore
import time
import audiomixer

PATCH_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0)
]
NUM_PATCHES = 4
START_TEMPO = 160
MIN_TEMPO = 60
MAX_TEMPO = 240


class BeatSequencer():
    def __init__(self, i2s, path, buttons):
        self.i2s = i2s
        self.buttons = buttons
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
        self.tempo = START_TEMPO
        self.mixer = audiomixer.Mixer(
            voice_count=4,
            sample_rate=22050,
            channel_count=2,
            bits_per_sample=16,
            samples_signed=True
        )

    def update(self):
        cur_time = time.monotonic()
        if cur_time - self.last_time > 60 / self.tempo:
            self.last_time = cur_time
            self.step += 1
            self.step %= 8
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

    def init(self):
        self.buttons.fill_neopixel((0, 0, 0))
        self.buttons.show_board_neopixel()
        self.patches = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.buttons.set_callback(self)
        self.last_time = time.monotonic()
        self.step = 0
        if self.i2s.playing:
            self.i2s.stop()
        self.i2s.play(self.mixer, loop=False)

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

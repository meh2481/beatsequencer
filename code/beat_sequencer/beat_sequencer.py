import os

PATCH_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0)
]
NUM_PATCHES = 4

class BeatSequencer():
    def __init__(self, i2s, sd_path, buttons):
        self.i2s = i2s
        self.sd_path = sd_path
        self.buttons = buttons
        self.audio_files = [ [f'{self.sd_path}/{patch_dir}/{file}'
            for file in os.listdir(f'{self.sd_path}/{patch_dir}')]
            for patch_dir in os.listdir(self.sd_path)
        ]

    def update(self):
        pass

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

    def button_pressed(self, x, y):
        if self.patches[y][x] == 0:
            self.patches[y][x] = 1
            self.buttons.set_neopixel(x, y, (0, 255, 0))
        else:
            self.patches[y][x] = 0
            self.buttons.set_neopixel(x, y, (0, 0, 0))
        self.buttons.show_board_neopixel()

    def button_released(self, x, y):
        pass

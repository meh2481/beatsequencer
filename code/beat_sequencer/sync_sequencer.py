
class SyncSequencer():
    def __init__(self, i2s, sd_path, buttons, uart):
        self.i2s = i2s
        self.sd_path = sd_path
        self.buttons = buttons
        self.uart = uart

    def update(self):
        pass

    def init(self):
        self.buttons.fill_neopixel((0, 0, 0))
        self.buttons.show_board_neopixel()

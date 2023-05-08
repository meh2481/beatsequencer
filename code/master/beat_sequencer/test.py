import time

DISPLAY_UPDATE_INTERVAL = 30

class Test:
    def __init__(self, buttons, display, accelerometer):
        self.buttons = buttons
        self.display = display
        self.accelerometer = accelerometer
        self.display_update_counter = 0

    def init(self):
        self.buttons.fill_neopixel((0, 0, 255))
        self.buttons.show_board_neopixel()
        self.buttons.set_callback(self)

    def button_pressed(self, x, y):
        self.buttons.set_neopixel(x, y, (255, 0, 0))
        self.buttons.show_board_neopixel()

    def button_released(self, x, y):
        self.buttons.set_neopixel(x, y, (0, 0, 255))
        self.buttons.show_board_neopixel()

    def update(self):
        # Display current accelerometer values
        x_accel, y_accel, z_accel = self.accelerometer.acceleration
        self.display_update_counter += 1
        if self.display_update_counter >= DISPLAY_UPDATE_INTERVAL:
            # X is inverted y, Y is x, for our orientation on the PCB
            # +X right, +Y is up
            self.display.set_sub_text(f"X: {-y_accel}\nY: {x_accel}\nZ: {z_accel}", False)
            self.display_update_counter = 0
        time.sleep(0.005)

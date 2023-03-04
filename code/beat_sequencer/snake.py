"""Snake game mostly coded by CoPilot"""
import random
import math
import time

MIN_MOVE_ACCEL = 0.2
SLEEP_TIME = 0.05
DEFAULT_MOVE_TIME = 0.5
SNAKE_HEAD_COLOR = (0, 255, 100)
SNAKE_BODY_COLOR = (0, 255, 0)
FRUIT_COLOR = (255, 0, 0)

class Snake():
    def __init__(self, buttons, accelerometer):
        self._buttons = buttons
        self._accelerometer = accelerometer

    def init(self):
        self.board = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.snake = [(0,0)]
        self.fruit = self.gen_random_fruit()
        self._update_board_colors()
        # Start moving right
        self.last_direction = -math.pi / 2
        self.next_move_time = time.monotonic() + DEFAULT_MOVE_TIME

    def gen_random_fruit(self):
        while True:
            x = random.randint(0, 7)
            y = random.randint(0, 3)
            if self.board[y][x] == 0 and (x, y) not in self.snake:
                self.board[y][x] = 2
                return (x, y)

    def update(self):
        # Wait until it's time to move
        cur_time = time.monotonic()
        if cur_time < self.next_move_time:
            return

        # Update accelerometer
        x_accel, y_accel, _ = self._accelerometer.acceleration

        # Compute x,y vector from accelerometer
        vector_angle = math.atan2(y_accel, x_accel)
        vector_length = math.sqrt(x_accel**2 + y_accel**2)
        # If board is flat/no input, move in last direction
        if vector_length < MIN_MOVE_ACCEL:
            vector_angle = self.last_direction

        # If vector is mostly right, move right
        if vector_angle > math.pi / 4 and vector_angle < 3 * math.pi / 4:
            self.snake.insert(0, (self.snake[0][0] - 1, self.snake[0][1]))
        # If vector is mostly up, move up
        elif vector_angle < -math.pi / 4 and vector_angle > -3 * math.pi / 4:
            self.snake.insert(0, (self.snake[0][0] + 1, self.snake[0][1]))
        # If vector is mostly left, move left
        elif vector_angle < -3 * math.pi / 4 or vector_angle > 3 * math.pi / 4:
            self.snake.insert(0, (self.snake[0][0], self.snake[0][1] + 1))
        # If vector is mostly down, move down
        else:
            self.snake.insert(0, (self.snake[0][0], self.snake[0][1] - 1))

        # Store last direction
        self.last_direction = vector_angle

        # Check for fruit
        if self.snake[0] == self.fruit:
            self.fruit = self.gen_random_fruit()
        else:
            self.snake.pop()

        # Check for win condition
        if len(self.snake) == 32:
            # TODO: Win
            self.game_over()

        # Check for collision
        if self.snake[0][0] > 7 or self.snake[0][1] > 3 or self.snake[0][0] < 0 or self.snake[0][1] < 0:
            self.game_over()

        # Check for self collision
        if self.snake[0] in self.snake[1:]:
            self.game_over()

        # Set the board colors
        self._update_board_colors()

        # Moves happen faster as the game progresses
        self.next_move_time = cur_time + DEFAULT_MOVE_TIME -  len(self.snake) * 0.01

    def game_over(self):
        self.snake = [(0,0)]
        self.board = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.fruit = self.gen_random_fruit()
        self.board[self.fruit[1]][self.fruit[0]] = 2
        # Start moving right
        self.last_direction = -math.pi / 2

    def _update_board_colors(self):
        self.board = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        for x, y in self.snake:
            self.board[y][x] = 1
        self.board[self.fruit[1]][self.fruit[0]] = 2
        for y in range(4):
            for x in range(8):
                if self.board[y][x] == 0:
                    self._buttons.set_neopixel(x, y, (0, 0, 0))
                elif self.board[y][x] == 1:
                    self._buttons.set_neopixel(x, y, SNAKE_BODY_COLOR)
                elif self.board[y][x] == 2:
                    self._buttons.set_neopixel(x, y, FRUIT_COLOR)
        # Set snake head a bluish green
        self._buttons.set_neopixel(self.snake[0][0], self.snake[0][1], SNAKE_HEAD_COLOR)
        self._buttons.show_board_neopixel()

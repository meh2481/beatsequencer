# SPDX-FileCopyrightText: 2022 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import random
import time
import board
import audiocore
import audiobusio
import sdcardio
import storage
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

# Create the I2C object for the NeoTrellis
i2c_bus = board.I2C()

# This is for a 2x2 array of NeoTrellis boards:
trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2F, auto_write=False),
     NeoTrellis(i2c_bus, False, addr=0x2E, auto_write=False)],
    [NeoTrellis(i2c_bus, False, addr=0x31, auto_write=False),
     NeoTrellis(i2c_bus, False, addr=0x30, auto_write=False)],
]

trellis = MultiTrellis(trelli)

# Set the brightness value (0 to 1.0)
trellis.brightness = .15

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

COLORS = [RED, MAROON, ORANGE, YELLOW, OLIVE,
          GREEN, AQUA, TEAL, BLUE, NAVY, PURPLE, PINK]

# Initialize each LED to a random color
pixel_colors = [[random.choice(COLORS) for _ in range(8)] for _ in range(8)]

effect_origin = (0, 0)
effect_start_time = 0
effect_iter = 0

# Setup SD card
spi_bus = board.SPI()
cs = board.D4
sdcard = sdcardio.SDCard(spi_bus, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Setup I2S audio out
audio = audiobusio.I2SOut(bit_clock=board.D24, word_select=board.D25, data=board.A3)

SOUNDS = [
    "/sd/startrek/DS9_BAJPHASR.wav",
    "/sd/startrek/alert10.wav",
    "/sd/startrek/padd_2.wav",
    "/sd/startrek/alert24.wav",
    "/sd/startrek/probe_launch_2.wav",
    "/sd/startrek/alertklaxon_clean.wav",
    "/sd/startrek/quantumtorpedoes.wav",
    "/sd/startrek/ambient_bridge_21.wav",
    "/sd/startrek/romulan_computerbeep2.wav",
    "/sd/startrek/borg_adapt3.wav",
    "/sd/startrek/romulan_disruptor1.wav",
    "/sd/startrek/borg_computer_beep.wav",
    "/sd/startrek/romulan_torpedo.wav",
    "/sd/startrek/borg_cut_2.wav",
    "/sd/startrek/smallexplosion1.wav",
    "/sd/startrek/borg_phaser_clean.wav",
    "/sd/startrek/tmp_warp_clean.wav",
    "/sd/startrek/borg_tractor_beam.wav",
    "/sd/startrek/tng_disruptor_clean.wav",
    "/sd/startrek/cloak_klingon.wav",
    "/sd/startrek/tng_nemesis_intruder_alert.wav",
    "/sd/startrek/computerbeep_41.wav",
    "/sd/startrek/tng_phaser11_clean.wav",
    "/sd/startrek/computerbeep_71.wav",
    "/sd/startrek/tng_phaser3_clean.wav",
    "/sd/startrek/computerbeep_74.wav",
    "/sd/startrek/tng_phaser4_clean_top.wav",
    "/sd/startrek/computerbeepsequence5.wav",
    "/sd/startrek/tng_phaser_rifle.wav",
    "/sd/startrek/console_explo_01.wav",
    "/sd/startrek/tng_slowwarp_clean2.wav",
    "/sd/startrek/cortical_stimulator.wav",
    "/sd/startrek/tng_torpedo_clean.wav",
    "/sd/startrek/denybeep4.wav",
    "/sd/startrek/tng_transporter1.wav",
    "/sd/startrek/ds9_door.wav",
    "/sd/startrek/tng_warp3_clean.wav",
    "/sd/startrek/ds9_phaser_blast_1.wav",
    "/sd/startrek/tng_weapons_clean.wav",
    "/sd/startrek/ds9_tricorder_1.wav",
    "/sd/startrek/tos_bosun_whistle_1.wav",
    "/sd/startrek/energize.wav",
    "/sd/startrek/tos_chirp_1.wav",
    "/sd/startrek/ent_screen5.wav",
    "/sd/startrek/tos_com_beep_1.wav",
    "/sd/startrek/forcefield_disable.wav",
    "/sd/startrek/tos_disruptor.wav",
    "/sd/startrek/forcefield_powering_down.wav",
    "/sd/startrek/tos_phaser_10.wav",
    "/sd/startrek/holoemitter_emh.wav",
    "/sd/startrek/tos_photon_torpedo.wav",
    "/sd/startrek/input_ok_1_clean.wav",
    "/sd/startrek/tos_red_alert.wav",
    "/sd/startrek/klingon_alert.wav",
    "/sd/startrek/tos_swoosh_1_long.wav",
    "/sd/startrek/klingon_computer_beep_1.wav",
    "/sd/startrek/tos_transporterbeep.wav",
    "/sd/startrek/klingon_disruptor_clean.wav",
    "/sd/startrek/tos_turbolift.wav",
    "/sd/startrek/klingon_torpedo_clean.wav",
    "/sd/startrek/voy_hand_phaser.wav",
    "/sd/startrek/klingon_weapon_2.wav",
    "/sd/startrek/voy_torpedo.wav",
    "/sd/startrek/largeexplosion1.wav"
]

wav_file_obj = open('/sd/mtte.wav', 'rb')
wav_file = audiocore.WaveFile(wav_file_obj)
started_playing_music = 0
iter = 0
starfield_delay = 0
sync_iter = 0
kick_timing = 0
red_pos = 0
white_pos = 0
starfield_kick_timing = 0

frame_updated = False
# This will be called when button events are received
def blink(xcoord, ycoord, edge):
    global effect_start_time
    global effect_origin
    global effect_iter
    global audio
    global wav_file_obj
    global frame_updated
    global started_playing_music
    global iter
    global starfield_delay
    global sync_iter
    global kick_timing
    global red_pos
    global white_pos
    global starfield_kick_timing
    # Turn the LED to a different color when a rising edge is detected
    if edge == NeoTrellis.EDGE_RISING:
        started_playing_music = time.monotonic()
        iter = 0
        starfield_delay = 0
        sync_iter = 0
        kick_timing = 0
        red_pos = 0
        white_pos = 0
        starfield_kick_timing = 0
        audio.play(wav_file)
        trellis.fill(BLUE)
        trellis.show()
        # colors_copy = COLORS.copy()
        # colors_copy.remove(pixel_colors[xcoord][ycoord])
        # random_color = random.choice(colors_copy)
        # trellis.color(xcoord, ycoord, random_color)
        # frame_updated = True
        # pixel_colors[xcoord][ycoord] = random_color
        # if effect_start_time == 0:
        #     effect_start_time = time.monotonic()
        #     effect_origin = (xcoord, ycoord)
        #     effect_iter = 0
        # if audio.playing:
        #     audio.stop()
        # if wav_file_obj is not None:
        #     wav_file_obj.close()
        # sound_to_play = SOUNDS[xcoord + ycoord * 8]
    #     print("Playing sound " + sound_to_play + "...")
    #     wav_file_obj = open(sound_to_play, "rb")
    #     wav_file = audiocore.WaveFile(wav_file_obj)
    #     audio.play(wav_file)
    # # Turn the LED off when a falling edge is detected
    elif edge == NeoTrellis.EDGE_FALLING:
        trellis.fill(BLACK)
        trellis.show()


for y in range(8):
    for x in range(8):
        # Activate rising edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
        # # Activate falling edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
        trellis.set_callback(x, y, blink)
        # trellis.color(x, y, pixel_colors[x][y])
        trellis.color(x, y, BLACK)
trellis.show()

print("ready")
STAR_TEAL = (0, 255, 75)
OFF_WHITE = (255, 255, 128)
STARFIELD_TIMINGS = [
    (19.08, 19.81, OFF_WHITE),
    (20.1, 21.011, RED),
    (21.311, 22.21, STAR_TEAL),
    (24.01, 24.61, STAR_TEAL),
    (24.91, 25.81, RED),
    (26.11, 27.01, OFF_WHITE),
    (28.81, 29.41, OFF_WHITE),
    (29.71, 30.61, RED),
    (30.91, 31.81, STAR_TEAL),
    (33.61, 34.21, STAR_TEAL),
    (34.51, 35.41, RED),
    (35.71, 36.61, OFF_WHITE),
    (96.04, 96.64, OFF_WHITE),
    (96.94, 97.84, RED),
    (98.14, 99.04, STAR_TEAL),
    (100.84, 101.44, STAR_TEAL),
    (101.74, 102.64, RED),
    (102.94, 103.84, OFF_WHITE),
    (105.64, 106.24, OFF_WHITE),
    (106.54, 107.44, RED),
    (107.74, 108.64, STAR_TEAL),
    (110.44, 111.04, STAR_TEAL),
    (111.34, 112.24, RED),
    (112.54, 113.44, OFF_WHITE),
    (115.24, 115.84, OFF_WHITE),
    (116.14, 117.04, RED),
    (117.34, 118.24, STAR_TEAL),
    (120.04, 120.64, STAR_TEAL),
    (120.94, 121.84, RED),
    (122.14, 123.04, OFF_WHITE),
    (124.84, 125.44, OFF_WHITE),
    (125.74, 126.64, RED),
    (126.94, 127.84, STAR_TEAL),
    (129.64, 130.24, STAR_TEAL),
    (130.54, 131.44, RED),
    (131.74, 132.64, OFF_WHITE),
]

STARFIELD_KICK_TIMINGS = [
    (19.81, 20.1),
    (21.011, 21.311),
    (22.21, 24.01),
    (24.61, 24.91),
    (25.81, 26.11),
    (27.01, 28.81),
    (29.41, 29.71),
    (30.61, 30.91),
    (31.81, 33.61),
    (34.21, 34.51),
    (35.41, 35.71),
]

KICK_TIMINGS = [
    (0.0, 0.596, 0),
    (0.596, 1.196, 4),
    (1.196, 1.796, 8),
    (1.796, 2.396, 12),
    (2.396, 2.996, 16),
    (2.996, 3.596, 20),
    (3.596, 4.196, 24),
    (4.196, 4.796, 28),
    (4.796, 5.396, 32),
    (5.396, 5.996, 36),
    (5.996, 6.596, 40),
    (6.596, 7.196, 44),
    (7.196, 7.796, 48),
    (7.796, 8.396, 52),
    (8.396, 8.996, 56),
    (8.996, 9.596, 60),
    (9.596, 10.196, 64),
    (10.196, 10.796, 68),
    (10.796, 11.396, 72),
    (11.396, 11.996, 76),
    (11.996, 12.596, 80),
    (12.596, 13.196, 84),
    (13.196, 13.796, 88),
    (13.796, 14.396, 92),
    (14.396, 14.996, 96),
    (14.996, 15.596, 100),
    (15.596, 16.196, 104),
    (16.196, 16.796, 108),
    (16.796, 17.096, 112),
    (17.096, 17.397, 116),
    (17.397, 17.697, 120),
    (17.697, 17.997, 124),
]

RED_SPINWHEEL_TIMINGS = [
    (17.997, 18.597)
]

WHITE_WIPE_TIMINGS = [
    (18.597, 19.08)
]

ITER_FAST_ANIM = 20
ITER_FAST_SFX = 0
while True:
    if iter > ITER_FAST_ANIM:
        iter = 0
        trellis.sync()
    iter += 1
    cur_time = time.monotonic() - started_playing_music
    has_timing = False
    for timing in STARFIELD_TIMINGS:
        if timing[0] < cur_time < timing[1]:
            has_timing = True
            for x in range(8):
                for y in range(8):
                    trellis.color(x, y, timing[2] if (x+y) % 2 == sync_iter else BLACK)
            if starfield_delay > 0:
                starfield_delay = 0
                sync_iter = 1 - sync_iter
            starfield_delay += 1
    for timing in KICK_TIMINGS:
        if timing[0] < cur_time < timing[1]:
            has_timing = True
            if kick_timing == timing[2]:
                kick_timing = timing[2] + 1
                trellis.fill(BLACK)
                trellis.color(3, 3, STAR_TEAL)
                trellis.color(4, 3, STAR_TEAL)
                trellis.color(3, 4, STAR_TEAL)
                trellis.color(4, 4, STAR_TEAL)
            elif kick_timing == timing[2] + 1:
                kick_timing = timing[2] + 2
                trellis.fill(BLACK)
                trellis.color(3, 2, STAR_TEAL)
                trellis.color(4, 2, STAR_TEAL)
                trellis.color(3, 5, STAR_TEAL)
                trellis.color(4, 5, STAR_TEAL)
                trellis.color(2, 3, STAR_TEAL)
                trellis.color(5, 3, STAR_TEAL)
                trellis.color(2, 4, STAR_TEAL)
                trellis.color(5, 4, STAR_TEAL)
            elif kick_timing == timing[2] + 2:
                kick_timing = timing[2] + 3
                trellis.fill(BLACK)
                trellis.color(3, 1, STAR_TEAL)
                trellis.color(4, 1, STAR_TEAL)
                trellis.color(3, 6, STAR_TEAL)
                trellis.color(4, 6, STAR_TEAL)
                trellis.color(1, 3, STAR_TEAL)
                trellis.color(6, 3, STAR_TEAL)
                trellis.color(1, 4, STAR_TEAL)
                trellis.color(6, 4, STAR_TEAL)
            elif kick_timing == timing[2] + 3:
                kick_timing = timing[2] + 4
                trellis.fill(BLACK)
                trellis.color(3, 0, STAR_TEAL)
                trellis.color(4, 0, STAR_TEAL)
                trellis.color(3, 7, STAR_TEAL)
                trellis.color(4, 7, STAR_TEAL)
                trellis.color(0, 3, STAR_TEAL)
                trellis.color(7, 3, STAR_TEAL)
                trellis.color(0, 4, STAR_TEAL)
                trellis.color(7, 4, STAR_TEAL)
            else:
                trellis.fill(BLACK)
    for timing in RED_SPINWHEEL_TIMINGS:
        if timing[0] < cur_time < timing[1]:
            has_timing = True
            trellis.fill(BLACK)
            trellis.color(8 - red_pos - 1, 0, RED)
            trellis.color(0, red_pos, RED)
            trellis.color(red_pos, 7, RED)
            trellis.color(7, 8 - red_pos - 1, RED)
            red_pos = (red_pos + 1) % 8
    for timing in WHITE_WIPE_TIMINGS:
        if timing[0] < cur_time < timing[1]:
            has_timing = True
            if white_pos == 0:
                trellis.fill(BLACK)
                for x in range(8):
                    trellis.color(x, 0, OFF_WHITE)
                    trellis.color(x, 7, OFF_WHITE)
            elif white_pos == 1:
                for x in range(8):
                    trellis.color(x, 1, OFF_WHITE)
                    trellis.color(x, 6, OFF_WHITE)
            elif white_pos == 2:
                for x in range(8):
                    trellis.color(x, 2, OFF_WHITE)
                    trellis.color(x, 5, OFF_WHITE)
            elif white_pos == 3:
                for x in range(8):
                    trellis.color(x, 3, OFF_WHITE)
                    trellis.color(x, 4, OFF_WHITE)
            elif white_pos == 4:
                for x in range(8):
                    trellis.color(x, 0, BLACK)
                    trellis.color(x, 7, BLACK)
            elif white_pos == 5:
                for x in range(8):
                    trellis.color(x, 1, BLACK)
                    trellis.color(x, 6, BLACK)
            elif white_pos == 6:
                for x in range(8):
                    trellis.color(x, 2, BLACK)
                    trellis.color(x, 5, BLACK)
            elif white_pos == 7:
                for x in range(8):
                    trellis.color(x, 3, BLACK)
                    trellis.color(x, 4, BLACK)
            white_pos = white_pos + 1
    for timing in STARFIELD_KICK_TIMINGS:
        if timing[0] < cur_time < timing[1]:
            has_timing = True
            if starfield_kick_timing == 0 and cur_time < timing[0] + 0.4:
                trellis.fill(BLACK)
                starfield_kick_timing = 1
            elif starfield_kick_timing == 1:
                starfield_kick_timing = 2
                trellis.color(3, 3, OFF_WHITE)
                trellis.color(4, 3, OFF_WHITE)
                trellis.color(3, 4, OFF_WHITE)
                trellis.color(4, 4, OFF_WHITE)
            elif starfield_kick_timing == 2:
                starfield_kick_timing = 3
                # trellis.fill(BLACK)
                trellis.color(2, 2, STAR_TEAL)
                trellis.color(3, 2, STAR_TEAL)
                trellis.color(4, 2, STAR_TEAL)
                trellis.color(5, 2, STAR_TEAL)
                trellis.color(2, 3, STAR_TEAL)
                trellis.color(5, 3, STAR_TEAL)
                trellis.color(2, 4, STAR_TEAL)
                trellis.color(5, 4, STAR_TEAL)
                trellis.color(2, 5, STAR_TEAL)
                trellis.color(3, 5, STAR_TEAL)
                trellis.color(4, 5, STAR_TEAL)
                trellis.color(5, 5, STAR_TEAL)
            elif starfield_kick_timing == 3:
                starfield_kick_timing = 4
                # trellis.fill(BLACK)
                trellis.color(1, 1, RED)
                trellis.color(2, 1, RED)
                trellis.color(3, 1, RED)
                trellis.color(4, 1, RED)
                trellis.color(5, 1, RED)
                trellis.color(6, 1, RED)
                trellis.color(1, 2, RED)
                trellis.color(6, 2, RED)
                trellis.color(1, 3, RED)
                trellis.color(6, 3, RED)
                trellis.color(1, 4, RED)
                trellis.color(6, 4, RED)
                trellis.color(1, 5, RED)
                trellis.color(6, 5, RED)
                trellis.color(1, 6, RED)
                trellis.color(6, 6, RED)
                trellis.color(2, 6, RED)
                trellis.color(3, 6, RED)
                trellis.color(4, 6, RED)
                trellis.color(5, 6, RED)
            # elif starfield_kick_timing == 4:
            #     starfield_kick_timing = 5
            #     trellis.color(3, 3, BLACK)
            #     trellis.color(4, 3, BLACK)
            #     trellis.color(3, 4, BLACK)
            #     trellis.color(4, 4, BLACK)
            # elif starfield_kick_timing == 5:
            #     starfield_kick_timing = 6
            #     trellis.color(2, 2, BLACK)
            #     trellis.color(3, 2, BLACK)
            #     trellis.color(4, 2, BLACK)
            #     trellis.color(5, 2, BLACK)
            #     trellis.color(2, 3, BLACK)
            #     trellis.color(5, 3, BLACK)
            #     trellis.color(2, 4, BLACK)
            #     trellis.color(5, 4, BLACK)
            #     trellis.color(2, 5, BLACK)
            #     trellis.color(3, 5, BLACK)
            #     trellis.color(4, 5, BLACK)
            #     trellis.color(5, 5, BLACK)
            elif starfield_kick_timing >= 4:
                starfield_kick_timing = 0
                trellis.fill(BLACK)
    if not has_timing:
        trellis.fill(BLACK)
    trellis.show()
    time.sleep(0.012)

# while True:
#     if effect_start_time != 0:
#         cur_time = time.monotonic()
#         if cur_time - effect_start_time > 0:
#             effect_start_time = cur_time
#             effect_iter += 1
#             if effect_iter > 8:
#                 effect_start_time = 0
#                 effect_origin = (0, 0)
#                 effect_iter = 0
#             else:
#                 for y in range(8):
#                     for x in range(8):
#                         dist = max(
#                             abs(x - effect_origin[0]), abs(y - effect_origin[1]))
#                         if dist == effect_iter:# and (x == effect_origin[0] or y == effect_origin[1]):
#                             trellis.color(x, y, WHITE)
#                             frame_updated = True
#                         elif dist == effect_iter - 1:# and (x == effect_origin[0] or y == effect_origin[1]):
#                             trellis.color(x, y,  pixel_colors[x][y])
#                             frame_updated = True
#     if frame_updated:
#         trellis.show()
#         frame_updated = False
#     # The NeoTrellis can only be read every 17 milliseconds or so
#     # time.sleep(0.02)


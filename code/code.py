# SPDX-FileCopyrightText: 2022 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import random
import time
import board
import audiocore
import audiopwmio
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

# Setup PWM audio out
audio = audiopwmio.PWMAudioOut(board.D11)

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
    # Turn the LED to a different color when a rising edge is detected
    if edge == NeoTrellis.EDGE_RISING:
        started_playing_music = time.monotonic()
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

iter = 0
ITER_FAST_ANIM = 20
ITER_FAST_SFX = 0
starfield_delay = 0
sync_iter = 0
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
    if not has_timing:
        trellis.fill(BLACK)
    trellis.show()
    time.sleep(0.02)

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


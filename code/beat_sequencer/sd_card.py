"""SD Card controller"""

import storage
import os
import busio
import board
import adafruit_sdcard
import digitalio

class SDCard:
    def __init__(self, path, list_files=False):
        # The sd card
        spi_sd = busio.SPI(board.GP2, board.GP3, board.GP4)
        cs_sd = digitalio.DigitalInOut(board.GP5)
        sdcard = adafruit_sdcard.SDCard(spi_sd, cs_sd, baudrate=1320000 * 4) # Increase default baudrate to play wav files from SD card

        # Mount sd card at sd
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, path)

        # List all files on the SD card
        if list_files:
            print("Files on SD card:")
            for file in os.listdir(path):
                # Filename
                print(file, os.stat(f'{path}/{file}')[6] / 1024 / 1024, "MB")

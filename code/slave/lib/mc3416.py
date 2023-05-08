"""
A driver for the MC3416 3-axis accelerometer.
"""
import busio
import time
from micropython import const
from struct import unpack
from adafruit_bus_device.i2c_device import I2CDevice


I2C_ADDR = 0x4C

_REG_DEVICE_STATUS: int = const(0x05)
_REG_INT_ENABLE: int = const(0x06)
_REG_MODE: int = const(0x07)
_REG_SAMPLE_RATE: int = const(0x08)
_REG_MOTION_CONTROL: int = const(0x09)
_REG_DATAXL: int = const(0x0D)
_REG_DATAXH: int = const(0x0E)
_REG_DATAYL: int = const(0x0F)
_REG_DATAYH: int = const(0x10)
_REG_DATAZL: int = const(0x11)
_REG_DATAZH: int = const(0x12)
_REG_STATUS: int = const(0x13)
_REG_INT_STATUS: int = const(0x14)
_REG_DEVICE_ID: int = const(0x18)
_REG_RANGE: int = const(0x20)
_REG_XOFFL: int = const(0x21)
_REG_XOFFH: int = const(0x22)
_REG_YOFFL: int = const(0x23)
_REG_YOFFH: int = const(0x24)
_REG_ZOFFL: int = const(0x25)
_REG_ZOFFH: int = const(0x26)
_REG_XGAIN: int = const(0x27)
_REG_YGAIN: int = const(0x28)
_REG_ZGAIN: int = const(0x29)
_REG_TF_THRESHL: int = const(0x40)
_REG_TF_THRESHH: int = const(0x41)
_REG_TF_DEBOUNCE: int = const(0x42)
_REG_AM_THRESHL: int = const(0x43)
_REG_AM_THRESHH: int = const(0x44)
_REG_AM_DEBOUNCE: int = const(0x45)
_REG_SHAKE_THRESHL: int = const(0x46)
_REG_SHAKE_THRESHH: int = const(0x47)
_REG_P2P_DURATIONL: int = const(0x48)
_REG_P2P_DURATIONH: int = const(0x49)
_REG_TIMER_CTL: int = const(0x4A)

_MC3416_MG2G_MULTIPLIER: float = 0.0000061  # 0.061 mG per lsb
_STANDARD_GRAVITY = 9.80665
_MC3416_DEVICE_ID = 0xA0

class MC3416:
    """Driver for the MC3416 3-axis accelerometer."""
    def __init__(self, i2c):
        self._i2c = I2CDevice(i2c, I2C_ADDR)
        self._buffer = bytearray(6)
        self._in_buffer = bytearray(6)

        # Should respond with the device ID
        chip_id = self._read_register(_REG_DEVICE_ID, 1)
        if chip_id[0] != _MC3416_DEVICE_ID:
            raise RuntimeError("Unable to read MC3416 device ID, check wiring!")

        # Power on
        self._write_register_byte(_REG_MODE, 0x1)
    
    @property
    def raw_x(self):
        return unpack("<h", self._read_register(_REG_DATAXL, 2))[0]

    @property
    def raw_y(self):
        return unpack("<h", self._read_register(_REG_DATAYL, 2))[0]
    
    @property
    def raw_z(self):
        return unpack("<h", self._read_register(_REG_DATAZL, 2))[0]
    
    @property
    def acceleration(self):
        # Read all 6 bytes at once
        self._buffer[0] = _REG_DATAXL & 0xFF
        x, y, z = unpack("<hhh", self._read_register(_REG_DATAXL, 6))
        x = x * _MC3416_MG2G_MULTIPLIER * _STANDARD_GRAVITY
        y = y * _MC3416_MG2G_MULTIPLIER * _STANDARD_GRAVITY
        z = z * _MC3416_MG2G_MULTIPLIER * _STANDARD_GRAVITY
        return x, y, z
        

    def _read_register(self, register: int, length: int) -> int:
        self._buffer[0] = register & 0xFF
        with self._i2c as i2c:
            i2c.write_then_readinto(self._buffer, self._in_buffer, out_start=0, out_end=1, in_start=0, in_end=length)
            return self._in_buffer[0:length]

    def _write_register_byte(self, register: int, value: int) -> None:
        self._buffer[0] = register & 0xFF
        self._buffer[1] = value & 0xFF
        with self._i2c as i2c:
            i2c.write(self._buffer, start=0, end=2)

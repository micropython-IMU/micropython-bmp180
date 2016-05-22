'''
This module serves as base class for a unified micropython driver interface. It is _NOT_ official but only a prototype to experiment with the different ideas coming up in the discussion.
'''

ALL = (1<<31)-1
TEMPERATURE = 1<<0
PRESSURE = 1<<1
HUMIDITY = 1<<2
ACCEL_X = 1<<3
ACCEL_Y = 1<<4
ACCEL_Z = 1<<5
GYRO_X = 1<<6
GYRO_Y = 1<<7
GYRO_Z = 1<<8
MAG_X = 1<<9
MAG_Y = 1<<10
MAG_Z = 1<<11

class SensorBase:

    def config():
        raise NotImplementedError

    def measure(self, what_bitmask=ALL):
        raise NotImplementedError

    def get_fixedp(self, what):
        raise NotImplementedError

    def get_float(self, what):
        raise NotImplementedError

class SensorBase:

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

    def measure(self, what_bitmask=ALL):
        raise NotImplementedError

    def measure_blocking(self, what_bitmask=ALL):
        raise NotImplementedError

    def get_fixedp(self, what):
        raise NotImplementedError

    def get_float(self, what):
        raise NotImplementedError

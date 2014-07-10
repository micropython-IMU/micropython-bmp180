# bmp180 - a micropython module for the bmp180 pressure sensor

# The MIT License (MIT)
# Copyright (c) 2014 Sebastian Plamauer, oeplse@gmail.com
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from struct import unpack
import pyb


# BMP180 class
class BMP180():

    # adress of BMP180 is hardcoded on the sensor
    _bmp_addr = 119

    # init
    def __init__(self, side_char=None):

        if side_char is None:
            side = 2
        elif str(side_char) in ('X', '1'):
            side = 1
        elif str(side_char) in ('Y', '2'):
            side = 2
        else:
            print('pass either X, 1, Y, 2 or None, defaulting to Y')
            side = 2

        self.oss = 0
        _bmp_addr = self._bmp_addr
        self.bmp = pyb.I2C(side, pyb.I2C.MASTER)
        self.chip_id = self.bmp.mem_read(2, _bmp_addr, 0xD0)
        self.AC1 = unpack('>h', self.bmp.mem_read(2, _bmp_addr, 0xAA))[0]
        self.AC2 = unpack('>h', self.bmp.mem_read(2, _bmp_addr, 0xAC))[0]
        self.AC3 = unpack('>h', self.bmp.mem_read(2, _bmp_addr, 0xAE))[0]
        self.AC4 = unpack('>H', self.bmp.mem_read(2, _bmp_addr, 0xB0))[0]
        self.AC5 = unpack('>H', self.bmp.mem_read(2, _bmp_addr, 0xB2))[0]
        self.AC6 = unpack('>H', self.bmp.mem_read(2, _bmp_addr, 0xB4))[0]
        self.B1 = unpack('>h', self.bmp.mem_read(2, _bmp_addr, 0xB6))[0]
        self.B2 = unpack('>h', self.bmp.mem_read(2, _bmp_addr, 0xB8))[0]
        self.MB = unpack('>h', self.bmp.mem_read(2, _bmp_addr, 0xBA))[0]
        self.MC = unpack('>h', self.bmp.mem_read(2, _bmp_addr, 0xBC))[0]
        self.MD = unpack('>h', self.bmp.mem_read(2, _bmp_addr, 0xBE))[0]

    # gauge uncompensated temperature
    def gauge_UT(self):

        self.bmp.mem_write(0x2E, self._bmp_addr, 0xF4)
        return pyb.millis()+5

    # get uncompensated temperature
    def get_UT(self, t_ready):

        if pyb.millis() <= t_ready:
            self.get_UT(t_ready)
        else:
            return unpack('>h', self.bmp.mem_read(2, self._bmp_addr, 0xF6))[0]

    # uncompensated temperature
    def UT(self):

        return self.get_UT(self.gauge_UT())

    # gauge uncompensated pressure
    def gauge_UP(self):

        delay = [5, 8, 14, 25]
        self.bmp.mem_write((0x34+(self.oss << 6)), self._bmp_addr, 0xF4)
        return pyb.millis() + pyb.delay(delay[self.oss])

    # get uncompensated pressure
    def get_UP(self, t_ready):

        if pyb.millis() <= t_ready:
            self.get_UP(t_ready)
        else:
            MSB = unpack('<h', self.bmp.mem_read(1, self._bmp_addr, 0xF6))[0]
            LSB = unpack('<h', self.bmp.mem_read(1, self._bmp_addr, 0xF7))[0]
            XLSB = unpack('<h', self.bmp.mem_read(1, self._bmp_addr, 0xF8))[0]
            return ((MSB << 16)+(LSB << 8)+XLSB) >> (8-self.oss)

    # uncompensated pressure
    def UP(self):

        return self.get_UP(self.gauge_UP())

    # calculated temperature
    def calc_temperature(self, UT):

        X1 = (UT-self.AC6)*self.AC5/2**15
        X2 = self.MC*2**11/(X1+self.MD)
        B5 = X1+X2
        return ((B5+8)/2**4)/10

    # B5 value for temperature compensation of pressure
    def B5(self, UT):

        X1 = (UT-self.AC6)*self.AC5/2**15
        X2 = self.MC*2**11/(X1+self.MD)
        return X1+X2

    # calculated pressure
    def calc_pressure(self, UT, UP):

        B6 = self.B5(UT)-4000
        X1 = (self.B2*(B6*B6/2**12))/2**11
        X2 = self.AC2*B6/2**11
        X3 = X1+X2
        B3 = ((int((self.AC1*4+X3)) << self.oss)+2)/4
        X1 = self.AC3*B6/2**13
        X2 = (self.B1*(B6*B6/2**12))/2**16
        X3 = ((X1+X2)+2)/2**2
        B4 = self.AC4*(X3+32768)/2**15
        B7 = (abs(UP)-B3)*(50000 >> self.oss)
        if B7 < 0x80000000:
            pressure = (B7*2)/B4
        else:
            pressure = (B7/B4)*2
        X1 = (pressure/2**8)**2
        X1 = (X1*3038)/2**16
        X2 = (-7357*pressure)/2**16
        return pressure+(X1+X2+3791)/2**4

    # temperature
    def temperature(self):
        return self.calc_temperature(self.UT)

    # pressure
    def pressure(self):
        return self.calc_pressure(self.UT, self.UP)

    # pressure baseline
    def baseline(self, dt=None):
        if (dt is None) or (dt == 0):
            dt = 1000
        count = 0
        sum_pressure = 0
        t_stop = pyb.millis()+dt
        while pyb.millis() < t_stop:
            sum_pressure = sum_pressure + self.pressure()
            count = count + 1
        return sum_pressure / count

    # altitude above reference
    def altitude_above_ref(self, pressure, pressure_ref):
        # absolute: pressure_ref = baseline
        # true: pressure_ref = QNH*100
        # pressure: pressure_ref = 101325
        if pressure_ref == 0:
            print('pressure_ref can\'t be zero')
            return None
        else:
            return 44330*(1-(pressure/pressure_ref)**(1/5.255))

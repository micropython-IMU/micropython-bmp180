'''
bmp180 is a micropython module for the Bosch BMP180 sensor. It measures
temperature as well as pressure, with a high enough resolution to calculate
altitude.
Breakoutboard: http://www.adafruit.com/products/1603  
data-sheet: http://ae-bst.resource.bosch.com/media/products/dokumente/
bmp180/BST-BMP180-DS000-09.pdf

The MIT License (MIT)
Copyright (c) 2014 Sebastian Plamauer, oeplse@gmail.com
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

from struct import unpack as unp
import pyb
import math


# BMP180 class
class BMP180():
    '''
    Module for the BMP180 pressure sensor.
    '''

    _bmp_addr = 119             # adress of BMP180 is hardcoded on the sensor

    # init
    def __init__(self, side_str=None):

        # choose which i2c port to use
        if side_str == 'X':
            side = 1
        elif side_str == 'Y':
            side = 2
        else:
            print('pass either X or Y, defaulting to Y')
            side = 2

        # create i2c obect
        _bmp_addr = self._bmp_addr
        self._bmp_i2c = pyb.I2C(side, pyb.I2C.MASTER)
        self.chip_id = self._bmp_i2c.mem_read(2, _bmp_addr, 0xD0)
        # read calibration data from EEPROM
        self._AC1 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xAA))[0]
        self._AC2 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xAC))[0]
        self._AC3 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xAE))[0]
        self._AC4 = unp('>H', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB0))[0]
        self._AC5 = unp('>H', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB2))[0]
        self._AC6 = unp('>H', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB4))[0]
        self._B1 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB6))[0]
        self._B2 = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xB8))[0]
        self._MB = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xBA))[0]
        self._MC = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xBC))[0]
        self._MD = unp('>h', self._bmp_i2c.mem_read(2, _bmp_addr, 0xBE))[0]

        # settings to be adjusted by user
        self.oversample_sett = 3
        self.baseline = 101325.0

        # private attributes not to be used by user
        self._t_temperature_ready = None
        self._UT = None
        self._t_pressure_ready = None
        self._B5 = None

        # output raw
        self.UT_raw = None
        self.B5_raw = None
        self.MSB_raw = None
        self.LSB_raw = None
        self.XLSB_raw = None

        for _ in range(128):
            next(self.gauge())
            pyb.delay(1)

    def compvaldump(self):
        '''
        Returns a list of all compensation values
        '''
        return [self._AC1, self._AC2, self._AC3, self._AC4, self._AC5, self._AC6, 
                self._B1, self._B2, self._MB, self._MC, self._MD, self.oversample_sett]

    # gauge raw
    def gauge(self):
        '''
        Generator refreshing the raw measurments.
        '''
        if self._t_pressure_ready is None:
            if self._B5 is None:
                if self._t_temperature_ready is None:
                    self._bmp_i2c.mem_write(0x2E, self._bmp_addr, 0xF4)
                    self._t_temperature_ready = pyb.millis()+5
                while pyb.millis() <= self._t_temperature_ready:
                    yield None
                try:
                    self.UT_raw = self._bmp_i2c.mem_read(2, self._bmp_addr, 0xF6)
                except:
                    yield None
                self._B5 = True
                self._t_temperature_ready = None
                yield None

            if self.oversample_sett not in range(4):
                print('oversample_sett can only be 0, 1, 2 or 3, using 3 instead')
                self.oversample_sett = 3

            delays = (5, 8, 14, 25)

            self._bmp_i2c.mem_write((0x34+(self.oversample_sett << 6)),
                                    self._bmp_addr,
                                    0xF4)

            self._t_pressure_ready = pyb.millis() + delays[self.oversample_sett]
        while pyb.millis() <= self._t_pressure_ready:
            yield None
        try:
            self.MSB_raw = self._bmp_i2c.mem_read(1, self._bmp_addr, 0xF6)
            self.LSB_raw = self._bmp_i2c.mem_read(1, self._bmp_addr, 0xF7)
            self.XLSB_raw = self._bmp_i2c.mem_read(1, self._bmp_addr, 0xF8)
        except:
            yield None
        self._t_pressure_ready = None
        self._B5 = None
        self._t_temperature_ready = None
        yield None

    @property
    def temperature(self):
        '''
        Temperature in degree C.
        '''
        next(self.gauge())
        try:
            UT = unp('>h', self.UT_raw)[0]
        except:
            return 0.0
        X1 = (UT-self._AC6)*self._AC5/2**15
        X2 = self._MC*2**11/(X1+self._MD)
        self.B5_raw = X1+X2
        return (((X1+X2)+8)/2**4)/10

    @property
    def pressure(self):
        '''
        Pressure in mbar.
        '''
        next(self.gauge())
        self.temperature
        try:
            MSB = unp('<h', self.MSB_raw)[0]
            LSB = unp('<h', self.LSB_raw)[0]
            XLSB = unp('<h', self.XLSB_raw)[0]
        except:
            return 0.0
        UP = ((MSB << 16)+(LSB << 8)+XLSB) >> (8-self.oversample_sett)
        B6 = self.B5_raw-4000
        X1 = (self._B2*(B6**2/2**12))/2**11
        X2 = self._AC2*B6/2**11
        X3 = X1+X2
        B3 = ((int((self._AC1*4+X3)) << self.oversample_sett)+2)/4
        X1 = self._AC3*B6/2**13
        X2 = (self._B1*(B6**2/2**12))/2**16
        X3 = ((X1+X2)+2)/2**2
        B4 = abs(self._AC4)*(X3+32768)/2**15
        B7 = (abs(UP)-B3) * (50000 >> self.oversample_sett)
        if B7 < 0x80000000:
            pressure = (B7*2)/B4
        else:
            pressure = (B7/B4)*2
        X1 = (pressure/2**8)**2
        X1 = (X1*3038)/2**16
        X2 = (-7357*pressure)/2**16
        return pressure+(X1+X2+3791)/2**4

    @property
    def altitude(self):
        '''
        Altitude in m.
        '''
        try:
            p = -7990.0*math.log(self.pressure/self.baseline)
        except:
            p = 0.0
        return p

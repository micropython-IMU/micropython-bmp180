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

import pyb
from sensorbase import *
from struct import unpack as unp


class BMP180(SensorBase):
    '''
    Module for the BMP180 pressure sensor.
    '''

    addr = 119             # adress of BMP180 is hardcoded on the sensor

    def __init__(self, i2c=pyb.I2C(1, pyb.I2C.MASTER), oversample=3):

        self.i2c = i2c
        self.oversample_setting = oversample
        self.chip_id = self.i2c.mem_read(2, self.addr, 0xD0)

        # read calibration data from EEPROM
        self._AC1 = unp('>h', self.i2c.mem_read(2, self.addr, 0xAA))[0]
        self._AC2 = unp('>h', self.i2c.mem_read(2, self.addr, 0xAC))[0]
        self._AC3 = unp('>h', self.i2c.mem_read(2, self.addr, 0xAE))[0]
        self._AC4 = unp('>H', self.i2c.mem_read(2, self.addr, 0xB0))[0]
        self._AC5 = unp('>H', self.i2c.mem_read(2, self.addr, 0xB2))[0]
        self._AC6 = unp('>H', self.i2c.mem_read(2, self.addr, 0xB4))[0]
        self._B1 = unp('>h', self.i2c.mem_read(2, self.addr, 0xB6))[0]
        self._B2 = unp('>h', self.i2c.mem_read(2, self.addr, 0xB8))[0]
        self._MB = unp('>h', self.i2c.mem_read(2, self.addr, 0xBA))[0]
        self._MC = unp('>h', self.i2c.mem_read(2, self.addr, 0xBC))[0]
        self._MD = unp('>h', self.i2c.mem_read(2, self.addr, 0xBE))[0]

        # output raw
        self.UT_raw = None
        self.B5_raw = None
        self.MSB_raw = None
        self.LSB_raw = None
        self.XLSB_raw = None
        self._gauge = self._makegauge() # Generator instance
        for _ in range(128):
            next(self._gauge)
            pyb.delay(1)

    def _makegauge(self):
        '''
        Generator refreshing the raw measurments.
        '''
        delays = (5, 8, 14, 25)
        while True:
            self.i2c.mem_write(0x2E, self.addr, 0xF4)
            t_start = pyb.millis()
            while pyb.elapsed_millis(t_start) <= 5: # 5mS delay
                yield None
            try:
                self.UT_raw = self.i2c.mem_read(2, self.addr, 0xF6)
            except:
                yield None

            self.i2c.mem_write((0x34+(self.oversample_setting << 6)),
                                    self.addr,
                                    0xF4)

            t_pressure_ready = delays[self.oversample_setting]
            t_start = pyb.millis()
            while pyb.elapsed_millis(t_start) <= t_pressure_ready:
                yield None
            try:
                self.MSB_raw = self.i2c.mem_read(1, self.addr, 0xF6)
                self.LSB_raw = self.i2c.mem_read(1, self.addr, 0xF7)
                self.XLSB_raw = self.i2c.mem_read(1, self.addr, 0xF8)
            except:
                yield None
            yield True

    def config(self, i2c=None, oversample=None):
        '''
        Configure sensor.
        oversample: 0, 1, 2, or 3
        i2c: i2c object
        '''

        if oversample is not None:
            if oversample in range(4):
                self.oversample_setting = oversample
            else:
                raise ValueError('oversample has to be 0, 1, 2, 3')

        if i2c is not None:
            if isinstance(i2c, pyb.I2C):
                self.i2c = i2c
            else:
                raise TypeError('i2c has to be i2c object')

    def measure(self, what_bitmask=ALL):
        '''
        Measure values.
        '''
        if next(self._gauge): # Discard old data
            pass
        while next(self._gauge) is None:
            pass

    def get_fixedp(self, what):
        '''
        TEMPERATURE in dC as int
        PRESSURE in Pa as int
        '''

        if what == TEMPERATURE:
            UT = unp('>h', self.UT_raw)[0]
            X1 = (UT-self._AC6)*self._AC5>>15
            X2 = (self._MC<<11)//(X1+self._MD)
            self.B5_raw = X1+X2
            return ((X1+X2)+8)>>4

        if what == PRESSURE:
            self.get_fixedp(TEMPERATURE)
            MSB = unp('<h', self.MSB_raw)[0]
            LSB = unp('<h', self.LSB_raw)[0]
            XLSB = unp('<h', self.XLSB_raw)[0]
            UP = ((MSB << 16)+(LSB << 8)+XLSB) >> (8-self.oversample_setting)
            B6 = self.B5_raw-4000
            X1 = (self._B2*(B6**2)>>12)>>11
            X2 = (self._AC2*B6)>>11
            X3 = X1+X2
            B3 = (((self._AC1*4+X3) << self.oversample_setting)+2)//4
            X1 = (self._AC3*B6)>>13
            X2 = (self._B1*(B6**2)>>12)>>16
            X3 = ((X1+X2)+2)>>2
            B4 = (abs(self._AC4)*(X3+32768))>>15
            B7 = (abs(UP)-B3) * (50000 >> self.oversample_setting)
            if B7 < 0x80000000:
                pressure = (B7*2)//B4
            else:
                pressure = (B7//B4)*2
            X1 = (pressure>>8)**2
            X1 = (X1*3038)>>16
            X2 = (-7357*pressure)>>16
            return pressure+(X1+X2+3791)

    def get_float(self, what):
        '''
        TEMPERATURE in C as float
        PRESSURE in Pa as float
        '''

        if what == TEMPERATURE:
            UT = unp('>h', self.UT_raw)[0]
            X1 = (UT-self._AC6)*self._AC5>>15
            X2 = (self._MC<<11)/(X1+self._MD)
            self.B5_raw = X1+X2
            return (((X1+X2)+8)/2**4)/10

        if what == PRESSURE:
            self.get_float(TEMPERATURE)
            MSB = unp('<h', self.MSB_raw)[0]
            LSB = unp('<h', self.LSB_raw)[0]
            XLSB = unp('<h', self.XLSB_raw)[0]
            UP = ((MSB << 16)+(LSB << 8)+XLSB) >> (8-self.oversample_setting)
            B6 = self.B5_raw-4000
            X1 = (self._B2*(B6**2/2**12))/2**11
            X2 = self._AC2*B6/2**11
            X3 = X1+X2
            B3 = ((int((self._AC1*4+X3)) << self.oversample_setting)+2)/4
            X1 = self._AC3*B6/2**13
            X2 = (self._B1*(B6**2/2**12))/2**16
            X3 = ((X1+X2)+2)/2**2
            B4 = abs(self._AC4)*(X3+32768)/2**15
            B7 = (abs(UP)-B3) * (50000 >> self.oversample_setting)
            if B7 < 0x80000000:
                pressure = (B7*2)/B4
            else:
                pressure = (B7/B4)*2
            X1 = (pressure/2**8)**2
            X1 = (X1*3038)/2**16
            X2 = (-7357*pressure)/2**16
            return pressure+(X1+X2+3791)/2**4

'''
bmp180 is a micropython module for the Bosch BMP180 sensor. It measures
temperature as well as pressure, with a high enough resolution to calculate
altitude.
Breakoutboard: http://www.adafruit.com/products/1603  
data-sheet: http://ae-bst.resource.bosch.com/media/products/dokumente/bmp180/BST-BMP180-DS000-09.pdf

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
        self.oversample_sett = 0
        self.temp_comp_sample_rate = 1
        self.baseline = 101325

        # priate attributes not to be used by user
        self._t_temperature_ready = None
        self._UT = None
        self._t_pressure_ready = None
        self._B5 = None
        self._t_B5 = None
        self._dt_B5 = 1000/self.temp_comp_sample_rate

    # gauge temperature
    def gauge_temperature(self):
        '''
        Starts the temperature measurement and sets the time it will be
        finished.
        '''
        self._bmp_i2c.mem_write(0x2E, self._bmp_addr, 0xF4)
        self._t_temperature_ready = pyb.millis()+5

        return

    # get temperature
    def get_temperature(self):
        '''
        Waits until the temperature measurement is finished, then returns the
        temperature.
        '''
        if self._t_temperature_ready is None:
            self.gauge_temperature()

        while pyb.millis() <= self._t_temperature_ready:
            pass

        self._UT = unp('>h', self._bmp_i2c.mem_read(2, self._bmp_addr, 0xF6))[0]
        X1 = (self._UT-self._AC6)*self._AC5/2**15
        X2 = self._MC*2**11/(X1+self._MD)
        self._t_temperature_ready = None

        return (((X1+X2)+8)/2**4)/10

    # B5 value for temperature compensation of pressure
    def _get_B5(self):
        '''
        Calculates and sets compensation value B5.
        '''
        if (self._B5 is None) or ((pyb.millis()-self._t_B5) > self._dt_B5):
            self.get_temperature()
            X1 = (self._UT-self._AC6)*self._AC5/2**15
            X2 = self._MC*2**11/(X1+self._MD)
            self._B5 = X1+X2
            self._t_B5 = pyb.millis()

        return

    # gauge pressure
    def gauge_pressure(self):
        '''
        Starts the pressure measurement and sets the time it will be
        finished.
        '''
        if self._B5 is None:
            self._get_B5()

        if self.oversample_sett not in range(4):
            print('oversample_sett can only be 0, 1, 2 or 3, using 3 instead')
            self.oversample_sett = 3

        delays = (5, 8, 14, 25)

        self._bmp_i2c.mem_write((0x34+(self.oversample_sett << 6)),self._bmp_addr,0xF4)
        self._t_pressure_ready = pyb.millis() + delays[self.oversample_sett]

        return

    # get pressure
    def get_pressure(self):
        '''
        Waits until the pressure measurement is finished, then returns the
        pressure.
        '''
        self._get_B5()

        if self._t_pressure_ready is None:
            self.gauge_pressure()

        while pyb.millis() <= self._t_pressure_ready:
            pass

        MSB = unp('<h', self._bmp_i2c.mem_read(1, self._bmp_addr, 0xF6))[0]
        LSB = unp('<h', self._bmp_i2c.mem_read(1, self._bmp_addr, 0xF7))[0]
        XLSB = unp('<h', self._bmp_i2c.mem_read(1, self._bmp_addr, 0xF8))[0]

        UP = ((MSB << 16)+(LSB << 8)+XLSB) >> (8-self.oversample_sett)
        B6 = self._B5-4000
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
        self._t_pressure_ready = None

        return pressure+(X1+X2+3791)/2**4

    # pressure baseline
    def set_baseline(self, dt=None):
        '''
        Measures the pressure for a given time and sets baseline to the mean of
        the measurements.
        '''
        if (dt is None) or (dt == 0):
            dt = 1000

        count = 0
        sum_pressure = 0
        t_stop = pyb.millis() + dt

        while pyb.millis() < t_stop:
            sum_pressure = sum_pressure + self.get_pressure()
            count = count + 1

        self.baseline = sum_pressure / count

        return

    # altitude above reference
    def get_altitude(self):
        '''
        Calculates and returns the altitude relative to baseline.

        | altitude |       baseline |  
        |:--------:|:--------------:|  
        | absolute |     baseline() |  
        | true     |        QNH*100 |  
        | pressure | 101325 or None |  
        '''
        try:
            return -7990*math.log(self.get_pressure()/self.baseline)

        except ZeroDivisionError:
            print('baseline can\'t be zero')
            return None

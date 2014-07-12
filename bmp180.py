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


# BMP180 class
class BMP180():
    '''
    Module for the BMP180 pressure sensor.
    '''

    _bmp_addr = 119             # adress of BMP180 is hardcoded on the sensor

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

        self.oversample_sett = 0
        _bmp_addr = self._bmp_addr
        self.bmp_i2c = pyb.I2C(side, pyb.I2C.MASTER)
        self.chip_id = self.bmp_i2c.mem_read(2, _bmp_addr, 0xD0)
        self.cal_AC1 = unp('>h', self.bmp_i2c.mem_read(2, _bmp_addr, 0xAA))[0]
        self.cal_AC2 = unp('>h', self.bmp_i2c.mem_read(2, _bmp_addr, 0xAC))[0]
        self.cal_AC3 = unp('>h', self.bmp_i2c.mem_read(2, _bmp_addr, 0xAE))[0]
        self.cal_AC4 = unp('>H', self.bmp_i2c.mem_read(2, _bmp_addr, 0xB0))[0]
        self.cal_AC5 = unp('>H', self.bmp_i2c.mem_read(2, _bmp_addr, 0xB2))[0]
        self.cal_AC6 = unp('>H', self.bmp_i2c.mem_read(2, _bmp_addr, 0xB4))[0]
        self.cal_B1 = unp('>h', self.bmp_i2c.mem_read(2, _bmp_addr, 0xB6))[0]
        self.cal_B2 = unp('>h', self.bmp_i2c.mem_read(2, _bmp_addr, 0xB8))[0]
        self.cal_MB = unp('>h', self.bmp_i2c.mem_read(2, _bmp_addr, 0xBA))[0]
        self.cal_MC = unp('>h', self.bmp_i2c.mem_read(2, _bmp_addr, 0xBC))[0]
        self.cal_MD = unp('>h', self.bmp_i2c.mem_read(2, _bmp_addr, 0xBE))[0]
        self.pressure_MSL = 101325

    # gauge uncompensated temperature
    def gauge_uncomp_temperature(self):
        '''
        Starts the temperature measurement and returns the time it will be
        finished.
        '''
        self.bmp_i2c.mem_write(0x2E, self._bmp_addr, 0xF4)
        return pyb.millis()+5

    # get uncompensated temperature
    def get_uncomp_temperature(self, t_ready):
        '''
        Waits until the temperature measurement is finished, then returns the
        uncompensated temperature.
        '''
        if pyb.millis() <= t_ready:
            self.get_uncomp_temperature(t_ready)
        else:
            return unp('>h', self.bmp_i2c.mem_read(2, self._bmp_addr, 0xF6))[0]

    # uncompensated temperature
    def uncomp_temperature(self):
        '''
        Measures and returns the uncompensated temperature.
        '''
        return self.get_uncomp_temperature(self.gauge_uncomp_temperature())

    # gauge uncompensated pressure
    def gauge_uncomp_pressure(self):
        '''
        Starts the pressure measurement and returns the time it will be
        finished.
        '''
        delay = [5, 8, 14, 25]
        self.bmp_i2c.mem_write(
                                (0x34+(self.oversample_sett << 6)),
                                self._bmp_addr,
                                0xF4)

        return pyb.millis() + pyb.delay(delay[self.oversample_sett])

    # get uncompensated pressure
    def get_uncomp_pressure(self, t_ready):
        '''
        Waits until the pressure measurement is finished, then returns the
        uncompensated temperature.
        '''
        if pyb.millis() <= t_ready:
            self.get_uncomp_pressure(t_ready)
        else:
            MSB = unp('<h', self.bmp_i2c.mem_read(1, self._bmp_addr, 0xF6))[0]
            LSB = unp('<h', self.bmp_i2c.mem_read(1, self._bmp_addr, 0xF7))[0]
            XLSB = unp('<h', self.bmp_i2c.mem_read(1, self._bmp_addr, 0xF8))[0]
            return ((MSB << 16)+(LSB << 8)+XLSB) >> (8-self.oversample_sett)

    # uncompensated pressure
    def uncomp_pressure(self):
        '''
        Measures and returns the uncompensated pressure.
        '''
        return self.get_uncomp_pressure(self.gauge_uncomp_pressure())

    # B5 value for temperature compensation of pressure
    def _B5(self, uncomp_temperature):
        '''
        Calculates and returns compensation value B5.
        '''
        X1 = (uncomp_temperature-self.cal_AC6)*self.cal_AC5/2**15
        X2 = self.cal_MC*2**11/(X1+self.cal_MD)
        return X1+X2

    # calculated temperature
    def calc_temperature(self, uncomp_temperature):
        '''
        Calculates and returns the compensted temperature.
        '''
        return ((self._B5(uncomp_temperature)+8)/2**4)/10

    # calculated pressure
    def calc_pressure(self, uncomp_temperature, uncomp_pressure):
        '''
        Calculates and returns the compensated pressure.
        '''
        B6 = self._B5(uncomp_temperature)-4000
        X1 = (self.cal_B2*(B6*B6/2**12))/2**11
        X2 = self.cal_AC2*B6/2**11
        X3 = X1+X2
        B3 = ((int((self.cal_AC1*4+X3)) << self.oversample_sett)+2)/4
        X1 = self.cal_AC3*B6/2**13
        X2 = (self.cal_B1*(B6*B6/2**12))/2**16
        X3 = ((X1+X2)+2)/2**2
        B4 = self.cal_AC4*(X3+32768)/2**15
        B7 = (abs(uncomp_pressure)-B3) * (50000 >> self.oversample_sett)
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
        '''
        Measures and returns the compensated temperature.
        '''
        return self.calc_temperature(self.uncomp_temperature)

    # pressure
    def pressure(self):
        '''
        Measures and returns the compensated pressure.
        '''
        return self.calc_pressure(self.uncomp_temperature,
                                  self.uncomp_pressure)

    # pressure baseline
    def baseline(self, dt=None):
        '''
        Measures the pressure for a given time and returns the mean of the
        measurements.
        '''
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
    def altitude_above_ref(self, pressure, pressure_ref=None):
        '''
        Calculates and returns the altitude relative to a reference pressure.

        | altitude |   pressure_ref |  
        |:--------:|:--------------:|  
        | absolute |       baseline |  
        | true     |        QNH*100 |  
        | pressure | 101325 or None |  
        '''
        if pressure_ref == None:
            pressure_ref = self.pressure_MSL
        elif pressure_ref == 0:
            print('pressure_ref can\'t be zero')
            return None
        else:
            return 44330*(1-(pressure/pressure_ref)**(1/5.255))

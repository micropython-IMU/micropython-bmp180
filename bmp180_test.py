# bmp180_test - a test for the micropython module bmp180
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

import sys
import pyb

sys.path.append('1:/')

from bmp180 import BMP180

try:

    print('init class')
    bmp180 = BMP180('Y')

    bmp180.oversample_sett = 2              # default = 0

    print('info')
    print(BMP180()._bmp_addr)
    print(bmp180.oversample_sett)
    print(bmp180.chip_id)
    print(bmp180.cal_AC1)
    print(bmp180.cal_AC2)
    print(bmp180.cal_AC3)
    print(bmp180.cal_AC4)
    print(bmp180.cal_AC5)
    print(bmp180.cal_AC6)
    print(bmp180.cal_B1)
    print(bmp180.cal_B2)
    print(bmp180.cal_MB)
    print(bmp180.cal_MC)
    print(bmp180.cal_MD)

    print('values')
    print(bmp180.uncomp_temperature())
    print(bmp180.uncomp_pressure())
    print(bmp180.temperature())
    print(bmp180.B5())
    print(bmp180.pressure())

    print('baseline')
    print(bmp180.baseline())
    print(bmp180.baseline(100))
    print(bmp180.baseline(0))

    print('altitudes')
    print(bmp180.altitude_above_ref(101325))
    print(bmp180.altitude_above_ref(0))

    print('\n\tTest passed.\n')

except:
    print('\n\tTest failed.\n')

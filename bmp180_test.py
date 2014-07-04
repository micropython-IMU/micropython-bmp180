import sys
import pyb

sys.path.append('1:/')

from bmp180 import BMP180

try:

    print('init class')
    bmp180 = BMP180()

    print('info')
    print(BMP180()._bmp_addr)
    print(bmp180.oss)
    print(bmp180.chip_id)
    print(bmp180.AC1)
    print(bmp180.AC2)
    print(bmp180.AC3)
    print(bmp180.AC4)
    print(bmp180.AC5)
    print(bmp180.AC6)
    print(bmp180.B1)
    print(bmp180.B2)
    print(bmp180.MB)
    print(bmp180.MC)
    print(bmp180.MD)

    print('values')
    print(bmp180.UT())
    print(bmp180.UP())
    print(bmp180.T())
    print(bmp180.B5())
    print(bmp180.p())

    print('baseline')
    print(bmp180.baseline())
    print(bmp180.baseline(100))
    print(bmp180.baseline(0))

    print('altitudes')
    print(bmp180.altitude_above_ref(101325))
    print(bmp180.altitude_above_ref(0))

    print(bmp180.altitude_abs())
    print(bmp180.altitude_abs(101325))

    print(bmp180.altitude_true(1013.25))

    print(bmp180.altitude_pressure())

    print('\n\tTest passed.\n')

except:

    print('\n\tTest failed.\n')

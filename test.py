from bmp180 import *
from altimeter import altitude

baro = BMP180()

baro.config(oversample=0)

baro.measure(ALL)
it = baro.get_fixedp(TEMPERATURE)
ip = baro.get_fixedp(PRESSURE)
ft = baro.get_float(TEMPERATURE)
fp = baro.get_float(PRESSURE)

print(it, ip, ft, fp)

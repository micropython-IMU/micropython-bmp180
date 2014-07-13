# main.py -- put your code here!

from bmp180 import BMP180

print('created obj')
baro = BMP180('X')

print('first')
baro.gauge_temperature()
baro.get_temperature()
baro.gauge_pressure()
baro.get_pressure()
baro.get_altitude()
baro.set_baseline()
print('done')

print('set wrong oversample')
baro.oversample_sett = 4
print('second')
baro.gauge_temperature()
baro.get_temperature()
baro.gauge_pressure()
baro.get_pressure()
baro.get_altitude()
baro.set_baseline()
print('done')

print('set wrong baseline')
baro.baseline = 0
print('third')
baro.gauge_temperature()
baro.get_temperature()
baro.gauge_pressure()
baro.get_pressure()
baro.get_altitude()
baro.set_baseline()
print('done')

print('pass')

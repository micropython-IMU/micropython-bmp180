micropython-bmp180
==================

Module bmp180
-----------------
bmp180 is a micropython module for the Bosch BMP180 sensor. It measures
temperature as well as pressure, with a high enough resolution to calculate
altitude.  
Breakoutboard: http://www.adafruit.com/products/1603  
data-sheet: http://ae-bst.resource.bosch.com/media/products/dokumente/bmp180/BST-BMP180-DS000-09.pdf

### Wiring the sensor to the pyboard

| pyboard| bmp180 |
|:------:|:------:|
| VIN    | VIN    |
| 3V3    | 3Vo    |
| GND    | GND    |
| SCL    | SCL    |
| SDA    | SDA    |

### Quickstart

Example:
```python
from bmp180 import BMP180
bmp180 = BMP180()
bmp180.oversample_sett = 2
temp = bmp180.temperature()
baseline = bmp180.baseline(1000)
p = bmp180.pressure()
altitude = bmp180.altitude_above_ref(p, baseline)
print(temp, baseline, p, altitude)
```
Note that in this example the altitude will be around zero, because the pressure measurment is done immediatly after the baseline setting.

Classes
-------
``BMP180``  
Module for the BMP180 pressure sensor.  
![UML diagramm](https://raw.githubusercontent.com/turbinenreiter/micropython-bmp180/master/classes_BMP180.png "UML diagramm")


Methods
--------------


``altitude_above_ref(self, pressure, pressure_ref=None)``  
Calculates and returns the altitude relative to a reference pressure.  

| altitude |   pressure_ref |  
|:--------:|:--------------:|  
| absolute |       baseline |  
| true     |        QNH*100 |  
| pressure | 101325 or None |  

``baseline(self, dt=None)``  
Measures the pressure for a given time and returns the mean of the  
measurements.

``calc_pressure(self, uncomp_temperature, uncomp_pressure)``  
Calculates and returns the compensated pressure.

``calc_temperature(self, uncomp_temperature)``  
Calculates and returns the compensted temperature.  

``gauge_uncomp_pressure(self)``  
Starts the pressure measurement and returns the time it will be  
finished.

``gauge_uncomp_temperature(self)``  
Starts the temperature measurement and returns the time it will be  
finished.

``get_uncomp_pressure(self, t_ready)``  
Waits until the pressure measurement is finished, then returns the  
uncompensated temperature.

``get_uncomp_temperature(self, t_ready)``  
Waits until the temperature measurement is finished, then returns the  
uncompensated temperature.

``pressure(self)``  
Measures and returns the compensated pressure.

``temperature(self)``  
Measures and returns the compensated temperature.

``uncomp_pressure(self)``  
Measures and returns the uncompensated pressure.

``uncomp_temperature(self)``  
Measures and returns the uncompensated temperature.

Instance variables
------------------
``chip_id``  
ID of chip is hardcoded on the sensor.

``oversample_sett``  
Sets the accuracy.
* 0 lowest accuracy, fastest
* 1
* 2
* 3 highest accuracy, slowest

``pressure_MSL``  
Pressure at Main Sea Level. The default is 101325 Pa, but you can use your local QNH in Pa.


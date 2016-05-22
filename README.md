micropython-bmp180
==================

Module bmp180
-----------------
bmp180 is a micropython module for the Bosch BMP180 sensor. It measures
temperature as well as pressure, with a high enough resolution to calculate
altitude.  
Breakoutboard: http://www.adafruit.com/products/1603  
data-sheet: http://ae-bst.resource.bosch.com/media/products/dokumente/bmp180/BST-BMP180-DS000-09.pdf

If you have any questions, open an issue.

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
from bmp180 import *
from altimeter import altitude

bmp180 = BMP180()
bmp180.config(oversample=2)

bmp180.measure()

temp = bmp180.get_fixedp(TEMPERATURE)
p = bmp180.get_float(PRESSURE)
alt = altitude(p, 101325)
```

Classes
-------
``BMP180``  
Module for the BMP180 pressure sensor.  
![UML diagramm](https://raw.githubusercontent.com/turbinenreiter/micropython-bmp180/master/classes_BMP180.png "UML diagramm")


Methods
--------------

``config(i2c, oversample)``  
Configure the sensor.  

``measure()``  
Initiates a blocking measurement.  

``get_fixedp(VALUE)``  
Returns VALUE as int.  

``get_float(VALUE)``  
Returns VALUE as float.  

Instance variables
------------------
``chip_id``  
ID of chip is hardcoded on the sensor.

``oversample_sett``  
Sets the accuracy. Default: 0  
* 0 lowest accuracy, fastest
* 1
* 2
* 3 highest accuracy, slowest

Modules
-------
``altimeter``  
Provides a function to calculate altitude from pressure.

Functions
---------

``altitude(pressure, baseline)``  
Input in Pa.  
Altitude in m.  
Baseline is the pressure at Main Sea Level. The default is 101325 Pa, but you can use your local QNH in Pa.  
To get different altitudes, use this as baselines:

| altitude |       baseline |  
|:--------:|:--------------:|  
| absolute | local pressure |  
| true     |        QNH*100 |  
| pressure | 101325 or None |  


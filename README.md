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
from bmp180 import BMP180
bmp180 = BMP180()
bmp180.oversample_sett = 2
bmp180.baseline = 101325

bmp180.measure_blocking()

temp = bmp180.get_fixedp(bmp180.TEMPERATURE)
p = bmp180.get_float(bmp180.PRESSURE)
altitude = bmp180.altitude()
```

Classes
-------
``BMP180``  
Module for the BMP180 pressure sensor.  
![UML diagramm](https://raw.githubusercontent.com/turbinenreiter/micropython-bmp180/master/classes_BMP180.png "UML diagramm")


Methods
--------------

``measure()``
Initiates a non-blocking measurement.  

``measure_blocking()``  
Initiates a blocking measurement.

``get_fixedp(VALUE)``  
Returns VALUE as int.  

``get_float(WHAT)``  
Returns VALUE as float.  

``altitude``  
Altitude in m.  


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

``baseline``  
Pressure at Main Sea Level. The default is 101325 Pa, but you can use your local QNH in Pa.  
To get different altitudes, use this as baselines:

| altitude |       baseline |  
|:--------:|:--------------:|  
| absolute | local pressure |  
| true     |        QNH*100 |  
| pressure | 101325 or None |  


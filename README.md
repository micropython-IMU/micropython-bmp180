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
from machine import I2C, Pin                        # create an I2C bus object accordingly to the port you are using
bus = I2C(1, baudrate=100000)           # on pyboard
# bus =  I2C(scl=Pin(4), sda=Pin(5), freq=100000)   # on esp8266
bmp180 = BMP180(bus)
bmp180.oversample_sett = 2
bmp180.baseline = 101325

temp = bmp180.temperature
p = bmp180.pressure
altitude = bmp180.altitude
print(temp, p, altitude)
```

Important Notice:  
Make sure to either use this in fast loops or call gauge() in fast loops to make sure to always get current values. If you call pressure() once and then again 10 seconds later, it will report a 10 seconds old value. Look at the gauge() function in the source to understand this. Alternatively use the blocking_read() method.

Classes
-------
``BMP180``  
Module for the BMP180 pressure sensor.  
![UML diagramm](https://raw.githubusercontent.com/turbinenreiter/micropython-bmp180/master/classes_BMP180.png "UML diagramm")


Methods
--------------

``compvaldump()``
Returns a list of all compensation values.  

``gauge()``  
Generator refreshing the measurements. Does not need to be called manually.

``temperature``  
Nonblocking read of temperature in degree C.  

``pressure``  
Nonblocking read of pressure in Pascal (divide result by 100 for millibar/hP).  

``blocking_read()``  
Trigger a read and wait until data is available.  

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


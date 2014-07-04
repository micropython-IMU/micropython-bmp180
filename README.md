micropython-bmp180
==================

micropython-bmp180 is a module for micropython which provides a class for the BMP180 pressure sensor.

Breakoutboard: http://www.adafruit.com/products/1603
data-sheet: http://ae-bst.resource.bosch.com/media/products/dokumente/bmp180/BST-BMP180-DS000-09.pdf

## Wiring the sensor to the pyboard

| pyboard| bmp180 |
|--------|--------|
| VIN    | VIN    |
| 3V3    | 3Vo    |
| GND    | GND    |
| SCL    | SCL    |
| SDA    | SDA    |

## Using the module

create the class
```python
from bmp180 import BMP180
bmp180 = BMP180()
```

```bmp180.oss``` is the paramater for accuracy and speed. 0 gives you the lowest accuracy at the highest speed, 3 gives you the highest accuracy at the lowest speed.

```bmp180.UT()``` returns the uncompensated temperature.  
```bmp180.UP()``` returns the uncompenstaed pressure.  
```bmp180.T()``` returns the temperature in °C.  
```bmp180.B5()``` returns the temperature-specific compensation value for calculating the compensated pressure.  
```bmp180.p()``` returns the pressure in Pa.  

```bmp180.baseline(dt)``` returns the mean of pressure measurements taken within ```dt``` milliseconds.  

```bmp180.altitude_above_ref(p_ref)``` returns the altitude relative to ```p_ref```. The pressure level passed is altitude 0.  
```bmp180.altitude_abs(baseline)``` same as ```altitude_above_ref```, but if no ```baseline``` passed uses ```baseline(1000)``` as reference.  
```bmp180.altitude_true(QNH)``` returns true altitude, pass local QNH in Pa as ```QNH```.  
```bmp180.altitude_pressure()``` returns pressure altitude relative to QNH = 1013.25hPA




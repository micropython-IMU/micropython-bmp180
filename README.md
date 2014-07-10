micropython-bmp180
==================

micropython-bmp180 is a module for micropython which provides a class for the BMP180 pressure sensor.

Breakoutboard: http://www.adafruit.com/products/1603  
data-sheet: http://ae-bst.resource.bosch.com/media/products/dokumente/bmp180/BST-BMP180-DS000-09.pdf

## Wiring the sensor to the pyboard

| pyboard| bmp180 |
|:------:|:------:|
| VIN    | VIN    |
| 3V3    | 3Vo    |
| GND    | GND    |
| SCL    | SCL    |
| SDA    | SDA    |

## Using the module

create the class:
```python
from bmp180 import BMP180
bmp180 = BMP180()
```

```bmp180.oss``` is the paramater for accuracy and speed. 0 gives you the lowest accuracy at the highest speed, 3 gives you the highest accuracy at the lowest speed.

```bmp180.T()``` returns the temperature in °C.  
```bmp180.p()``` returns the pressure in Pa.  

```bmp180.baseline(dt)``` returns the mean of pressure measurements taken within ```dt``` milliseconds.  

```bmp180.altitude_above_ref(p_ref)``` returns the altitude relative to ```p_ref``` in m. The pressure level passed is altitude 0. Pass ```baseline``` to geht absolute altitude, local ```QNH``` in Pa to get true altitude or ```101325``` Pa fpr pressure altitude.

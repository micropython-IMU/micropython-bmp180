Module bmp180
-----------------
bmp180 is a micropython module for the Bosch BMP180 sensor. It measures
temperature as well as pressure, with a high enough resolution to calculate
altitude.

Classes
-------
BMP180 
Module for the BMP180 pressure sensor.


Methods
--------------


```altitude_above_ref(self, pressure, pressure_ref=None)```  
    Calculates and returns the altitude relative to a reference pressure.  
    For:             use:  
        absolute        pressure_ref = baseline  
        true            pressure_ref = QNH*100  
        pressure        pressure_ref = 101325  

```baseline(self, dt=None)```  
    Measures the pressure for a given time and returns the mean of the  
    measurements.

```calc_pressure(self, uncomp_temperature, uncomp_pressure)```  
    Calculates and returns the compensated pressure.

```calc_temperature(self, uncomp_temperature)```  
    Calculates and returns the compensted temperature.

```gauge_uncomp_pressure(self)```  
    Starts the pressure measurement and returns the time it will be  
    finished.

```gauge_uncomp_temperature(self)```  
    Starts the temperature measurement and returns the time it will be  
    finished.

```get_uncomp_pressure(self, t_ready)```  
    Waits until the pressure measurement is finished, then returns the  
    uncompensated temperature.

```get_uncomp_temperature(self, t_ready)```  
    Waits until the temperature measurement is finished, then returns the  
    uncompensated temperature.

```pressure(self)```  
    Measures and returns the compensated pressure.

```temperature(self)```  
    Measures and returns the compensated temperature.

```uncomp_pressure(self)```  
    Measures and returns the uncompensated pressure.

```uncomp_temperature(self)```  
    Measures and returns the uncompensated temperature.

Instance variables
------------------
```chip_id```
    ID of chip is hardcoded on the sensor.

```oversample_sett```
    Sets the accuracy.
    * 0 lowest accuracy, fastest
    * 1
    * 2
    * 3 highest accuracy, slowest

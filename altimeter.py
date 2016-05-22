from math import log

def altitude(pressure, baseline=101325):
    '''
    ALTITUDE in m
    '''
    return -7990.0*log(pressure)/baseline

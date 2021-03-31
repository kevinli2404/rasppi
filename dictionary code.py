#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Can enable debug output by uncommenting:
#import logging
#logging.basicConfig(level=logging.DEBUG)

import time
import numpy as np
import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
import matplotlib.pyplot as plt
import scipy as sp

# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0


# Uncomment one of the blocks of code below to configure your Pi or BBB to use
# software or hardware SPI.

# Raspberry Pi software SPI configuration.
CLK = 25
CS  = 24
DO  = 18
sensor = MAX31855.MAX31855(CLK, CS, DO)

# Raspberry Pi hardware SPI configuration.
#SPI_PORT   = 0
#SPI_DEVICE = 0
#sensor = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# BeagleBone Black software SPI configuration.
#CLK = 'P9_12'
#CS  = 'P9_15'
#DO  = 'P9_23'
#sensor = MAX31855.MAX31855(CLK, CS, DO)

# BeagleBone Black hardware SPI configuration.
#SPI_PORT   = 1
#SPI_DEVICE = 0
#sensor = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
results={}
run = int(input("how many compositions to test?"))
r=0
while (r<run): 
    comp = input("Enter Composition (%)")
# Loop printing measurements every second.
    print('Press Ctrl-C to quit.')
    store=list()
    rest=0
    while (sensor.readTempC()) < 30:
        temp = sensor.readTempC()
        tups=(rest,temp)
        store.append(tups)
        internal = sensor.readInternalC()
        time.sleep(1.0)
        rest+=1
        print(store)
    x,y=zip(*store)
##ones= [1]*len(y)
    y =np.asarray(y)
    
    from scipy.interpolate import UnivariateSpline
    threshold = 0.1
    m = len(y)
    x = np.arange(m)
    s = m
    max_error = 1
    while max_error > threshold: 
      spl = UnivariateSpline(x, y, k=1, s=2)
      interp_y = spl(x)
      max_error = np.max(np.abs(interp_y - y))
      s /= 2
    knots = spl.get_knots()
    values = spl(knots)

    ts = knots.size
    idx = np.arange(ts)
    changes = []
    for j in range(1, ts-1):
      spl = UnivariateSpline(knots[idx != j], values[idx != j], k=1, s=0)
      if np.max(np.abs(spl(x) - interp_y)) > 2*threshold:
        changes.append(knots[j])
    plt.plot(y)
    plt.plot(changes, y[np.array(changes, dtype=int)], 'ro')
    plt.xlabel('time')
    plt.ylabel('temp')
    plt.show()
##print(len(changes))
##print(y)

    temps=[]
    for i in range (len(changes)):
    
    ##j=store.index(changes[i-1])
        print(changes[i-1])
        print(y[int(changes[i-1])])
        temps.append(y[int(changes[i-1])])
    ##temps.append(store[j][1])
    
    results[comp]= temps
##results[comp]=y(changes)

    r+=1


print(results)



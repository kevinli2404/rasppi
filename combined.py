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

# Raspberry Pi software SPI configuration.
CLK = 25
CS  = 24
DO  = 18
sensor = MAX31855.MAX31855(CLK, CS, DO)



results={} #the dictionary that will store composition and locations of gradient change
run = int(input("how many compositions to test?"))#determining how many compositions to test
r=0

#This code will run for each composition. It will record temperature time data from the thermocouple and figure out location of gradient changes
while (r<run): 
    comp = input("Enter Composition (%)") #user enters composition

    print('Press Ctrl-C to quit.') 
    store=list()
    rest=0 #initiate time variable
    while (sensor.readTempC()) < 32: #measuring temperatures from melt to 70 degrees C
        temp = sensor.readTempC()
        tups=(rest,temp)
        store.append(tups) #storing time and temperature
        time.sleep(1.0)
        rest+=1
        print(tups)
        
    x,y=zip(*store) #breaking time and temperature into two separate lists
    
    #using linear interpolation to figure out where changes of gradient occur
    y =np.asarray(y)
    from scipy.interpolate import UnivariateSpline
    threshold = 0.1
    m = len(y)
    x = np.arange(m)
    s = m
    max_error = 1
    while max_error > threshold: 
      spl = UnivariateSpline(x, y, k=1, s=s)
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
    for i in range (2):
    
    ##j=store.index(changes[i-1])
        print(changes[i])
        print(y[int(changes[i])])
        temps.append(y[int(changes[i])])
    ##temps.append(store[j][1])
    
    results[comp]= temps
##results[comp]=y(changes)
    r+=1
print(results)

##import matplotlib.pyplot as plt
##import numpy as np

##dict={'10': [214, 200], '20': [196,170], '30': [178,140],'50': [142,110],'60': [170,110],'70': [230,110]}
eut=56
eutemp=140
##print(dict)
##print(len(dict))
xc,yt=zip(*results.items())
xc=list(xc)
#yt=list(yt)
#print(yt)
#yt=yt[0][:2]
print(yt)
#yt=tuple(yt)
print(type(yt))
xc=[float(item) for item in xc]
yt1,yt2=zip(*yt)
yt1,yt2=list(yt1),list(yt2)
##print(xc,yt1,yt2)
##print(type(xc),type(yt1))
xc1=[]
xc3=[]
xc2=[]
ytt1=[]
ytt2=[]
ytt3=[]
for i in range(len(xc)):
    test=xc[i]
    print(xc[i],i)
    if xc[i]<56:
        xc1.append(xc[i]),ytt1.append(yt1[i]),ytt2.append(yt2[i])
    else:
        xc3.append(xc[i]),ytt3.append(yt1[i])
        
        
print(xc1,ytt1,ytt2,xc3,ytt3)
##adding in the points we know ie melting points and composition of pure and eutectic to each curve.
xc1.insert(0,0),xc1.append(56),xc3.insert(0,56),xc3.append(100)
ytt1.insert(0,227),ytt1.append(eutemp),ytt2.insert(0,227),ytt2.append(eutemp),ytt3.insert(0,eutemp),ytt3.append(267)
print(xc1,ytt1,ytt2,xc3,ytt3)
xc2=xc1


cf1,cf2,cf3=np.polyfit(xc1,ytt1,2),np.polyfit(xc2,ytt2,2),np.polyfit(xc3,ytt3,2)
p1,p2,p3=np.poly1d(cf1),np.poly1d(cf2),np.poly1d(cf3)


x1,x2,x3=np.linspace(xc1[0],xc1[-1]),np.linspace(xc2[0],xc2[-1]),np.linspace(xc3[0],xc3[-1])
y1,y2,y3=p1(x1),p2(x2),p3(x3)

yy2=[]
xx2=[]
for i in range(len(x2)):
    test=y2[i]
    if y2[i]>eutemp:
        xx2.append(x2[i]),yy2.append(y2[i])
xh=xx2[-1]
xh1=np.linspace(xh,100)
yh=[eutemp]*len(xh1)


plt.xlim(0,100)
plt.ylim(50,300)
plt.scatter(xc1,ytt1)
plt.scatter(xc2,ytt2)
plt.scatter(xc3,ytt3)
plt.plot(x1,y1)
plt.plot(xx2,yy2)
plt.plot(x3,y3)
plt.plot(xh1,yh)
plt.show()



            


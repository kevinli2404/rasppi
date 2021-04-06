#this code utilises the Adafruit_Python_MAX31855 library which is used to read the temperature of the thermocouple. Only selected parts have been utilised. 
#The complete code can be found at
#https://github.com/adafruit/Adafruit_Python_MAX31855

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



results={} #the dictionary that will store composition and two locations of gradient change
run = int(input("how many compositions to test?")) #determining how many compositions to test
r=0 #indexing which run is currently happening

#This code will run for each composition. It will record temperature time data from the thermocouple and figure out location of gradient changes
while (r<run): 
    comp = input("Enter Composition (%)") #user enters composition

    print('Press Ctrl-C to quit.') #ctrl-c can be used to quit if the set up is wrong. 
    store=list() #initiating the storage of a list of tuples that store temperature-time data. 
    rest=0 #initiate time variable
    while (sensor.readTempC()) > 70: #measuring temperatures from melt to 70 degrees C
        temp = sensor.readTempC()
        tups=(rest,temp)
        store.append(tups) #storing time and temperature
        time.sleep(1.0) #wait 1 second between readings. This can be amended for more granular data. 
        rest+=1 #counter used to assign a time variable for each temperature.
        #print(tups)
        
    x,y=zip(*store) #breaking time and temperature into two separate lists
    
    #using piecewise linera fit in order to determine where gradient changes occur
    #the variables can be adjusted in order to change sensitivity of gradient change. 
    #code extracted from https://stackoverflow.com/questions/47519626/using-numpy-scipy-to-identify-slope-changes-in-digital-signals
    y =np.asarray(y)
    from scipy.interpolate import UnivariateSpline
    threshold = 0.1 #this is the parameter to change to affect the sensitivity of gradient changes
    m = len(y)
    x = np.arange(m)
    s = m
    max_error = 1
    while max_error > threshold: 
      spl = UnivariateSpline(x, y, k=1, s=s) #fits a straight line through a few points
      interp_y = spl(x)
      max_error = np.max(np.abs(interp_y - y))
      s /= 2
    knots = spl.get_knots()
    values = spl(knots) #gets the locations of each of the gradient changes
    
    #test the importance of each knot, ie does the gradient change sufficiently at each point
    #removes each knot in turn and then checks the effect on the error if it is removed. 
    ts = knots.size
    idx = np.arange(ts)
    changes = []
    for j in range(1, ts-1):
      spl = UnivariateSpline(knots[idx != j], values[idx != j], k=1, s=0)
      if np.max(np.abs(spl(x) - interp_y)) > 2*threshold:
        changes.append(knots[j])
        
    #plotting a graph of the recorded temperature time data
    #marking the locations of the knots.
    plt.plot(y)
    plt.plot(changes, y[np.array(changes, dtype=int)], 'ro')
    plt.xlabel('time')
    plt.ylabel('temp')
    plt.show()

    #recording the temperature of the two gradient changes
    temps=[]
    for i in range (2): #making sure that only 2 are selected, prevents issues later on
        temps.append(y[int(changes[i])]) #append the temperature of the change instead of the saved time
    results[comp]= temps
    r+=1 #move onto the next composition. 
print(results) #print the dictionary of compositions and the value - a tuple of two temperatures. 

#set of test data used to check the fit. 
#dict={'10': [214, 200], '20': [196,170], '30': [178,140],'50': [142,110],'60': [170,110],'70': [230,110]} 

#set the temperature and composition of the eutectic point - so applicable to other systems. 
eut=56
eutemp=140

xc,yt=zip(*results.items()) #split the composition and tempeature results. 
xc=list(xc) #change the data type of xc to a list.

xc=[float(item) for item in xc] #change composition results from string into float. 
yt1,yt2=zip(*yt) #split the tuple of temperatures into two separate lists. 
yt1,yt2=list(yt1),list(yt2)

xc1, xc2, xc3, ytt1, ytt2, ytt3  = ([] for i in range(6))

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



            



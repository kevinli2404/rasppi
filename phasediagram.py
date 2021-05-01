import matplotlib.pyplot as plt
import numpy as np

dict={'10': [214, 200], '20': [196,170], '30': [178,140],'50': [142,110],'60': [170,110],'70': [230,110]}
eut=56
eutemp=140
##print(dict)
##print(len(dict))
xc,yt=zip(*dict.items())
xc=list(xc)
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
    #print(xc[i],i)
    if xc[i]<56:
        xc1.append(xc[i]),ytt1.append(yt1[i]),ytt2.append(yt2[i])
    else:
        xc3.append(xc[i]),ytt3.append(yt1[i])
        
        
#print(xc1,ytt1,ytt2,xc3,ytt3)
##adding in the points we know ie melting points and composition of pure and eutectic to each curve.
xc1.insert(0,0),xc1.append(56),xc3.insert(0,56),xc3.append(100)
ytt1.insert(0,227),ytt1.append(140),ytt2.insert(0,227),ytt2.append(140),ytt3.insert(0,140),ytt3.append(267)
#print(xc1,ytt1,ytt2,xc3,ytt3)
xc2=xc1


cf1,cf2,cf3=np.polyfit(xc1,ytt1,2),np.polyfit(xc2,ytt2,2),np.polyfit(xc3,ytt3,2)
p1,p2,p3=np.poly1d(cf1),np.poly1d(cf2),np.poly1d(cf3)


x1,x2,x3=np.linspace(xc1[0],xc1[-1]),np.linspace(xc2[0],xc2[-1]),np.linspace(xc3[0],xc3[-1])
y1,y2,y3=p1(x1),p2(x2),p3(x3)

yy2=[]
xx2=[]
for i in range(len(x2)):
    test=y2[i]
    if y2[i]>140:
        xx2.append(x2[i]),yy2.append(y2[i])
xh=xx2[-1]
xh1=np.linspace(xh,100)
yh=[140]*len(xh1)


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



            

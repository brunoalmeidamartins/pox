#!/usr/bin/python
# -*- coding: UTF-8 -*-

import matplotlib.pyplot as plt
import commands
import time

i=0
tempo=600
x=list()
y11tx=list()
y11rx=list()
y12tx=list()
y12rx=list()
y14tx=list()
y14rx=list()

plt.ion() #Turn interactive mode on
fig,(ax11,ax12,ax14)=plt.subplots(3,sharex=True,sharey=True)

fig.suptitle('Taxa de Pacotes - Switch 3',fontsize=18)
ax11.set_title('Interface eth11',fontsize=14)
ax12.set_title('Interface eth12',fontsize=14)
ax14.set_title('Interface eth14',fontsize=14)
plt.xlabel('Tempo(s)',fontsize=14)
ax11.set_ylabel('Tx. Pacotes',fontsize=14)
ax12.set_ylabel('Tx. Pacotes',fontsize=14)
ax14.set_ylabel('Tx. Pacotes',fontsize=14)
ax11.grid()
ax12.grid()
ax14.grid()
plt.axis([0,tempo,0,10000])

while i<tempo:
    tx11=int(commands.getoutput("ovs-ofctl dump-ports s3 11 | grep tx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    rx11=int(commands.getoutput("ovs-ofctl dump-ports s3 11 | grep rx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    tx12=int(commands.getoutput("ovs-ofctl dump-ports s3 12 | grep tx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    rx12=int(commands.getoutput("ovs-ofctl dump-ports s3 12 | grep rx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    tx14=int(commands.getoutput("ovs-ofctl dump-ports s3 14 | grep tx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    rx14=int(commands.getoutput("ovs-ofctl dump-ports s3 14 | grep rx | awk -F= '{print $2}' | awk -F, '{print $1}'"))

    x.append(i)
    y11tx.append(tx11)
    y11rx.append(rx11)
    y12tx.append(tx12)
    y12rx.append(rx12)
    y14tx.append(tx14)
    y14rx.append(rx14)

    #ax11.scatter(i,tx11,c='r')
    #ax11.scatter(i,rx11,c='g')
    #ax12.scatter(i,tx12,c='r')
    #ax12.scatter(i,rx12,c='g')
    #ax14.scatter(i,tx14,c='r')
    #ax14.scatter(i,rx14,c='g')

    ax11.plot(x,y11tx,'r-',label='TX')
    ax11.plot(x,y11rx,'g-',label='RX')
    ax12.plot(x,y12tx,'r-',label='TX')
    ax12.plot(x,y12rx,'g-',label='RX')
    ax14.plot(x,y14tx,'r-',label='TX')
    ax14.plot(x,y14rx,'g-',label='RX')

    if i==0:
        ax11.legend(loc='upper left',fontsize=12)
        ax12.legend(loc='upper left',fontsize=12)
        ax14.legend(loc='upper left',fontsize=12)

    plt.show()
    plt.pause(0.0001) #If there is an active figure it will be updated and displayed, and the GUI event loop will run during the pause
    i+=1  
    time.sleep(1)

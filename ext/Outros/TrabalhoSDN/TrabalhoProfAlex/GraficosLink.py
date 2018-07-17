import matplotlib.pyplot as plt
import commands
import time

i = 0
tempo =600

x=list()
y1 = list()
y2 = list()
y3 = list()
y4 = list()
y5 = list()
y6 = list()

plt.ion() #Turn interactive mode on

fig = plt.figure()
rect = fig.patch
rect.set_facecolor('#31312e')

ax1 = fig.add_subplot(1,1,1, axisbg='grey')

tx311_aux = tx314_aux = tx312_aux = tx211_aux = tx214_aux = tx114_aux = 0 #Guarda Valores Anteriores
rx311_aux = rx314_aux = rx312_aux = rx211_aux = rx214_aux = rx114_aux = 0 #Guarda Valores Anteriores


while i <tempo:
    #S3 {1,6,2}
    tx311=int(commands.getoutput("ovs-ofctl dump-ports s3 11 | grep tx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    rx311=int(commands.getoutput("ovs-ofctl dump-ports s3 11 | grep rx | awk -F= '{print $2}' | awk -F, '{print $1}'"))

    tx314=int(commands.getoutput("ovs-ofctl dump-ports s3 14 | grep tx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    rx314=int(commands.getoutput("ovs-ofctl dump-ports s3 14 | grep rx | awk -F= '{print $2}' | awk -F, '{print $1}'"))

    tx312=int(commands.getoutput("ovs-ofctl dump-ports s3 12 | grep tx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    rx312=int(commands.getoutput("ovs-ofctl dump-ports s3 12 | grep rx | awk -F= '{print $2}' | awk -F, '{print $1}'"))

    #s2 {4,3}
    tx211=int(commands.getoutput("ovs-ofctl dump-ports s2 11 | grep tx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    rx211=int(commands.getoutput("ovs-ofctl dump-ports s2 11 | grep rx | awk -F= '{print $2}' | awk -F, '{print $1}'"))

    tx214=int(commands.getoutput("ovs-ofctl dump-ports s2 14 | grep tx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    rx214=int(commands.getoutput("ovs-ofctl dump-ports s2 14 | grep rx | awk -F= '{print $2}' | awk -F, '{print $1}'"))

    #s1 {5}
    tx114=int(commands.getoutput("ovs-ofctl dump-ports s1 14 | grep tx | awk -F= '{print $2}' | awk -F, '{print $1}'"))
    rx114=int(commands.getoutput("ovs-ofctl dump-ports s1 14 | grep rx | awk -F= '{print $2}' | awk -F, '{print $1}'"))

    x.append(i)
    y1.append((tx311-tx311_aux)+(rx311-rx311_aux))
    print((tx311-tx311_aux)+(rx311-rx311_aux))

    y2.append((tx314-tx314_aux)+(rx314-rx314_aux))
    y3.append((tx214-tx214_aux)+(rx214-rx214_aux))
    y4.append((tx211-tx211_aux)+(rx211-rx211_aux))
    y5.append((tx114-tx114_aux)+(rx114-rx114_aux))
    y6.append((tx312-tx312_aux)+(rx312-rx312_aux))


    ax1.plot(x,y1,'c',linewidth=3.3,linestyle='-', label='Link1')
    ax1.plot(x,y2,'red',linewidth=3.3,linestyle='-', label='Link2')
    ax1.plot(x,y3,'green',linewidth=3.3,linestyle='-', label='Link3')
    ax1.plot(x,y4,'blue',linewidth=3.3,linestyle='-', label='Link4')
    ax1.plot(x,y5,'yellow',linewidth=3.3,linestyle='-', label='Link5')
    ax1.plot(x,y6,'orange',linewidth=3.3,linestyle='-', label='Link6')
    #ax1.plot(x1,y1,'r',linewidth=2.5,linestyle='--', label='Teste2')
    if i == 0:
        ax1.legend(loc='upper right') #"upper left" Esqueda Cima

    ax1.tick_params(axis='x', colors='c')
    ax1.tick_params(axis='y', colors='c')
    ax1.spines['bottom'].set_color('w')
    ax1.spines['top'].set_color('w')
    ax1.spines['left'].set_color('w')
    ax1.spines['right'].set_color('w')
    ax1.yaxis.label.set_color('c')
    ax1.xaxis.label.set_color('c')

    ax1.set_title('Links', color='c')
    ax1.set_xlabel('Tempo (s)')
    ax1.set_ylabel('Pacotes')

    plt.show()
    plt.pause(0.0001)
    i+=1
    time.sleep(1)

    tx311_aux = tx311
    tx314_aux = tx314
    tx312_aux = tx312
    tx211_aux = tx211
    tx214_aux = tx214
    tx114_aux = tx114

    rx311_aux = rx311
    rx314_aux = rx314
    rx312_aux = rx312
    rx211_aux = rx211
    rx214_aux = rx214
    rx114_aux = rx114

    #Debug
    #print((tx311-tx311_aux)+(rx311-rx311_aux))
    #print((tx314-tx314_aux)+(rx314-rx314_aux))
    #print((tx214-tx214_aux)+(rx214-rx214_aux))
    #print((tx211-tx211_aux)+(rx211-rx211_aux))
    #print((tx114-tx114_aux)+(rx114-rx114_aux))
    #print((tx312-tx312_aux)+(rx312-rx312_aux))

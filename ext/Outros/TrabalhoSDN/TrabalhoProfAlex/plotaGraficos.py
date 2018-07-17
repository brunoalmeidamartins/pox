import matplotlib.pyplot as plt

x = [100,58,96,75,78,92]
y = [1,2,3,4,5,6]

fig = plt.figure()
rect = fig.patch
rect.set_facecolor("#ffffff")

ax1 = fig.add_subplot(2,3,1)
ax1.plot(x,y,'r')
ax1.set_title('Grafico 1')
ax1.set_xlabel('xlabel')
ax1.set_ylabel('ylabel')

ax2 = fig.add_subplot(2,3,2)
ax2.plot(x,y,'r')
ax2.set_title('Grafico 2')
ax2.set_xlabel('xlabel')
ax2.set_ylabel('ylabel')

ax3 = fig.add_subplot(2,3,3)
ax3.plot(x,y,'r')
ax3.set_title('Grafico 3')
ax3.set_xlabel('xlabel')
ax3.set_ylabel('ylabel')

ax4 = fig.add_subplot(2,3,4)
ax4.plot(x,y,'r')
ax4.set_title('Grafico 4')
ax4.set_xlabel('xlabel')
ax4.set_ylabel('ylabel')

ax5 = fig.add_subplot(2,3,5)
ax5.plot(x,y,'r')
ax5.set_title('Grafico 5')
ax5.set_xlabel('xlabel')
ax5.set_ylabel('ylabel')

ax6 = fig.add_subplot(2,3,6)
ax6.plot(x,y,'r')
ax6.set_title('Grafico 6')
ax6.set_xlabel('xlabel')
ax6.set_ylabel('ylabel')


plt.show()

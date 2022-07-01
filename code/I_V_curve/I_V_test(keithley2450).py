# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 15:52:37 2019

@author: 安藤研究室
"""
#%%
import pyvisa as visa          # PyVISA module, for GPIB comms
import numpy as np    # enable NumPy numerical analysis
import time          # to allow pause between measurements
import os            # Filesystem manipulation - mkdir, paths etc.

import matplotlib.pyplot as plt # for python-style plottting, like 'ax1.plot(x,y)'
import pandas as pd
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
#%%

SaveFiles = True   # Save the plot & data?  Only display if False.

DevName = 'I-V Curve 01' # will be inserted into filename of saved plot
Keithley_GPIB_Addr = 18

CurrentCompliance = 1.0e-3    # compliance (max) current
start = -5.0e-3    # starting value of Voltage sweep
stop = +5.0e-3      # ending value 
numpoints = 10  # number of points in sweep



#%%

# Open Visa connections to instruments
#keithley = visa.GpibInstrument(22)     # GPIB addr 22
rm = visa.ResourceManager()
keithley2450 = rm.get_instrument(  'GPIB::' + str(Keithley_GPIB_Addr)  )


# Setup Keithley for  current loop
#keithley.write("*RST")
#keithley.write("SOUR:FUNC:MODE CURR")  # current source
#keithley.write("SOUR:CURR 0")          # set current to 0
#keithley.write('SENS:FUNC "VOLT"')   
#keithley.write('FORM:ELEM VOLT')
#keithley.write('SENS:VOLT:RANGE 3')
#keithley.write("SENS:VOLT:PROT:LEV " + str(CompVolt))  # set voltage compliance
#keithley.write(":OUTP ON")                             # turn on output
#print "gain keithley initialized ..."
#%%
# Setup electrodes as voltage source
keithley2450.write("*RST")
#print("reset the instrument")
time.sleep(0.5)    # add second between
keithley2450.write(":SOUR:FUNC:MODE VOLT")
#keithley.write(":SENS:CURR:PROT:LEV " + str(CurrentCompliance))
keithley2450.write(":SENS:CURR:RANGE:AUTO 1")   # set current reading range to auto (boolean)
keithley2450.write(":OUTP ON")                    # Output on    

#%%
### START QtApp #####
app = QtGui.QApplication([])            # you MUST do this once (initialize things)
####################
win = pg.GraphicsWindow(title='Signal from serial port') # creates a window
p = win.addPlot(title='Realtime plot')  # creates empty space for the plot in the window
curve = p.plot(symbol='o')

#pg.QtGui.QApplication.exec_()
              # create an empty “plot” (a curve to plot)
#windowWidth = 100                       # width of the window displaying the curve
#Xm = np.linspace(0,0,windowWidth)           # create array that will contain the relevant time series
#ptr = windowWidth
V=-1e-3              
x=[]
y=[]
def update():
   global curve, ptr, x ,y, V
#   Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
   V+=2e-3/100
   keithley2450.write(":SOUR:VOLT " + str(V))
   yvalue = keithley2450.query(":READ? \"defbuffer1\" ,source")
   xvalue =  keithley2450.query(":READ?")       # read line (single value) from the serial port
   x.append(float(xvalue))
   y.append(float(yvalue))
#   Xm[-1] = float(value)                 # vector containing the instantaneous values
#   ptr += 1                              # update x position for displaying the curve
   curve.setData(y,x)                     # set the curve with this data
   curve.setPos(0,float(x[-1]))                   # set x position in the graph to 0
   QtGui.QApplication.processEvents()    # you MUST process the plot now
#pg.QtGui.QApplication.exec_() # you MUST put this at the end
         # set first x position
# Realtime data plot. Each time this function is called, the data display is updated
#def update():
#   global curve, ptr, Xm
#   Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
#   value =  keithley2450.ask(":READ?")       # read line (single value) from the serial port
#   Xm[-1] = float(value)                 # vector containing the instantaneous values
#   ptr += 1                              # update x position for displaying the curve
#   curve.setData(Xm)                     # set the curve with this data
#   curve.setPos(0,ptr)                   # set x position in the graph to 0
#   QtGui.QApplication.processEvents()    # you MUST process the plot now
### MAIN PROGRAM #####
# this is a brutal infinite loop calling your realtime data plot
X=0
while X<100: 
    update()
    X+=1
### END QtApp ####
pg.QtGui.QApplication.exec_() # you MUST put this at the end
#%%
# Loop to sweep voltage
Voltage=[]
Current = []
for V in np.linspace(start, stop, num=numpoints, endpoint=True):
    #Voltage.append(V)
    print("Voltage set to: " + str(V) + " V" )
    keithley2450.write(":SOUR:VOLT " + str(V))
    time.sleep(0.1)    # add second between
    keithley2450.write("SOUR:VOLT:READ:BACK ON")
    data = keithley2450.query(":READ? \"defbuffer1\" ,source")
    data2 = keithley2450.query(":READ?")
#    data1= keithley2450.ask("meas:volt?")#returns string with many values (V, I, ...)
    print(data,data2)

        # remove delimiters, return values into list elements
#    I = eval( answer.pop(1) ) * 1e3     # convert to number
    Current.append(data2)
    
#    vread = eval( answer.pop(0) )
    Voltage.append(data)
    
    #Current.append(  I  )          # read the current
    
    print("--> Current = "+ str(Current[-1]) +'A')   # print last read value
#end for(V)
plt.plot(Voltage,Current,'o',c='b')
    #%%
keithley2450.write(":OUTP OFF")     # turn off

#set to current source, voltage meas
keithley2450.write(":SOUR:FUNC:MODE curr")

keithley2450.write(":SENS:volt:RANGE:AUTO 1")

keithley2450.close()

#%%     ###### Plot #####
I=np.array(Current,dtype=float)*1e+6
V=np.array(Voltage,dtype=float)*1000
plt.plot(V,I,'o-')
plt.title('I-V Curve - ' + DevName)
plt.xlabel('Voltage (mV)')
plt.ylabel('Current (uA)')
if SaveFiles:
    # create subfolder if needed:
    if not os.path.isdir(DevName): os.mkdir(DevName)
    curtime = time.strftime('%Y-%M-%d_%H%M.%S')
    SavePath = os.path.join(DevName, 'I-V Curve - ' + DevName + ' - [' + curtime +']' )
    plt.savefig(  SavePath + '.png'  )
#    data = np.array([Current,Voltage],dtype=float )
#    data1 = pd.DataFrame(data, columns=['Current','Voltage'])
#    np.savetxt( SavePath + '.txt',s3, fmt="%e" )
#    np.savetxt( SavePath + '.txt',data1, fmt="%e", delimiter="\t", header="Current (A)\tVoltage (V)" )
#    np.array(Voltage).tofile(  os.path.join(DevName, 'I-V Voltage - ' + DevName + ' - [' + curtime +'].txt' )  )
#    np.array(Current).tofile(  os.path.join(DevName, 'I-V Current - ' + DevName + ' - [' + curtime +'].txt' )  )
plt.show()
#%%
s1=pd.Series(I,name='Current(pA)')
s2=pd.Series(V,name='Voltage(mV)')
s3=pd.concat([s2,s1],axis=1)
s3.to_csv( SavePath +".csv",index=False)


#fig1.canvas.window().raise_()
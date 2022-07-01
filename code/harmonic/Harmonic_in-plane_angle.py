# %%
from optosigma import GSC01
import pyvisa as visa
import time  
import matplotlib.pyplot as plt 
import pandas as pd 
from scipy import optimize
import matplotlib.cm as cm
import numpy as np
from tqdm import tqdm
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
#%%
port = "COM3"  # depends on your environment
controller = GSC01(port) #default baudrate=9600
#%%
# Return to mechanical origin 
controller.return_origin()
controller.sleep_until_stop()
#%%
def first_set_angle(angle):
    # initialize position
    controller.return_origin()
    controller.sleep_until_stop()
    dif_posi=angle//0.0025 # conversion from angle to pulse (0.0025 [deg/pulse])
    controller.position += dif_posi # move to position
    controller.sleep_until_stop()
    current_posi=controller.position*0.0025
    return current_posi

def dif_angle_move(dif_angle):
    dif_posi = dif_angle//0.0025
    controller.position += dif_posi
    controller.sleep_until_stop()
    current_posi = controller.position*0.0025
    print(current_posi)
    return current_posi

def set_angle(set_angle):
    current_posi = controller.position*0.0025
    if set_angle<=0:
        pass
    dif_angle= set_angle-current_posi
    dif_angle_move(dif_angle)
#%% confirming the address connected to GPIB
rm=visa.ResourceManager() 
print(rm.list_resources())

# %% define measurements mahine
ke_6221 = rm.open_resource(  'GPIB1::12::INSTR'  )
#LI5650 Lock-in-amp
Lamp=rm.open_resource(  'GPIB0::7::INSTR'  )
# %% set the parameter for Keithrlry6221 to generate continuous sine wave
ke_6221.write('*RST')
ke_6221.write('SOUR:WAVE:FUNC SIN')#Select sine wave
ke_6221.write('SOUR:WAVE:FREQ 3.41e2') # Set frequency to 1kHz
ke_6221.write('SOUR:WAVE:AMPL 25e-3') #Set amplitude to 1mA.
ke_6221.write('SOUR:WAVE:OFFS 0') #Set offset to 0mA.
ke_6221.write('SOUR:WAVE:PMAR:STAT ON') #Turn on phase marker.
ke_6221.write('SOUR:WAVE:PMAR 0') #‘ Set phase marker to 0°.
ke_6221.write('SOUR:WAVE:PMAR:OLIN 1') #‘ Use line 1 for phase marker.
ke_6221.write('SOUR:WAVE:RANG BEST')
ke_6221.write('SOUR:WAVE:DUR:TIME INF') #Continuous waveform.
# %% set lock-in amp
Lamp.write(':ROUT A')
Lamp.write('DET SING') # single mode
Lamp.write('FREQ:HARM ON') #Harmonics on
Lamp.write('FREQ:MULT 2') # nth-order harmonics
Lamp.write(':INPut2:TYPE TPOS') # ref signal type
Lamp.write(':CALC1:FORM REAL') # data1->X (Rcos(theta))
Lamp.write(':CALC2:FORM IMAG') # data2->Y (Rsin(theta))
Lamp.write(':CALC3:FORM MLIN') # data3->R
Lamp.write(':CALC4:FORM PHAS') # data4->theta
Lamp.write(':DATA  30') # read Data1, Data2, Data3, Data4
#%%
Lamp.query(':FREQ:MULT?')
# %%
ke_6221.write('SOUR:WAVE:ARM') #‘ Arm waveform.
ke_6221.write('SOUR:WAVE:INIT')# Turn on output, trigger waveform.
#%%
Lamp.write(':CALC1:OFFS:AUTO:ONCE') # setting offset to zero value of  X and Y component
#Lamp.write('PHAS:AUTO:ONCE') # main detector
#%% set PSD
Lamp.write(':INP:OFFS:AUTO:ONCE')
#%% auto set time constant of filter  subscope is FILT2 setting
#Lamp.write('FILT:AUTO:ONCE')
#%% auto set for sensitivity and time constant
Lamp.write(':AUTO:ONCE')
#%%
Lamp.write('PHAS:AUTO:ONCE') # main detector (sub scope is PHAS2)
#%% time constant
Lamp.write('FILT:TCON 300e-3') #100ms
# Dynamic Reserve
Lamp.write('DRES MED') #HIGH, MED, LOW

#%% sensitivity
sens=0.5e-3
Lamp.write('VOLT:AC:RANG %f' %sens)
# %% motion controller
# set origin position
controller.return_origin()
controller.sleep_until_stop()
#%%
dif_angle_move(-350)
#%%
angle=[]
data1=[]
data2=[]
for i in tqdm(np.linspace(0, 350,116),leave= False):
    dif_angle= 3#deg
    dif_pulse=dif_angle//0.0025
    controller.position += dif_pulse # move to position
    controller.sleep_until_stop()
    #Lamp.write('PHAS:AUTO:ONCE') 
    time.sleep(1)
    data=Lamp.query('Fetch?')
    volt = data.split(',')
    X = float(volt[0])
    Y = float(volt[1])
    #print(dif_pulse)
    current_posi=controller.position*0.0025
    #print(current_posi)
    angle.append(current_posi)
    data1.append(X)
    data2.append(Y)
    #print(volt)
#%%
%matplotlib inline
data1 = np.array(data1)
data2 = np.array(data2)
plt.plot(angle,data1*1e+6,'o',markersize=6)
plt.show()
plt.plot(angle,data2*1e+6,'o',markersize=6)
# %%
dif_angle_move(-350)
# %%
def f (x,a,b,c,d,e):
    return np.cos((x-e)/180*np.pi)*(a+b*np.cos(2*(x-d)/180*np.pi))+c
def f1 (x,a,b,c,d):
    return np.cos((x-d)/180*np.pi)*(a+b*np.cos(2*(x-d)/180*np.pi))+c
def f2 (x,a,b,c,d):
    return a*np.cos(2*(x-d)/180*np.pi)+b*x+c
ini=[0.1,0.1,13,1]
param, param_cov=optimize.curve_fit(f2, angle, data1*1e+6,ini,maxfev=12000)
print(param)
#%%
x=np.arange(0,360,0.01)
plt.plot(angle,data1*1e+6,'ok',markersize=6)
plt.plot(x,f2(x,*param),'-r')
plt.show()
angle= np.array(angle)
plt.plot(angle,data1*1e+6-f2(angle,*param),'ok',markersize=6)
#plt.plot(x,np.cos(x/180*np.pi)*(0.5-np.cos(2*x/180*np.pi))+13)


#%%
### START QtApp #####
app = QtGui.QApplication([])            # you MUST do this once (initialize things)
####################
win = pg.GraphicsWindow(title='Signal from serial port') # creates a window
p = win.addPlot(title='Realtime plot')  # creates empty space for the plot in the window
curve = p.plot(symbol='o')


V=-1e-3              
x=[]
y=[]
def update():
   global curve, ptr, x ,y, V
   dif_angle= 5 #deg
   dif_pulse=dif_angle//0.0025
   controller.position += dif_pulse # move to position
   controller.sleep_until_stop()
   #Lamp.write('PHAS:AUTO:ONCE') 
   time.sleep(4)
   data=Lamp.query('Fetch?')
   volt = data.split(',')
   X = float(volt[0])
   #print(dif_pulse)
   current_posi=controller.position*0.0025
   angle.append(current_posi)
   data1.append(X)
#   Xm[-1] = float(value)                 # vector containing the instantaneous values
#   ptr += 1                              # update x position for displaying the curve
   curve.setData(data1,angle)                     # set the curve with this data
   curve.setPos(0,float(angle[-1]))                   # set x position in the graph to 0
   QtGui.QApplication.processEvents()    # you MUST process the plot now

# this is a brutal infinite loop calling your realtime data plot
X=0
while X<100: 
    update()
    X+=1
### END QtApp ####
pg.QtGui.QApplication.exec_() # you MUST put this at the end
# %%

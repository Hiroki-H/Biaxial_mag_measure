#%%
import pyvisa as visa
from optosigma import GSC01
import time  
import matplotlib.pyplot as plt 
import pandas as pd 
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
# %%
keithley2450=rm.open_resource('GPIB0::18::INSTR')
# %% set keithley 2450
current=1e-4 #Ampere
keithley2450.write("*RST")
keithley2450.write(":SOUR:FUNC:MODE CURR")
keithley2450.write(":SOUR:CURR:VLIM 21") #compliance voltage V
keithley2450.write(":SOUR:CURR " + str(current))
keithley2450.write(":OUTP ON") 
#%%


# %% define kethley2182A nanovoltmeter
keithley2182A = rm.open_resource(  'GPIB0::8::INSTR'  )
#%% set keithley2182
#keithley2182A.write("*RST")
keithley2182A.write(":SENSe:VOLTage:NPLCycles 1") # medium
keithley2182A.write(":SENSe:VOLTage:DFILter 0") # digital filter off
# %%


def current_sweep(start, end, datapoints):
    current=[]
    data=[]
    for i in tqdm(np.linspace(start,end,datapoints),leave= False):
        keithley2450.write(":SOUR:CURR %f" %(i*1e-3))
        time.sleep(0.5)
        Volt=float(keithley2182A.query(":SENSe:Data?"))
        current.append(i)
        data.append(Volt)
    keithley2450.write(":SOUR:CURR %f" %0)
    return current, data


def current_sweep2(start, end, datapoints):
    current=[]
    data=[]
    for i in tqdm(np.linspace(start,end,datapoints),leave= False):
        keithley2450.write(":SOUR:CURR %f" %(i*1e-3))
        time.sleep(0.1)
        keithley2450.write(":SOUR:CURR %f" %(100e-6))
        time.sleep(1.5)
        Volt=float(keithley2182A.query(":SENSe:Data?"))
        current.append(i)
        data.append(Volt/100e-6)
    keithley2450.write(":SOUR:CURR %f" %0)
    return current, data
#%%
set_angle(30)
dif_angle_move(0.1)
#%% test switching 
I1,V1= current_sweep(5, -5, 40)
I2,V2= current_sweep(-5, 5, 40)
#%% test switching draw result
I1,I2 = np.array(I1),np.array(I2)
V1,V2 = np.array(V1), np.array(V2)
plt.plot(I1,V1/I1*1e+3,'or-')
plt.plot(I2,V2/I2*1e+3,'ob-')
plt.xlabel('current I (mA)',fontsize=20)
plt.ylabel('$R_{xy} $ (ohm)',fontsize=20)
plt.show()
plt.plot(I1,V1*1e+3,'or-')
plt.plot(I2,V2*1e+3,'ob-')
plt.xlabel('current I (mA)',fontsize=20)
plt.ylabel('$V_{xy} $ (mV)',fontsize=20)
plt.show()
# %%
I1,R1= current_sweep2(10.5, -10.5, 100)
I2,R2= current_sweep2(-10.5, 10.5, 100)

# %%
%matplotlib inline
I1,I2 = np.array(I1),np.array(I2)
V1,V2 = np.array(V1), np.array(V2)
plt.plot(I1,R1,'ob-')
plt.plot(I2,R2,'or-')
plt.xlabel('current I (mA)',fontsize=20)
plt.ylabel('$R_{xy} $ (ohm)',fontsize=20)
plt.show()
# %%
path='./Experiment/20220127/SiO2sub_Ti(1.5)Pt(1.5)Co(0.7)Pt(1.5)Ti(x)SiO2(4)/x=1.5/switching'
Z=[I1,R1,I2,R2]
df_AHE=pd.DataFrame(Z)
df_AHE=df_AHE.transpose()
df_AHE.columns=['current_+ to -(mA)','Resi_+ to -(ohm)','current_- to +(mA)','Resi_- to +(ohm)']
df_AHE.to_csv(path+'/SW_-{:.3f}mT_100uA.csv'.format(100),index=False)
# %%

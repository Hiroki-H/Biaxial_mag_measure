# %%
from optosigma import GSC01
import pyvisa as visa
import time  
import matplotlib.pyplot as plt 
import pandas as pd 
import matplotlib.cm as cm
import numpy as np
from tqdm import tqdm
# %%

#%% confirming the address connected to GPIB
rm=visa.ResourceManager() 
print(rm.list_resources())

# %% define bipolar power supply
adc_OOP = rm.open_resource(  'GPIB0::11::INSTR'  )

# %% set biplor power supply
adc_OOP.write('C,*RST')
adc_OOP.write('M1')  # trigger mode hold
adc_OOP.write('VF')  # voltage output
adc_OOP.write('F2')  # current measurement
adc_OOP.write('SOV0,LMI0.03')  # dc 0V, limit 30mA
adc_OOP.write('OPR') # output on

#%%
adc_IP = rm.open_resource(  'GPIB0::5::INSTR'  )

adc_IP.write('C,*RST')
adc_IP.write('M1')  # trigger mode hold
adc_IP.write('VF')  # voltage output
adc_IP.write('F2')  # current measurement
adc_IP.write('SOV0,LMI0.03')  # dc 0V, limit 30mA
adc_IP.write('OPR') # output on


# %% define measurements mahine
ke_6221 = rm.open_resource(  'GPIB1::12::INSTR'  )
#LI5650 Lock-in-amp
Lamp=rm.open_resource(  'GPIB0::7::INSTR'  )
# %% set the parameter for Keithrlry6221 to generate continuous sine wave
ke_6221.write('*RST')
ke_6221.write('SOUR:WAVE:FUNC SIN')#Select sine wave
ke_6221.write('SOUR:WAVE:FREQ 3.41e2') # Set frequency to 1kHz
ke_6221.write('SOUR:WAVE:AMPL 8e-3') #Set amplitude to 1mA.
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
Lamp.write(':CALC1:OFFS:AUTO:ONCE') # setting offset to zero value of  X and Y component


# %%
ke_6221.write('SOUR:WAVE:ARM') #‘ Arm waveform.
ke_6221.write('SOUR:WAVE:INIT')# Turn on output, trigger waveform.
# %%
#%% time constant
Lamp.write('FILT:TCON 1') #100ms
#%% sensitivity
sens=5e-4
Lamp.write('VOLT:AC:RANG %f' %sens)
#%%
Lamp.write('PHAS:AUTO:ONCE') # main detector (sub scope is PHAS2)
# %%

def AHE_field_IP(start,end,datapoint):
    data1=[]
    data2=[]
    field=[]
    adc_IP.write('SOV%f' % start)
    time.sleep(10)
    for i in range(datapoint):
        slope=(end-start)/datapoint
        V=slope*(i-datapoint//2)
        adc_IP.write('SOV%f' % V)
        #print(kikusui_IP.query("VOLT?"))
        time.sleep(3)
        data=Lamp.query('Fetch?')
        volt = data.split(',')
        X,Y = float(volt[0]),float(volt[1])
        #time.sleep(0.3)
        data1.append(X)
        data2.append(Y)
        field.append(V)
    adc_IP.write('SOV%f' % 0)
    return field, data1,data2
# %%
adc_OOP.write('SOV%f' % 8)
time.sleep(1)
adc_OOP.write('SOV%f' % 0)
time.sleep(1)
field,data1,data2=AHE_field_IP(-8,8,100)
time.sleep(5)
adc_OOP.write('SOV%f' % -8)
time.sleep(1)
adc_OOP.write('SOV%f' % 0)
time.sleep(1)
field2,data3,data4=AHE_field_IP(8,-8,100)
#%%
plt.plot(field,data1,'or')

plt.plot(field2,data3,'ob')
plt.show()
#%%
plt.plot(field,data2,'or')

plt.plot(field2,data4,'ob')
plt.show()
# %%
field=np.array(field)
field2=np.array(field2)
data1=np.array(data1)
data3=np.array(data3)
plt.title('X',fontsize=20)
plt.plot(34.955*field-7.6213,data1*1e+6,'or')
plt.plot(34.955*field2-7.6213,data3*1e+6,'ob')
plt.xlabel('$μ_0H_x$ (mT)',fontsize=20)
plt.ylabel('$V_{2\omega}$ (μV)',fontsize=20)
plt.xlim(-260,260)
plt.show()
# %%
field=np.array(field)
field2=np.array(field2)
data2=np.array(data2)
data4=np.array(data4)
plt.title('Y',fontsize=20)
plt.plot(34.955*field-7.6213,data2*1e+6,'or')
plt.plot(34.955*field2-7.6213,data4*1e+6,'ob')
plt.xlabel('$μ_0H_x$ (mT)',fontsize=20)
plt.ylabel('$V_{2\omega}$ (μV)',fontsize=20)
plt.xlim(-260,260)
plt.show()
# %%

# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 19:03:43 2021

@author: keioa
"""

#%%　imoprt package
import pyvisa as visa
import time    
#%% confirming the address connected to GPIB
rm=visa.ResourceManager() 
print(rm.list_resources())

#%% LI5650 Lock-in-amp
Lamp=rm.open_resource(  'GPIB0::7::INSTR'  )

#%%
print(Lamp.query("*IDN?"))
Lamp.write('*CLS')
#%%
print(Lamp.query(":FETCh?"))
print(Lamp.query(":INP:COUP?"))
print(Lamp.query("DATA?"))
print(Lamp.query(":FORMAT?"))# data format
print(Lamp.query(':INPut:FILTer:NOTCh1:FREQuency?'))

#%%
print(Lamp.write('DET SING'))
print(Lamp.query("DET?"))

#%%
Lamp.write('FREQ:HARM ON')
print(Lamp.query('FREQ:HARM?'))
Lamp.write('FREQ:MULT 1')
print(Lamp.query('FREQ:MULT?'))
#%%
print(Lamp.query('FREQ2?'))
#%%
Lamp.write(':CALC1:FORM REAL')
print(Lamp.query('CALCulate1:FORMat?')) # data1 format
#%%
Lamp.write(':CALC1:MULT 1') #set Expand 
print(Lamp.query(':CALC1:MULT?'))
#%%
Lamp.write(':CALC1:OFFS:AUTO:ONCE') # setting offset to zero value of  X and Y component
Lamp.write(':CALC2:FORM IMAG')
print(Lamp.query('CALCulate2:FORMat?')) # data2 format

#%%
Lamp.write(':CALC3:FORM REAL2')
print(Lamp.query('CALC3:FORM?')) # data3 format
#%%
#Lamp.write(':CALC4:FORM IMAG2')
Lamp.write(':CALC4:FORM PHAS')
print(Lamp.query('CALC4:FORM?')) # data4 format

#%%
Lamp.write('FORM ASC')
print(Lamp.query('FORM?'))
#%% data load 
Lamp.write(':DATA  30')
print(Lamp.query(":DATA?"))
print(Lamp.query('Fetch?'))
a=Lamp.query('Fetch?')
u=list(map(float,a.split(',')))
print(u)
#%%
Lamp.write(':INP:COUP AC')
print(Lamp.query(':INP:COUP?'))



#%% notch filter
Lamp.write('INP:FILT:NOTC1 on')
print(Lamp.query(':INP:FILT:NOTC1?'))
print(Lamp.query(':INP:FILT:NOTC1:FREQ?'))
#%% notch filter second harmonic
Lamp.write('INP:FILT:NOTC2 on')
print(Lamp.query(':INP:FILT:NOTC2?'))

#%% float or ground
Lamp.write(':INP:LOW FLO')
print(Lamp.query('INP:LOW?'))


#%% pSD setting
## always adjust offset on phase
Lamp.write(':INP:OFFS:AUTO ON')
print(Lamp.query(':INP:OFFS:AUTO?'))

##set once
Lamp.write(':INP:OFFS:AUTO:ONCE')
print(Lamp.query(':INP:OFFS:AUTO?'))


#%% INput2(REF)
Lamp.write(':INP2:TYPE SIN') #6221 is TPOS
print(Lamp.query(':INP2:TYPE?'))

#%% set input A or AB or I
Lamp.write(':ROUT A')
print(Lamp.query(':ROUT?'))

#%% REF signal
Lamp.write(':ROUT2 RINP') # RINP: input ref, IOSC: Internal Osci, SINP: signal input
print(Lamp.query(':ROUT2?'))


#%% auto set for sensitivity and time constant
Lamp.write(':AUTO:ONCE')
#%%

print(Lamp.query('DATA?'))

#%% setting dynamic reserve
Lamp.write('DRES HIGH')
print(Lamp.query(':DRES?'))

#%% auto set time constant of filter  subscope is FILT2 setting
Lamp.write('FILT:AUTO:ONCE')
# slope 24dB/oct
Lamp.write('FILT:SLOP 24')
print(Lamp.query('FILT:SLOP?'))

#%% time constant
Lamp.write('FILT:TCON 100e-3') #100ms
print(Lamp.query('FILT:TCON?'))

#%% filter type exponential or moving
Lamp.write('FILT:TYPE MOV')
print(Lamp.query('FILT:TYPE?'))

#%% main scope detector
print(Lamp.query('FREQ?'))
print(Lamp.query('FREQ:MULT?'))
print(Lamp.query('FREQ:HARM?'))

#%%# sub scope 
#print(Lamp.query(':FREQ2?'))
Lamp.write('FREQ2:HARM on ')
print(Lamp.query('FREQ2:HARM?'))

Lamp.write('FREQ2:MULT 2')
print(Lamp.query('FREQ2:MULT?'))


#%% AUTO PHASE set theta=0
Lamp.write('PHAS:AUTO:ONCE') # main detector (sub scope is PHAS2)




#%%
Lamp.write(':INPut2:TYPE TPOS')
Lamp.query(':INPut2:TYPE?')



# %%

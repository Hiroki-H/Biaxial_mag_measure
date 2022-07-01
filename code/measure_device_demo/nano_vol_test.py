# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 11:35:05 2021

@author: keioa
"""


#%%　imoprt package
import pyvisa as visa
import time
#%% confirming the address connected to GPIB
rm=visa.ResourceManager() 
print(rm.list_resources())

#%% nanovoltmeter
Nanov=rm.open_resource(  'GPIB0::8::INSTR'  )
#%%
Nanov.write('*RST')
#%%
print(Nanov.query(':VOLT:RANG?'))
Nanov.write(':VOLT:RANG:AUTO on') # Auto range(channel 1)
print(Nanov.query(':VOLT:RANG?'))
#%% set Rate
print(Nanov.query(':VOLT:NPLC?'))
Nanov.write(':VOLT:NPLC 1') # 1=Medium 5=slow 0.1=Fast
print(Nanov.query(':VOLT:NPLC?'))
#%% set filter (off)
Nanov.write(':VOLT:STAT off')
#%%
print(Nanov.query(':READ?'))
print(Nanov.query(':MEAS:VOLT?'))

#%%
print(Nanov.query(':FETCh?'))
#Nanov.read(':FETC')
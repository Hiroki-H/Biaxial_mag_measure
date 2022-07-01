#%%　imoprt package
import pyvisa as visa
import time  
import matplotlib.pyplot as plt 
import pandas as pd 
import matplotlib.cm as cm
import numpy as np

#%% confirming the address connected to GPIB
rm=visa.ResourceManager() 
print(rm.list_resources())
# %%
# %% define measurements mahine
ke_6221 = rm.open_resource(  'GPIB1::12::INSTR'  )
# %%
ke_6221.write('*RST')
ke_6221.write('SOUR:WAVE:FUNC SIN')#Select sine wave
ke_6221.write('SOUR:WAVE:FREQ 3.41e2') # Set frequency to 1kHz
ke_6221.write('SOUR:WAVE:AMPL 1e-3') #Set amplitude to 1mA.
ke_6221.write('SOUR:WAVE:OFFS 0') #Set offset to 0mA.
ke_6221.write('SOUR:WAVE:PMAR:STAT ON') #Turn on phase marker.
ke_6221.write('SOUR:WAVE:PMAR 0') #‘ Set phase marker to 0°.
ke_6221.write('SOUR:WAVE:PMAR:OLIN 1') #‘ Use line 1 for phase marker.
ke_6221.write('SOUR:WAVE:RANG BEST')
ke_6221.write('SOUR:WAVE:DUR:TIME INF') #Continuous waveform.
# %%
ke_6221.write('SOUR:WAVE:ARM') #‘ Arm waveform.
ke_6221.write('SOUR:WAVE:INIT')# Turn on output, trigger waveform.
# %%
ke_6221.write('SOUR:WAVE:ABOR') #Stop generating waveform
# %%

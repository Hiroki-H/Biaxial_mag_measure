# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 16:40:08 2021

@author: keioa
"""

#%%
import pyvisa as visa      

#%%
rm = visa.ResourceManager()
ke2182A = rm.open_resource(  'GPIB0::8::INSTR'  )
#%%
print(ke2182A.query(":MEASure:VOLTage?"))
#%%
print(ke2182A.query(":SENSe:VOLTage:NPLCycles?"))
ke2182A.write(":SENSe:VOLTage:NPLCycles 1")
print(ke2182A.query(":SENSe:VOLTage:NPLCycles?"))
print(ke2182A.query(":SENSe:Data?"))
#%%
print(ke2182A.query(':READ?'))
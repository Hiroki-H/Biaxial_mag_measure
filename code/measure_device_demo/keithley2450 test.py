# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 12:17:06 2019

@author: 安藤研究室 hiroki hayashi
"""
#%% import package
import pyvisa


#%%
rm=pyvisa.ResourceManager() 
print(rm.list_resources())

#%%
inst=rm.open_resource('GPIB0::18::INSTR')
print(inst.query("*IDN?"))
#%%
print(inst.query("READ?"))
inst.write("system:beeper 1000,1")
#%%
print(inst.query("measure:current?"))
print(inst.query("current:unit?"))
print(inst.query("READ?"))
print(inst.query("measure:volt?"))
print(inst.query("READ?"))
#inst.write("*RST")
#%%
#inst.write("func \"current\"")
#inst.write("sour:func volt")
#inst.query("sour:func?")
inst.write("outp on")
inst.write("sour:func volt")
inst.write("sour:volt 1")
#%%
import numpy
inst.write("outp off")
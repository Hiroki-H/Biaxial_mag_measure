#%%　imoprt package
import pyvisa as visa
import time  
import matplotlib.pyplot as plt 
import pandas as pd 
import matplotlib.cm as cm
import numpy as np
from optosigma import GSC01





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
# %%
set_angle(30)
# %%
dif_angle_move(-10)
# %%

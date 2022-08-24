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


#%% confirming the address connected to GPIB
rm=visa.ResourceManager() 
print(rm.list_resources())

#%%
adc_IP = rm.open_resource(  'GPIB0::5::INSTR'  )

adc_IP.write('C,*RST')
adc_IP.write('M1')  # trigger mode hold
adc_IP.write('VF')  # voltage output
adc_IP.write('F2')  # current measurement
adc_IP.write('SOV0,LMI0.03')  # dc 0V, limit 30mA
adc_IP.write('OPR') # output on

# %% define keithley 2450 current source
keithley2450=rm.open_resource('GPIB0::18::INSTR')
# %% set keithley 2450
current=15e-3 #Ampere
keithley2450.write("*RST")
keithley2450.write(":SOUR:FUNC:MODE CURR")
keithley2450.write(":SOUR:CURR " + str(current))
keithley2450.write(":OUTP ON") 
# %% define kethley2182A nanovoltmeter
keithley2182A = rm.open_resource(  'GPIB0::8::INSTR'  )
#%% set keithley2182
#keithley2182A.write("*RST")
keithley2182A.write(":SENSe:VOLTage:NPLCycles 1") # medium
keithley2182A.write(":SENSe:VOLTage:DFILter 0") # digital filter off
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
# %% motion controller
# set origin position
controller.return_origin()
controller.sleep_until_stop()

#%%

def PHE_SOT(field,current,waittime):
    adc_IP.write('SOV%f' %field)
    time.sleep(5)
    angle=[]
    data_p=[]
    data_m= []
    Diff = []
    for i in tqdm(np.linspace(0, 350,117),leave= False):
        keithley2450.write(":SOUR:CURR %f" %(current*1e-3))
        time.sleep(waittime)
        Ip=float(keithley2450.query("measure:current?"))
        Voltp=float(keithley2182A.query(":SENSe:Data?"))

        keithley2450.write(":SOUR:CURR %f" %(-current*1e-3))
        time.sleep(waittime)
        Im=float(keithley2450.query("measure:current?"))
        Voltm=float(keithley2182A.query(":SENSe:Data?"))
        dif_angle= 3#deg
        dif_pulse=dif_angle//0.0025
        controller.position += dif_pulse # move to position
        controller.sleep_until_stop()
        #Lamp.write('PHAS:AUTO:ONCE') 

        #print(dif_pulse)
        current_posi=controller.position*0.0025
        #print(current_posi)
        angle.append(current_posi)
        data_p.append(Voltp/Ip)
        data_m.append(Voltm/Im)
        Diff.append(Voltp/Ip-Voltm/Im)
    return angle, data_p, data_m, Diff

#%%
dif_angle_move(-2)
#%%
angle,Rp,Rm,Diff=PHE_SOT(6,25,0.5)
dif_angle_move(-352)
# angle1,R1=PHE_SOT(1,-30)
# dif_angle_move(-350)
#%%

#%%
%matplotlib inline
#R1 = np.array(R1)
plt.plot(angle,Rp,'or',markersize=6)
plt.plot(angle,Rm,'ob',markersize=6)
plt.show()
plt.plot(angle,Diff,'ok',markersize=6)
#plt.plot(angle1,R1,'ob',markersize=6)
# %%
path='C:/Users/keioa/OneDrive/デスクトップ/member/hayashi/Experiment/20220819/sub_Pt(5)_Py(5)'
for current in np.linspace(15,25,7):
    angle,Rp,Rm,Diff=PHE_SOT(6,current,1.5)
    dif_angle_move(-352)
    plt.plot(angle,Diff,'ok',markersize=6)
    plt.show()
    cur= [current]*len(Rp)
    Z=[angle,cur,Rp,Rm,Diff]
    df_PHE=pd.DataFrame(Z)
    df_PHE=df_PHE.transpose()
    df_PHE.columns=['angle(deg)','current(mA)','Rp(ohm)','Rm(ohm)', 'Diff (ohm)']
    df_PHE.to_csv(path+'/DPHE_+{:.3f}mT_{:.2f}mA.csv'.format(202,current),index=False)

#%%
for current in np.linspace(14,20,7):
    print(current)
#%%
R2=R-R[0]
R3=R1-R1[0]
#%%
plt.plot(angle,R2,'or',markersize=6)
plt.plot(angle1,R3,'ob',markersize=6)
#%%
plt.plot(angle,R2-R3,'ok',markersize=6)


# %%
def f (x,a,b,c,d,e,ff):
    return a*np.cos((x-d)/180*np.pi)+b*np.cos((x-d)/180*np.pi)*np.cos(2*(x-d)/180*np.pi)+c+e*x+\
        ff*np.sin(2*(x-d)/180*np.pi)
def f1 (x,a,b,c,d):
    return np.cos((x-d)/180*np.pi)*(a+b*np.cos(2*(x-d)/180*np.pi))+c
ini=[0.1,0.1,1,3,90,1]
param, param_cov=optimize.curve_fit(f, angle, (R2-R3)*1e+3,ini,maxfev=12000)
print(param)
#%%
x=np.arange(0,360,0.01)
angle= np.array(angle)
plt.plot(angle,(R2-R3)*1e+3-param[4]*angle,'ok',markersize=6)
plt.plot(x,f(x,*param)-param[4]*x,'-r')
#%%
plt.plot(x,0.692*np.cos(x/180*np.pi))
plt.plot(x,-1.907*np.cos(x/180*np.pi)*np.cos(2*x/180*np.pi))


#%%
dif_angle_move(-2)
#%%　PHE field-dep

def PHE_SOT_field_dep(start_field, end_field, points, current, path,f):
    field_V=[]
    A=[]
    B=[]
    for field in tqdm(np.linspace(start_field, end_field,points),leave=False):
        current_posi=controller.position*0.0025
        if current_posi>0:
            dif_angle_move(-2)
        angle,R=PHE_SOT(field,current)
        dif_angle_move(-350)
        angle1,R1=PHE_SOT(field,-current)
        dif_angle_move(-350)
        angle,R,R1= np.array(angle),np.array(R),np.array(R1)
        ini=[0.1,0.1,1,3,90,1]
        param, param_cov=optimize.curve_fit(f, angle, (R-R1)*1e+3,ini,maxfev=12000)
        print(param)
        x=np.arange(0,360,0.01)
        plt.plot(angle,(R-R1)*1e+3-param[4]*angle,'ok',markersize=6)
        plt.plot(x,f(x,*param)-param[4]*x,'-r')
        plt.show()
        field_V.append(field)
        A.append(param[0])
        B.append(param[1])
        Z=[angle,R,angle1,R1]
        df_PHE=pd.DataFrame(Z)
        df_PHE=df_PHE.transpose()
        df_PHE.columns=['angle(deg)_+_I','Resi(ohm)_+_I','angle(deg)_-_I','Resi(ohm)_-_I']
        df_PHE.to_csv(path+'/PHE_+{:.3f}mA_+{:.3f}V.csv'.format(current,field),index=False)
    return field_V, A, B


#%%
#%% IV measurement for elctric field
I_s=[]
V_s=[]
for i in tqdm(np.linspace(-40,40,80), leave=False):
    keithley2450.write(":SOUR:CURR " + str(i*1e-3))
    time.sleep(1)
    I=float(keithley2450.query("measure:current?"))
    V=float(keithley2450.query("measure:volt?"))
    I_s.append(I)
    V_s.append(V)
data_e=[I_s,V_s]
df_data=pd.DataFrame(data_e)
df_data=df_data.transpose()
df_data.columns=['measure_current(A)','measure_volt(V)']

df_data.to_csv(path+'/current_vs_voltage_for_electric_field.csv',index=False)

keithley2450.write(":SOUR:CURR 0")
keithley2450.write(":OUTP OFF") 


#################
## AHE for DPHE measurements
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
def AHE_field(start,end,datapoint):
    data=[]
    field=[]
    adc_OOP.write('SOV%f' % start)
    time.sleep(10)
    for i in range(datapoint):
        slope=(end-start)/datapoint
        V=slope*(i-datapoint//2)
        adc_OOP.write('SOV%f' % V)
        #print(kikusui_IP.query("VOLT?"))
        I=float(keithley2450.query("measure:current?"))
        Volt=float(keithley2182A.query(":SENSe:Data?"))
        #time.sleep(0.3)
        data.append(Volt/I)
        field.append(V)
    adc_OOP.write('SOV%f' % 0)
    return field, data
#%%
field,data =AHE_field(-8, 8, 1000)
field2,data2 =AHE_field(8, -8, 1000)

#%%
plt.plot(field,data, 'or')
plt.plot(field2,data2, 'ob')
plt.show()
#%%
Z=[field,data,field2,data2]
df_AHE=pd.DataFrame(Z)
df_AHE=df_AHE.transpose()
df_AHE.columns=['field_- to +','Resi_- to +(ohm)','field_+ to -','Resi_+ to -(ohm)']
df_AHE.to_csv(path+'/AHE_{:.2f}mA_-start.csv'.format(1),index=False)

# %%

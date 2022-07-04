#%%　imoprt package
import pyvisa as visa
import time  
import matplotlib.pyplot as plt 
import pandas as pd 
import matplotlib.cm as cm
import numpy as np
from tqdm import tqdm
from optosigma import GSC01


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

# %% define keithley 2450 current source
keithley2450=rm.open_resource('GPIB0::18::INSTR')
# %% set keithley 2450
current=1e-4 #Ampere
keithley2450.write("*RST")
keithley2450.write(":SOUR:FUNC:MODE CURR")
keithley2450.write(":SOUR:CURR:VLIM 10") #compliance voltage V
keithley2450.write(":SOUR:CURR " + str(current))
keithley2450.write(":OUTP ON") 
# %% define kethley2182A nanovoltmeter
keithley2182A = rm.open_resource(  'GPIB0::8::INSTR'  )
#%% set keithley2182
#keithley2182A.write("*RST")
keithley2182A.write(":SENSe:VOLTage:NPLCycles 1") # medium
keithley2182A.write(":SENSe:VOLTage:DFILter 0") # digital filter off

#%% current change
# current=-7e-3 #Ampere
# keithley2450.write(":SOUR:CURR " + str(current))
# keithley2450.write(":OUTP ON") 

#%% 
def AMR_field(start,end,datapoint):
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
for i in tqdm(range(1),desc='measurement',leave = False):
    print('{}回目'.format(i))
    field,data=AMR_field(-8,8,100)
    time.sleep(5)
    field2,data2=AMR_field(8,-8,100)
    plt.plot(field,data,'or')

    plt.plot(field2,data2,'ob')
    plt.show()
data=np.array(data)
data2=np.array(data2)
print((field[np.argmax(data)]+field2[np.argmax(data2)])/2)
#%%

#%%
Z=[field,data,field2,data2]
df_AMR=pd.DataFrame(Z)
df_AMR=df_AMR.transpose()
df_AMR.columns=['field_- to +','Resi_- to +(ohm)','field_+ to -','Resi_+ to -(ohm)']
df_AMR.to_csv('AMR_-18mA_-start.csv',index=False)




#%%
def AMR_cur(current):
    keithley2450.write(":SOUR:CURR " + str(current))
    time.sleep(20)
    field,data=AMR_field(-1.5,1.5,1200)
    field2,data2=AMR_field(1.5,-1.5,1200)
    plt.plot(field,data,'or')
    plt.plot(field2,data2,'ob')
    plt.show()
    return np.array(field), np.array(field2),np.array(data),np.array(data2)

#%%
curren=[2,4,6,8]
start=0
end=8
path='./Experiment/20220213/Al2O3_sub_Pt(1.5)Co(0.7)Pt(1.5)/signal'
for j in tqdm(range(17)):
    V=(end-start)/16*j+start
    adc_IP.write('SOV%f' % V)
    for i in tqdm(curren, leave=False):
        p_c=i*1e-3
        p_m=-i*1e-3
        field, field2,data,data2=AMR_cur(p_c)
        Z=[field,data,field2,data2]
        df_AHE=pd.DataFrame(Z)
        df_AHE=df_AHE.transpose()
        df_AHE.columns=['field_- to +','Resi_- to +(ohm)','field_+ to -','Resi_+ to -(ohm)']
        df_AHE.to_csv(path+'/AHE_+{:.3f}mA_+{:.3f}V.csv'.format(p_c*1e+3,V),index=False)
        field3, field4,data3,data4=AMR_cur(p_m)
        Z=[field3,data3,field4,data4]
        df_AHE=pd.DataFrame(Z)
        df_AHE=df_AHE.transpose()
        df_AHE.columns=['field_- to +','Resi_- to +(ohm)','field_+ to -','Resi_+ to -(ohm)']
        df_AHE.to_csv(path+'/AHE_{:.3f}mA_+{:.3f}V.csv'.format(p_m*1e+3,V),index=False)
    if V!=0:
        adc_IP.write('SOV%f' % -V)
        for i in curren:
            p_c=i*1e-3
            p_m=-i*1e-3
            field, field2,data,data2=AMR_cur(p_c)
            Z=[field,data,field2,data2]
            df_AHE=pd.DataFrame(Z)
            df_AHE=df_AHE.transpose()
            df_AHE.columns=['field_- to +','Resi_- to +(ohm)','field_+ to -','Resi_+ to -(ohm)']
            df_AHE.to_csv(path+'/AHE_+{:.3f}mA_{:.3f}V.csv'.format(p_c*1e+3,-V),index=False)
            field3, field4,data3,data4=AMR_cur(p_m)
            Z=[field3,data3,field4,data4]
            df_AHE=pd.DataFrame(Z)
            df_AHE=df_AHE.transpose()
            df_AHE.columns=['field_- to +','Resi_- to +(ohm)','field_+ to -','Resi_+ to -(ohm)']
            df_AHE.to_csv(path+'/AHE_{:.3f}mA_{:.3f}V.csv'.format(p_m*1e+3,-V),index=False)
adc_IP.write('SOV%f' % 0)
I_s=[]
V_s=[]
for i in tqdm(curren, leave=False):
    keithley2450.write(":SOUR:CURR " + str(i*1e-3))
    I=float(keithley2450.query("measure:current?"))
    V=float(keithley2450.query("measure:volt?"))
    I_s.append(I)
    V_s.append(V)
data_e=[curren,I_s,V_s]
df_data=pd.DataFrame(data_e)
df_data=df_data.transpose()
df_data.columns=['set_current(mA)','measure_current(A)','measure_volt(V)']
path='./Experiment/20220213/Al2O3_sub_Pt(1.5)Co(0.7)Pt(1.5)'
df_data.to_csv(path+'/current_vs_voltage_for_electric_field.csv',index=False)

keithley2450.write(":SOUR:CURR 0")
keithley2450.write(":OUTP OFF") 
# plt.plot(Ip,shift_p,'o')
# plt.plot(Im,shift_m,'o')
# plt.xlabel('current I(A)')
# plt.ylabel('Heff(V)')
# plt.show()
#%%


#%%


#%%
field,field2,data,data2=AMR_cur(50e-3)
plt.plot(field[5:],data[5:],'-r')
plt.plot(field2[5:],data2[5:],'-r')
#plt.show()
field,field2,data,data2=AMR_cur(-50e-3)
plt.plot(field[5:],data[5:],'-b')
plt.plot(field2[5:],data2[5:],'-b')
plt.show()



# %%
print()
# %%
#%matplotlib inline
#plt.rcParams["font.family"] = 'Times New Roman'
plt.rcParams["font.family"] = 'Arial'
plt.rcParams["mathtext.fontset"] = 'cm' #全体のフォントを設定
#plt.rcParams['mathtext.default'] = 'it'
plt.rcParams['font.size'] = 30 #フォントサイズを設定
plt.rcParams['axes.linewidth'] = 3 #軸の太さを設定。目盛りは変わらない
plt.rcParams['xtick.labelsize'] = 30 # 横軸のフォントサイズ
plt.rcParams['ytick.labelsize'] = 30 # 縦軸のフォントサイズ
plt.rcParams['xtick.direction']='in'
plt.rcParams['ytick.direction']='in'
plt.rcParams['xtick.top']='True'
plt.rcParams['ytick.right']='True'
plt.rcParams['xtick.major.width']=3
plt.rcParams['xtick.minor.visible']='True'
plt.rcParams['xtick.minor.width']=3
plt.rcParams['xtick.minor.size']=5
plt.rcParams['ytick.minor.size']=5
plt.rcParams['ytick.major.width']=3
plt.rcParams['ytick.minor.width']=3
plt.rcParams['xtick.major.size']=7
plt.rcParams['ytick.major.size']=7
plt.rcParams['figure.figsize'] = 10,5
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

# %%
plt.plot(field_V,data,'ob')
plt.plot(field_V2,data2,'or')
plt.show()
# %%
def AHE_field2(start,end,datapoint):
    data=[]
    field=[]
    adc_IP.write('SOV%f' % start)
    time.sleep(10)
    for i in range(datapoint):
        slope=(end-start)/datapoint
        V=slope*(i-datapoint//2)
        adc_IP.write('SOV%f' % V)
        #print(kikusui_IP.query("VOLT?"))
        I=float(keithley2450.query("measure:current?"))
        Volt=float(keithley2182A.query(":SENSe:Data?"))
        #time.sleep(0.3)
        data.append(Volt/I)
        field.append(V)
    adc_IP.write('SOV%f' % 0)
    return field, data
# %%
path='./Experiment/20220127/SiO2sub_Ti(1.5)Pt(1.5)Co(0.7)Pt(1.5)Ti(x)SiO2(4)/x=1.5/switching'
adc_OOP.write('SOV%f' % -8)
time.sleep(3)
adc_OOP.write('SOV%f' % 0)
field,data=AHE_field2(-8,8,200)
time.sleep(5)
adc_OOP.write('SOV%f' % 8)
time.sleep(3)
adc_OOP.write('SOV%f' % 0)
field2,data2=AHE_field2(8,-8,200)
plt.plot(field,data,'or')

plt.plot(field2,data2,'ob')
plt.show()
#%%
Z=[field,data,field2,data2]
df_AMR=pd.DataFrame(Z)
df_AMR=df_AMR.transpose()
df_AMR.columns=['field_- to +_Hx','Resi_- to +(ohm)','field_+ to -_Hx','Resi_+ to -(ohm)']
df_AMR.to_csv(path+'/AHE_100uA_In-plane.csv',index=False)
#%%

plt.plot(field,data,'or')
plt.xlabel('H_x  (V)',fontsize=20)
plt.ylabel('$R_{xy} $ (ohm)',fontsize=20)
plt.plot(field2,data2,'ob')
plt.show()
# %%

path='./Experiment/20220127/SiO2sub_Ti(1.5)Pt(1.5)Co(0.7)Pt(1.5)Ti(x)SiO2(4)/x=1.5/switching'
field,data=AMR_field(-4,4,1000)
time.sleep(5)
field2,data2=AMR_field(4,-4,1000)
plt.plot(field,data,'or')

plt.plot(field2,data2,'ob')
plt.show()

Z=[field,data,field2,data2]
df_AMR=pd.DataFrame(Z)
df_AMR=df_AMR.transpose()
df_AMR.columns=['field_- to +','Resi_- to +(ohm)','field_+ to -','Resi_+ to -(ohm)']
df_AMR.to_csv(path+'/AHE_100uA.csv',index=False)

#%%
plt.plot(field,data,'or')

plt.plot(field2,data2,'ob')
plt.xlabel('H_z  (V)',fontsize=20)
plt.ylabel('$R_{xy} $ (ohm)',fontsize=20)
plt.show()
#%%
path='./Experiment/20220205/I-V_Harmonic'
I_s=[]
V_s=[]
for i in tqdm(np.linspace(-31,31,80), leave=False):
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

df_data.to_csv(path+'/current_vs_voltage_for_electric_field_W(20)Ni(8)SiO2(4).csv',index=False)

keithley2450.write(":SOUR:CURR 0")
keithley2450.write(":OUTP OFF") 
# %%





#================================================# 
#angle vs AHE
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

#%%
path='./Experiment/20220127/SiO2sub_Ti(1.5)Pt(1.5)Co(0.7)Pt(1.5)Ti(x)SiO2(4)/x=1.5/switching/AHE_angle_100uA'
for i in tqdm(np.linspace(0, 90,30),leave= False):
        dif_angle= 3#deg
        dif_pulse=dif_angle//0.0025
        current_posi = controller.position*0.0025
        #Lamp.write('PHAS:AUTO:ONCE') 
        time.sleep(2)
        field,data=AMR_field(-8,8,200)
        time.sleep(5)
        field2,data2=AMR_field(8,-8,200)
        plt.plot(field,data,'or')

        plt.plot(field2,data2,'ob')
        plt.show()
        Z=[field,data,field2,data2]
        df_AMR=pd.DataFrame(Z)
        df_AMR=df_AMR.transpose()
        df_AMR.columns=['field_- to +','Resi_- to +(ohm)','field_+ to -','Resi_+ to -(ohm)']
        df_AMR.to_csv(path+'/AHE_100uA_angle_dep_{:.4f}deg.csv'.format(current_posi),index=False)

        controller.position += dif_pulse # move to position
        controller.sleep_until_stop()
# %%

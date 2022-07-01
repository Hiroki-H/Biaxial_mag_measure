# -----------------------------------------------------------
# Author: Akiyo and Revised by hiroki
# Description: R vs field (pulse delta measurement)
# Required equipments: Keithley6221 Current Source
#                      Keithley2182A nanovoltmeter
#                      ADCMT 6240A Current/Voltage Source
#                      RS232-cable
#                      Trigger Link cable
# Reference: Reference Manual 622x-901-01 Rev. C / October 2008
# -----------------------------------------------------------
#%%
import pyvisa as visa
import matplotlib.pyplot as plt
from time import sleep
import numpy
import pandas as pd
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

#%%
# -----------------------------------------------------------
# Initialization
# -----------------------------------------------------------
rm = visa.ResourceManager()
rm.list_resources()
ke_6221 = rm.open_resource('GPIB1::12::INSTR') # KEITHLEY6221
adc_OOP = rm.open_resource(  'GPIB0::11::INSTR'  )
#%%
# -----------------------------------------------------------
# Constants of kikusui PBZ20-20 bipolar power supply for In-plane field
# -----------------------------------------------------------
MAG_VOL_MIN_P = 1.0
MEAS_POINT_NUM_P = 100
MAG_VOL_DELTA_P = -0.1

MAG_VOL_MIN_M = -1.0
MEAS_POINT_NUM_M = 21
MAG_VOL_DELTA_M = 0.1
# -----------------------------------------------------------
# Constants of KEITHLEY6221
# -----------------------------------------------------------
DELTA_DELAY = 100e-3
DELTA_COUNT = 10
TRACE_POINT = 10
MEAS_TIME = 5 # sec
SOURCE_CURR = 100e-6

#%%
# -----------------------------------------------------------
# Settings of ADCMT6241A
# -----------------------------------------------------------


# %% set biplor power supply
adc_OOP.write('C,*RST')
adc_OOP.write('M1')  # trigger mode hold
adc_OOP.write('VF')  # voltage output
adc_OOP.write('F2')  # current measurement
adc_OOP.write('SOV0,LMI0.03')  # dc 0V, limit 30mA
adc_OOP.write('OPR') # output on



#%%
# -----------------------------------------------------------
# Settings of KEITHLEY6221
# -----------------------------------------------------------
ke_6221.write('*RST')
ke_6221.write('UNIT V')
ke_6221.write('SOUR:DELT:DELay %f' % DELTA_DELAY)
ke_6221.write('SOUR:DELT:COUN %d' % DELTA_COUNT)
ke_6221.write('SOUR:DELT:CAB OFF')
ke_6221.write('TRAC:POIN %d' % TRACE_POINT)
ke_6221.write('SOUR:DELT:HIGH %f' % SOURCE_CURR)


#%%
# -----------------------------------------------------------
# Measurement
# -----------------------------------------------------------
def Delta_field(data_points,start_field_vol,end_field_vol):
    field=[]
    Resi=[]
    ke_6221.write('*RST')
    ke_6221.write('UNIT V')
    ke_6221.write('SOUR:DELT:DELay %f' % DELTA_DELAY)
    ke_6221.write('SOUR:DELT:COUN %d' % DELTA_COUNT)
    ke_6221.write('SOUR:DELT:CAB OFF')
    ke_6221.write('TRAC:POIN %d' % TRACE_POINT)
    ke_6221.write('SOUR:DELT:HIGH %f' % SOURCE_CURR)
    ke_6221.write('SOUR:DELT:ARM') # arms delta mode
    for i in range(data_points+1):
        slope=(end_field_vol-start_field_vol)/data_points
        field_vol=start_field_vol+slope*i
        adc_OOP.write('SOV%f' % field_vol)
        ke_6221.write('INIT:IMM') # starts delta measurements
        sleep(MEAS_TIME) # wait until measurement stops
        read_data = ke_6221.query_ascii_values("trace:data?") # even: meas_data, odd:  meas_time
        meas_data = read_data[::2]
        V_kiku=field_vol
        print('{:.4f}'.format(V_kiku), numpy.average(meas_data))
        field.append(V_kiku)
        Resi.append(numpy.average(meas_data)/SOURCE_CURR)
        update(V_kiku,numpy.average(meas_data)/SOURCE_CURR)
    ke_6221.write('SOUR:SWE:ABOR') # stops delta mode
    adc_OOP.write('SOV%f' % 0) # set zero field
    return field,Resi


x=[]
y=[]
def update(x1,y1):
    global curve, ptr, x ,y, V
    #   Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
    #keithley2450.write(":SOUR:VOLT " + str(V))
    #yvalue = keithley2450.query(":READ? \"defbuffer1\" ,source")
    #xvalue =  keithley2450.query(":READ?")       # read line (single value) from the serial port
    x.append(float(x1))
    y.append(float(y1))
    #   Xm[-1] = float(value)                 # vector containing the instantaneous values
    #   ptr += 1                              # update x position for displaying the curve
    curve.setData(x,y)                     # set the curve with this data
    #curve.setPos(0,float(x[-1]))                   # set x position in the graph to 0
    pg.QtGui.QApplication.processEvents()    # you MUST process the plot now


#%%

if __name__=='__main__':
    ### START QtApp #####
    app = pg.QtGui.QApplication([])            # you MUST do this once (initialize things)
    ####################
    win = pg.GraphicsWindow(title='Signal from serial port') # creates a window
    p = win.addPlot(title='Realtime plot')  # creates empty space for the plot in the window
    curve = p.plot( pen =(0, 114, 189), symbolBrush =(0, 114, 189),
                         symbolPen ='w', symbol ='p', symbolSize = 14, name ="symbol ='p'")
    p.showGrid(x=True,y=True)
    p.setLabel('left', "Resistance", units='ohm')
    p.setLabel('bottom', "magnetic field_volt", units='V')
    # Peforming measurement
    field1,Resi1=Delta_field(data_points=10,start_field_vol=-8,end_field_vol=8)
    sleep(5)
    field2,Resi2=Delta_field(10,8,-8)
    #%% visualizing measurement data
    plt.plot(field1,Resi1,'o-r')
    plt.plot(field2,Resi2,'o-b')
    plt.xlabel('V_field(V)')
    plt.ylabel('R(ohm)')
    plt.show()
    #%%
    # --------------------------------------------------#
    # stored data
    # ---------------------------------------------------#
    data=[field1,Resi1,field2,Resi2]
    df_AHE=pd.DataFrame(data)
    df_AHE=df_AHE.transpose()
    df_AHE.columns=['field_- to +','Resi_- to +(ohm)','field_+ to -','Resi_+ to -(ohm)']
    df_AHE
    #df_AMR.to_csv('AMR_1mA_test.csv',index=False)

#-------------------------------------------------------------#

    adc_OOP.write('SBY')  # output off
    adc_OOP.query('*OPC?')

    ke_6221.close()
    adc_OOP.close()

# %%

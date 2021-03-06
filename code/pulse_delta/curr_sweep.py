# -----------------------------------------------------------
# Author: Akiyo and revised by hiroki
# Description: Example for pulse delta measurement
# Required equipments: Keithley6221 Current Source
#                      Keithley2182A nanovoltmeter
#                      RS232-cable
#                      Trigger Link cable
# Reference: Reference Manual 622x-901-01 Rev. C / October 2008
# -----------------------------------------------------------
#%%
import pyvisa as visa
import matplotlib.pyplot as plt
#from RsInstrument.RsInstrument import RsInstrument, BinFloatFormat
from time import sleep
import numpy 
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pandas as pd
#%%
# -----------------------------------------------------------
# Initialization
# -----------------------------------------------------------
rm = visa.ResourceManager()
rm.list_resources()
ke_6221 = rm.open_resource('GPIB1::12::INSTR') # KEITHLEY6221
# ke_6221.read_termination = '\r'
# -----------------------------------------------------------
# Constants
# -----------------------------------------------------------
#%%
# -----------------------------------------------------------
# Measurement
# -----------------------------------------------------------

#%%
DELTA_COUNT4FLIP = 1 #pulse count
# DELTA_DELAY = 100e-6
# PULSE_WIDTH = 500e-6
DELTA_DELAY = 16e-6
PULSE_WIDTH = 50e-6
DELTA_COUNT4MEAS = 10
TRACE_POINT4MEAS = 10
DELTA_COUNT4FLIP = 1
FLIP_TIME = 5
MEAS_TIME = 5
CURR_LOW = 0 # 0-CURR_HIGH pulse
SOURCE_MEAS_CURR = 100e-6
Comp_vol=40 #V compliance voltage
ke_6221.write('*RST')
ke_6221.write('UNIT VOLTS')
ke_6221.write('SOUR:PDEL:RANG BEST') # current Range
ke_6221.write('SOUR:PDEL:INT 5') #INTERVAL 5PLC
ke_6221.write('SOUR:PDEL:SWE OFF')
ke_6221.write('SOUR:PDEL:LME 2') # two low-pulse measurement
ke_6221.write('SOUR:PDEL:LOW %f' % CURR_LOW)
ke_6221.write('SOUR:PDEL:WIDT %f' % PULSE_WIDTH)
ke_6221.write('SOUR:PDEL:SDEL %f' % DELTA_DELAY)
ke_6221.write('SOUR:CURR:COMP %f' % Comp_vol)
def pulse_delta(start_cur,end_cur,data_points):
    current=[]
    write_volt=[]
    read_volt=[]
    Resi=[]
    for i in range(data_points+1):
        slope=(end_cur-start_cur)/data_points
        pulse_cur=start_cur+slope*i
        ke_6221.write('SOUR:PDEL:HIGH %f' % pulse_cur)
        ke_6221.write('SOUR:PDEL:COUN %d' % DELTA_COUNT4FLIP)
        ke_6221.write('SOUR:PDEL:ARM') # arms pulse-delta mode
        ke_6221.write('INIT:IMM') # starts pulse-delta measurements
        sleep(FLIP_TIME) # wait until measurement stops
        ke_6221.write('SOUR:SWE:ABOR') # stops pulse-delta mode
        read_data_flip_volt = ke_6221.query_ascii_values("SENS:DATA?") # even: meas_data_flip_volt, odd:  meas_time
        meas_data_flip_volt = read_data_flip_volt[::2]
        ke_6221.write('SOUR:PDEL:HIGH %f' % SOURCE_MEAS_CURR)
        ke_6221.write('SOUR:PDEL:COUN %d' % DELTA_COUNT4MEAS)
        ke_6221.write('TRAC:POIN %d' % TRACE_POINT4MEAS)
        ke_6221.write('SOUR:PDEL:ARM') # arms delta mode
        ke_6221.write('INIT:IMM') # starts delta measurements
        sleep(MEAS_TIME) # wait until measurement stops
        ke_6221.write('SOUR:SWE:ABOR') # stops delta mode
        read_data_meas_volt = ke_6221.query_ascii_values("trace:data?") # even: meas_data_flip_volt, odd:  meas_time
        meas_data_meas_volt = read_data_meas_volt[::2]
        print('{:.8f}'.format(pulse_cur), numpy.average(meas_data_flip_volt), numpy.average(meas_data_meas_volt))
        current.append(pulse_cur)
        write_volt.append(numpy.average(meas_data_flip_volt))
        read_volt.append(numpy.average(meas_data_meas_volt))
        Resi.append(numpy.average(meas_data_meas_volt)/SOURCE_MEAS_CURR)
        update(pulse_cur,numpy.average(meas_data_meas_volt)/SOURCE_MEAS_CURR)
    return current,write_volt,read_volt,Resi

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


if __name__ == '__main__':
    ### START QtApp #####
    app = pg.QtGui.QApplication([])            # you MUST do this once (initialize things)
    ####################
    win = pg.GraphicsWindow(title='Signal from serial port') # creates a window
    p = win.addPlot(title='Realtime plot')  # creates empty space for the plot in the window
    curve = p.plot( pen =(0, 114, 189), symbolBrush =(0, 114, 189),
                         symbolPen ='w', symbol ='p', symbolSize = 14, name ="symbol ='p'")
    p.showGrid(x=True,y=True)
    p.setLabel('left', "Resistance", units='ohm')
    p.setLabel('bottom', "Current", units='A')
    cur1,write_volt1,read_volt1,Resi1=pulse_delta(-30e-3,30e-3,11)
    #cur2,write_volt2,read_volt2,Resi2=pulse_delta(18e-3,-18e-3,10)
    plt.plot(cur1,Resi1,'o-')
    #plt.plot(cur2,Resi2,'o-')
    #plt.xlim(-0.078,0.08)
    #plt.ylim(190,194)
    plt.show()

    data=[cur1,Resi1,cur2,Resi2]
    df=pd.DataFrame(data)
    df=df.transpose()
    df.columns=['current_- to +(A)','Resi_- to +(ohm)','current_+ to -(A)','Resi_+ to -(ohm)']
    df
    df.to_csv('AMR_1mA_test.csv',index=False)
    ke_6221.close()
# %%



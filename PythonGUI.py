import serial
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk
from tkinter import ttk
from tkinter import *

import time

ser = serial.Serial()
ser.baudrate = 115200
ser.port = 'COM14'
ser.open()


#========================== ADC FUNCTIONS ==========================#
def ADC_readout():
	ser.write(b"readout__")

def ADC_test():
    ser.write(b"test__")

def ADC_stop():
	start_button.config(state=NORMAL)
	stop_button.config(state=DISABLED)
	pos_dropdown.config(state=NORMAL)
	neg_dropdown.config(state=NORMAL)
	gain_dropdown.config(state=NORMAL)
	data_dropdown.config(state=NORMAL)
	ser.write(b"stop__")

def ADC_start():
	stop_button.config(state=NORMAL)
	start_button.config(state=DISABLED)
	pos_dropdown.config(state=DISABLED)
	neg_dropdown.config(state=DISABLED)
	gain_dropdown.config(state=DISABLED)
	data_dropdown.config(state=DISABLED)
	ADC_setpins(dVar_pos.get(), dVar_neg.get())
	time.sleep(.1)
	ADC_setgain(dVar_gain.get())
	time.sleep(.1)
	ADC_setdatarate(dVar_data.get())
	time.sleep(.1)
	ser.write(b"start__")

def ADC_setpins(pin1, pin2):
	message = "setinputpins "+pin1+" "+pin2+"__"
	ser.write(message.encode())

def ADC_setgain(value):
	message = "setgain "+value+"__"
	ser.write(message.encode())

def ADC_setdatarate(value):
	message = "setdatarate "+value+"__"
	ser.write(message.encode())

#========================== UI ELEMENTS ==========================#
root = tk.Tk()
tk.Tk.wm_title(root, "Sensor Analysis")
#label = tk.Label(root, text="Sensor Analysis")
#label.grid(row=0, column=4)

LARGE_FONT= ("Verdana", 12)

quit_button = ttk.Button(root, text="Quit",command=quit)
quit_button.grid(row=0, column=5)

#pause_button = ttk.Button(root, text="Pause (3s)", command=ADC_test)
#pause_button.grid(row=3, column=5)

start_button = ttk.Button(root, text="Start", command=ADC_start)
start_button.grid(row=1, column=5)

stop_button = ttk.Button(root, text="Stop", command=ADC_stop, state=DISABLED)
stop_button.grid(row=2, column=5)

root.grid_columnconfigure(6, minsize=60)

dlabel = tk.Label(root, text="Input Pins", font=LARGE_FONT)
dlabel.grid(row=0, column=7, columnspan=2, sticky=S)

dVar_pos = StringVar(root)
dVar_pos.set("8")
pos_dropdown = OptionMenu(root, dVar_pos, "7", "8", "10", "11")
pos_dropdown.grid(row=1, column=7, sticky=E)
poslabel = tk.Label(root, text="+", font=LARGE_FONT)
poslabel.grid(row=2, column=7, sticky=N)

dVar_neg = StringVar(root)
dVar_neg.set("10")
neg_dropdown = OptionMenu(root, dVar_neg, "7", "8", "10", "11")
neg_dropdown.grid(row=1, column=8, sticky=E)
neglabel = tk.Label(root, text="GND", font=LARGE_FONT)
neglabel.grid(row=2, column=8, sticky=N)

dVar_gain = StringVar(root)
dVar_gain.set("1")
gain_dropdown = OptionMenu(root, dVar_gain, "1", "2", "4", "8", "16", "32", "64", "128")
gain_dropdown.grid(row=5, column=8, sticky=E)
gainlabel = tk.Label(root, text="Gain", font=LARGE_FONT)
gainlabel.grid(row=4, column=8, sticky=S)

dVar_data = StringVar(root)
dVar_data.set("100")
data_dropdown = OptionMenu(root, dVar_data, "60", "100", "200", "400", "800", "1000", "2000", "4000")
data_dropdown.grid(row=8, column=8, sticky=E)
datalabel = tk.Label(root, text="Datarate", font=LARGE_FONT)
datalabel.grid(row=7, column=8, sticky=S)



#========================== ANIMATED PLOT ==========================#
ADC_stop() #we don't want any data coming in before the settings are initialized

LARGE_FONT= ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

yList = []

MAX_LIST_SIZE = 100

def animate(i):
    if (ser.inWaiting() > 0):
    	yList.append(float(ser.readline()))
    	if (len(yList) > MAX_LIST_SIZE):
    		yList.pop(0)

    	xList = list(range(len(yList)))
    	a.clear()
    	a.plot(xList, yList)

canvas = FigureCanvasTkAgg(f, root)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, rowspan=48, columnspan=4)


#========================== MAIN EXECUTION ==========================#
ani = animation.FuncAnimation(f, animate, interval=1)
root.mainloop()

import serial
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import *

import time

import sys
import glob


ser = serial.Serial()
ser.baudrate = 115200
frame_active = False

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def set_serial_port():
	if (ser.isOpen()):
		ser.close()
		disable_regs()
		start_button.config(state=DISABLED)
		port_button.config(text="Connect")
		port_dropdown.config(state=NORMAL)
	else:
		ser.port = dVar_port.get()
		ser.open()
		ADC_stop()
		enable_regs()
		start_button.config(state=NORMAL)
		port_button.config(text="Disconnect")
		port_dropdown.config(state=DISABLED)

def clear_data():
	global yList, num_samples, dataFile
	yList = []
	num_samples = 0
	dataFile.close()
	dataFile = open("temp_data.txt", "w")
	data_slider.config(from_=0, to=0)


dataFile = open("temp_data.txt", "w")

def save_data():
	path = filedialog.asksaveasfilename(filetypes=(("text files", "*.txt"),("all files","*.*")))
	if (path != ""):
		if (path[-4:] != ".txt"):
			path += ".txt"
		global dataFile
		dataFile.close()
		data_out = open(path, "w")
		lines = [line.rstrip("\n") for line in open("temp_data.txt")]
		for line in lines:
			if line != "":
				data_out.write(line + "\n")

		dataFile = open("temp_data.txt", "a")

def open_data():
	path = filedialog.askopenfilename(filetypes=(("text files", "*.txt"),("all files","*.*")))
	if (path != ""):
		global saved_yList
		saved_yList = []
		if (ser.isOpen()):
			ser.close()
		lines = [line.rstrip('\n') for line in open(path)]
		for line in lines:
			if line != "":
				saved_yList.append(float(line[(line.find(",")+1):]))
		data_slider.config(from_=min(len(saved_yList), MAX_LIST_SIZE), to=len(saved_yList))
		data_slider.set(min(len(saved_yList), MAX_LIST_SIZE))

#========================== ADC FUNCTIONS ==========================#
def ADC_readout():
	ser.write(b"readout__")

def ADC_test():
    ser.write(b"test__")

def enable_regs():
	pos_dropdown.config(state=NORMAL)
	neg_dropdown.config(state=NORMAL)
	gain_dropdown.config(state=NORMAL)
	data_dropdown.config(state=NORMAL)
	pga_dropdown.config(state=NORMAL)
	filter_dropdown.config(state=NORMAL)
	clock_dropdown.config(state=NORMAL)
	chop_dropdown.config(state=NORMAL)


def disable_regs():
	pos_dropdown.config(state=DISABLED)
	neg_dropdown.config(state=DISABLED)
	gain_dropdown.config(state=DISABLED)
	data_dropdown.config(state=DISABLED)
	pga_dropdown.config(state=DISABLED)
	filter_dropdown.config(state=DISABLED)
	clock_dropdown.config(state=DISABLED)
	chop_dropdown.config(state=DISABLED)

def ADC_stop():
	dataFile.flush()
	global frame_active
	frame_active = False

	global saved_yList
	saved_yList = []
	lines = [line.rstrip('\n') for line in open("temp_data.txt")]
	for line in lines:
		if line != "":
			saved_yList.append(float(line[(line.find(",")+1):]))

	start_button.config(state=NORMAL)
	stop_button.config(state=DISABLED)
	save_button.config(state=NORMAL)
	open_button.config(state=NORMAL)
	clear_button.config(state=NORMAL)
	port_button.config(state=NORMAL)
	#port_dropdown.config(state=NORMAL)

	enable_regs()
	if (ser.isOpen()):
		ser.write(b"stop__")
		#ser.close()
		port_dropdown["menu"].delete(0, "end")
		choices = serial_ports()
		for c in choices:
			port_dropdown["menu"].add_command(label=c, command=tk._setit(dVar_port, c))

def ADC_start():
	#ser.port = dVar_port.get()
	#ser.open()
	global frame_active
	frame_active = True

	start_button.config(state=DISABLED)
	stop_button.config(state=NORMAL)
	save_button.config(state=DISABLED)
	open_button.config(state=DISABLED)
	clear_button.config(state=DISABLED)
	port_button.config(state=DISABLED)
	#port_dropdown.config(state=DISABLED)

	disable_regs()
	ser.write(b"start__")

def ADC_setpins(a, b, c):
	message = "setinputpins "+ dVar_pos.get() +" "+ dVar_neg.get() +"__"
	ser.write(message.encode())

def ADC_setgain(a, b, c):
	message = "setgain "+ dVar_gain.get() +"__"
	ser.write(message.encode())

def ADC_setdatarate(a, b, c):
	message = "setdatarate "+ dVar_data.get() +"__"
	ser.write(message.encode())

def ADC_setpga(a, b, c):
	message = "setpga "+ dVar_pga.get() +"__"
	ser.write(message.encode())

def ADC_setclock(a, b, c):
	message = "setpga "+ dVar_clock.get() +"__"
	ser.write(message.encode())

def ADC_setfilter(a, b, c):
	message = "setpga "+ dVar_filter.get() +"__"
	ser.write(message.encode())

def ADC_setchop(a, b, c):
	message = "setpga "+ dVar_chop.get() +"__"
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
stop_button.grid(row=2, column=5, sticky=N)

clear_button = ttk.Button(root, text="Clear Data", command=clear_data)
clear_button.grid(row=3, column=5)

open_button = ttk.Button(root, text="View Saved Data", command=open_data)
open_button.grid(row=46, column=7)

save_button = ttk.Button(root, text="Save All Data to File", command=save_data)
save_button.grid(row=46, column=5, columnspan=2)

root.grid_columnconfigure(6, minsize=60)

dlabel = tk.Label(root, text="Input Pins   ", font=LARGE_FONT)
dlabel.grid(row=0, column=7, columnspan=2, sticky=S)

dVar_pos = StringVar(root)
dVar_pos.set("8")
pos_dropdown = OptionMenu(root, dVar_pos, "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11")
pos_dropdown.grid(row=1, column=7)
poslabel = tk.Label(root, text="+", font=LARGE_FONT)
poslabel.grid(row=2, column=7, sticky=N)
dVar_pos.trace("w", ADC_setpins)

dVar_neg = StringVar(root)
dVar_neg.set("10")
neg_dropdown = OptionMenu(root, dVar_neg, "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11")
neg_dropdown.grid(row=1, column=8)
neglabel = tk.Label(root, text="GND", font=LARGE_FONT)
neglabel.grid(row=2, column=8, sticky=N)
dVar_neg.trace("w", ADC_setpins)

dVar_gain = StringVar(root)
dVar_gain.set("1")
gain_dropdown = OptionMenu(root, dVar_gain, "1", "2", "4", "8", "16", "32", "64", "128")
gain_dropdown.grid(row=5, column=8, sticky=E)
gainlabel = tk.Label(root, text="Gain", font=LARGE_FONT)
gainlabel.grid(row=4, column=8, sticky=S)
dVar_gain.trace("w", ADC_setgain)

dVar_data = StringVar(root)
dVar_data.set("100")
data_dropdown = OptionMenu(root, dVar_data, "60", "100", "200", "400", "800", "1000", "2000", "4000")
data_dropdown.grid(row=8, column=8, sticky=E)
datalabel = tk.Label(root, text="Datarate", font=LARGE_FONT)
datalabel.grid(row=7, column=8, sticky=S)
dVar_data.trace("w", ADC_setdatarate)

port_options = serial_ports()
dVar_port = StringVar(root)
dVar_port.set(port_options[0])
port_dropdown = OptionMenu(root, dVar_port, *port_options)
port_dropdown.grid(row=33, column=8, sticky=E)
portlabel = tk.Label(root, text="Port", font=LARGE_FONT)
portlabel.grid(row=32, column=8, sticky=S)

port_button = ttk.Button(root, text="Connect", command=set_serial_port)
port_button.grid(row=34, column=8, columnspan=2)

data_slider = Scale(root, from_=0, to=0, orient=HORIZONTAL)
data_slider.grid(row=44, column=5, columnspan=4, sticky=W+E)


dVar_pga = StringVar(root)
dVar_pga.set("Enabled")
dVar_pga.trace("w", ADC_setpga)
pga_dropdown = OptionMenu(root, dVar_pga, "Enabled", "Bypassed", "IP_Buffer_Bypassed")
pga_dropdown.grid(row=5, column=7, sticky=E)
pgalabel = tk.Label(root, text="PGA", font=LARGE_FONT)
pgalabel.grid(row=4, column=7, sticky=S)
dVar_pga.trace("w", ADC_setpga)

dVar_filter = StringVar(root)
dVar_filter.set("Low_Latency")
filter_dropdown = OptionMenu(root, dVar_filter, "Low_Latency", "SINC3")
filter_dropdown.grid(row=8, column=7, sticky=E)
filterlabel = tk.Label(root, text="Filter", font=LARGE_FONT)
filterlabel.grid(row=7, column=7, sticky=S)
dVar_filter.trace("w", ADC_setfilter)

dVar_clock = StringVar(root)
dVar_clock.set("Internal")
clock_dropdown = OptionMenu(root, dVar_clock, "Internal", "External")
clock_dropdown.grid(row=5, column=5, sticky=E)
clocklabel = tk.Label(root, text="Clock", font=LARGE_FONT)
clocklabel.grid(row=4, column=5, sticky=S)
dVar_clock.trace("w", ADC_setclock)

dVar_chop = StringVar(root)
dVar_chop.set("Off")
chop_dropdown = OptionMenu(root, dVar_chop, "On", "Off")
chop_dropdown.grid(row=8, column=5, sticky=E)
choplabel = tk.Label(root, text="Chop", font=LARGE_FONT)
choplabel.grid(row=7, column=5, sticky=S)
dVar_chop.trace("w", ADC_setchop)


#========================== ANIMATED PLOT ==========================#
disable_regs()
start_button.config(state=DISABLED)

LARGE_FONT= ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

yList = []
saved_yList = []

MAX_LIST_SIZE = 100
num_samples = 0;

def animate(i):
	global frame_active
	if not (frame_active):
		xList = list(range(max(data_slider.get()-MAX_LIST_SIZE, 0), data_slider.get()))
		a.clear()
		view_yList = []

		for n in range(max(data_slider.get()-MAX_LIST_SIZE, 0), data_slider.get()):
			view_yList.append(saved_yList[n])
		a.plot(xList, view_yList)

	else:
		if (ser.inWaiting() > 0):
			line = ser.readline().decode("utf-8")
			dataFile.write(line)
			text = line.split(',')
			yList.append(float(text[1]))
			if (len(yList) > MAX_LIST_SIZE):
				yList.pop(0)


			global num_samples
			num_samples += 1;
			xList = list(range(max(num_samples-MAX_LIST_SIZE, 0), num_samples))
			a.clear()
			a.plot(xList, yList)
			data_slider.config(from_=min(num_samples, MAX_LIST_SIZE), to=num_samples)
			data_slider.set(num_samples)

canvas = FigureCanvasTkAgg(f, root)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, rowspan=48, columnspan=4)


#========================== MAIN EXECUTION ==========================#
ani = animation.FuncAnimation(f, animate, interval=1)
root.mainloop()

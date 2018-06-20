import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style

import tkinter as tk
from tkinter import ttk

import serial

ser = serial.Serial()
ser.baudrate = 115200
ser.port = 'COM14'
ser.open()

def ADC_readout():
	ser.write(b"readout__")

def ADC_test():
    ser.write(b"test__")

def ADC_stop():
	ser.write(b"stop__")

def ADC_start():
	ser.write(b"start__")


LARGE_FONT= ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

yList = []

MAX_LIST_SIZE = 100

def animate(i):
    """pullData = open("sampleText.txt","r").read()
    dataList = pullData.split('\n')
    xList = []
    yList = []
    for eachLine in dataList:
        if len(eachLine) > 1:
            x, y = eachLine.split(',')
            xList.append(int(x))
            yList.append(int(y))

    a.clear()
    a.plot(xList, yList)"""
    if (ser.inWaiting() > 0):
    	yList.append(float(ser.readline()))
    	if (len(yList) > MAX_LIST_SIZE):
    		yList.pop(0)

    	xList = list(range(len(yList)))
    	a.clear()
    	a.plot(xList, yList)
    

    
            

class SensorGUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        #tk.Tk.iconbitmap(self, default="clienticon.ico")
        tk.Tk.wm_title(self, "Sensor Analysis")
        
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}


        frame = GraphFrame(container, self)

        self.frames[GraphFrame] = frame

        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(GraphFrame)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        
class GraphFrame(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Quit",
                            command=quit)
        button1.pack()

        button2 = ttk.Button(self, text="Pause (3s)",
                            command=ADC_test)
        button2.pack()

        button3 = ttk.Button(self, text="Start",
                            command=ADC_start)
        button3.pack()

        button4 = ttk.Button(self, text="Stop",
                            command=ADC_stop)
        button4.pack()

        

        

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


app = SensorGUI()
ani = animation.FuncAnimation(f, animate, interval=1)
app.mainloop()
#!/usr/bin/python
# -*- coding: utf-8 -*-



totalMinutes = 20



from Tkinter import Tk, Frame, Toplevel, Button, Label, BOTH
from datetime import datetime, timedelta
import threading



class Binder:
	def __init__(self):
		self.dict = {}

	def addBinding(self, char, fun):
		self.dict[char] = fun

	def keyEvent(self, event):
		char = event.char

		if char in self.dict:
			self.dict[char]()



class MainFrame(Frame):
	def __init__(self, parent, binder):
		Frame.__init__(self, parent)

		self.parent = parent
		self.binder = binder
		self.initUI()
	
	def initUI(self):
		self.parent.title("PyTimer")

		self.parent.bind('<Key>', self.binder.keyEvent)
		self.pack(fill=BOTH, expand=1)

		grid = Frame(self)
		grid.pack()

		self.au = Button(grid, text="A+")
		self.au.grid(row=1, column=0, padx=5, pady=5)

		self.ad = Button(grid, text="A-")
		self.ad.grid(row=0, column=0, padx=5, pady=5)

		self.bu = Button(grid, text="B+")
		self.bu.grid(row=1, column=1, padx=5, pady=5)

		self.bd = Button(grid, text="B-")
		self.bd.grid(row=0, column=1, padx=5, pady=5)

		self.ss = Button(grid, text="start/stop")
		self.ss.grid(columnspan=2, pady=5)

		self.rt = Button(grid, text="reset")
		self.rt.grid(columnspan=2, pady=5)

		self.focus_set()

	def setA(self, up, down):
		self.au.config(command=up)
		self.ad.config(command=down)

	def setB(self, up, down):
		self.bu.config(command=up)
		self.bd.config(command=down)

	def setStartStop(self, ss):
		self.ss.config(command=ss)

	def setReset(self, reset):
		self.rt.config(command=reset)



class NumWindow(Toplevel):
	def __init__(self, master, title, binder, geometry):
		Toplevel.__init__(self, master)

		self.master = master
		self.binder = binder
		self.initUI(title, geometry)
	
	def initUI(self, title, geometry):
		self.title(title)
		self.geometry(geometry)

		self.bind('<Key>', self.binder.keyEvent)
		self.label = Label(self, text='-', background='white')
		self.label.pack(fill=BOTH, expand=1)

		def resize(event):
			self.label.config(font=(None, int(event.height * .95)))

		self.bind('<Configure>', resize)

	def setNum(self, num):
		self.label.config(text=num)



class PointTracker:
	def __init__(self, callback):
		self.i = 0;
		self.callback = callback;

	def up(self): 
		self.i = self.i + 1;
		self.callback(self.i)

	def down(self):
		self.i = max(0, self.i - 1)
		self.callback(self.i)

	def reset(self):
		self.i = 0
		self.callback(0)



class Timer:
	def __init__(self, onUpdate, onEnded=None):
		self.onUpdate = onUpdate
		self.onEnded = onEnded
		self.lock = threading.RLock()
		self.timer = None
		self.reset()
		
	def reset(self):
		with self.lock:
			self.remaining = timedelta(0, totalMinutes *60 -1, 999999)
			self.end = None
			self.running = False			
			if self.timer != None:
				self.timer.cancel()
				self.timer = None

			self.update(self.remaining)

	def update(self, rem):
		with self.lock:
			ss = rem.seconds + 1
			mm = ss // 60
			ss = ss % 60
			self.onUpdate(mm, ss)
		
	def startStop(self):
		def tick():
			with self.lock:
				rem = self.end - datetime.now()
				if rem.days < 0:
					if self.onEnded != None:
						self.onEnded()
					self.reset()
					
				else:
					self.update(rem)
					self.timer = threading.Timer(rem.microseconds / 1000000.0, tick)
					self.timer.start()
			
		with self.lock:
			if not self.running:
				self.end = datetime.now() + self.remaining
				self.remaining = None
				self.running = True
				tick()
				
			else:
				self.remaining = self.end - datetime.now()
				self.end = None
				self.running = False
				
				if self.timer != None:
					self.timer.cancel()
					self.timer = None



def main():
	binder = Binder()

	root = Tk()
	sw = root.winfo_screenwidth() /10
	sh = root.winfo_screenheight() /10

	root.geometry("200x150+{x:d}+{y:d}".format(x = 5*sw -100, y = 7*sh + 40))
	mainwin = MainFrame(root, binder)

	wpa = NumWindow(root, "Punti A", binder,
					"{w:d}x{h:d}+{x:d}+{y:d}".format(w = 3*sw, h = 3*sh, x = 2*sw, y = sh))
	ta = PointTracker(wpa.setNum)
	ta.reset()
	mainwin.setA(ta.up, ta.down)
	binder.addBinding('c', ta.up)
	binder.addBinding('d', ta.down)

	wpb = NumWindow(root, "Punti B", binder,
					"{w:d}x{h:d}+{x:d}+{y:d}".format(w = 3*sw, h = 3*sh, x = 5*sw, y = sh))
	tb = PointTracker(wpb.setNum)
	tb.reset()
	mainwin.setB(tb.up, tb.down)
	binder.addBinding('m', tb.up)
	binder.addBinding('k', tb.down)

	wm = NumWindow(root, "Minuti",  binder,
					"{w:d}x{h:d}+{x:d}+{y:d}".format(w = 3*sw, h = 3*sh, x = 2*sw, y = 4*sh + 20))
	ws = NumWindow(root, "Secondi", binder,
					"{w:d}x{h:d}+{x:d}+{y:d}".format(w = 3*sw, h = 3*sh, x = 5*sw, y = 4*sh + 20))

	def updateTimer(mm, ss):
		wm.setNum("{:02d}".format(mm))
		ws.setNum("{:02d}".format(ss))

	def reset():
		timer.reset()
		ta.reset()
		tb.reset()

	timer = Timer(updateTimer)
	mainwin.setStartStop(timer.startStop)
	binder.addBinding(' ', timer.startStop)
	mainwin.setReset(reset)

	root.mainloop()



if __name__ == '__main__':
	main()


















import urllib.request
import tkinter
from tkinter.simpledialog import askstring
from aesm import Cipher, ClientNetwork

class Window(tkinter.Tk):
	def __init__(self):
		super(Window,self).__init__()
		self.geometry("800x600")
		self.bind('<KeyPress>', self.sendMessage)
		self.title("Test Chat System")
		self.resizable(False,False)
		self.protocol("WM_DELETE_WINDOW", self.closeFunction)
		self.after(0,self.retrieveMessage)

		self.frame = tkinter.Frame(self)
		self.frame.pack()

		self.scrollbar = tkinter.Scrollbar(self.frame)
		self.chat = tkinter.Text(self.frame,height=26,bd=5,yscrollcommand=self.scrollbar.set,font=("Courier",14))
		self.scrollbar.config(command=self.chat.yview)
		self.scrollbar.pack(side="right",fill="y")
		self.chat.pack(side="left",fill="x")
		self.msg = tkinter.Entry(self,bd=5,font=("Courier",14,"bold"))
		self.msg.pack(side="bottom",fill="both")
		self.mainloop()

	def retrieveMessage(self):
		msg = socket.retrieved.getData()
		if msg != None:
			self.showMessage(msg[1])
		self.after(10,self.retrieveMessage)

	def showMessage(self,message):
		self.chat.configure(state='normal')
		self.chat.insert('end', message+"\n")
		self.chat.configure(state='disabled')

	def sendMessage(self,event):
		if event.char == "\r":
			text = self.msg.get()
			socket.sendData(f"QOPWQEQWKN{text}")
			self.msg.delete(0,len(text))

	def closeFunction(self):
		socket.stop()
		self.destroy()
		exit()

def getData():
	try:
		hostInfo = eval(urllib.request.urlopen("https://socketlayerserver.ditinlenehibis.repl.co").read())
	except:
		hostInfo = None
	return hostInfo

ipInfo = getData()

name = askstring('Test Chat System', 'Provide with a username!')

socket = ClientNetwork(host=ipInfo[0],port=ipInfo[1])
socket.sendData("0UL9FZ6VVM"+name)

win = Window()



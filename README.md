# Asynchronous Encrypted Socket Module

This is a completely asynchronous and encrypted sockets layer module that I created
It's purpose is to handle retrieve all packets sent by connection and create convenient data structures in order parse through these packets one by one
It also handles encryption between two endpoints, it isn't perfect like any other encryption standard. However it is better than none and also just wanted test and tinker with encrption.

# How does the library work?

Well first off both modules on client and server side require the same name, this was an intentional choice as to throw off any interception of the encryption key.
<br>
So e.g.
Server-side imports: `import aesm` => Client-side imports: `import aesm`
<br>
** It will not work if the imports are of different names **
<br>
The library uses different data structures in order to handle data appropriately

Packets => They are tuple e.g. (1682417420, "Message") // The first value in the tuple is a unix time of when the message was sent
<hr>

To get started I will show you some examples of how to instantiate the class
```py
#You must import "Cipher"

from aesm import Cipher, ServerNetwork, ClientNetwork

#ServerSide
socket = ServerNetwork(host="<ENTER VALID HOST ADDRESS>", port=<ENTER HOST PORT>)

#ClientSide
socket = ClientNetwork(host="<ENTER TARGET ADDRESS>", port=<ENTER TARGET PORT>)
```

# Server-side Functionality

```py
#You must import "Cipher" from aesm

import asyncio
from aesm import Cipher, ServerNetwork

socket = ServerNetwork(host="<ENTER VALID HOST ADDRESS>", port=<ENTER HOST PORT>)

while (True):
  socket.connections.activity() # Returns None or (<ADDRESS>, <True or False, which indicates whether the connection accepted or not respectively>, <UNIX TIME OF ACTIVITY>)
  
  socket.connections.getDataOrdinal(oldToNew=True) # Returns latest/oldest packet in the stack of connections
  
  socket.connections[<ADDRESS>]["data"].getData() # Returns the oldest data packet sent by client
  socket.connections[<ADDRESS>]["data"][<POSITION INTEGER>] # Returns data packet in that position
  len(socket.connections[<ADDRESS>]["data"]) # Returns number of packets in queue
  
  
  asyncio.run(socket.sendTo("<INSERT DATA AS STRING>",<ADDRESS>)) #Sends data to a specific connection
  asyncio.run(socket.sendAll("<INSERT DATA AS STRING>")) #Send data to all connections
  
socket.stop() # Stops the socket connection, you could also do socket.close() but it may lead to unclosed threads and connections(not reliable)
```

# Client-side Functionality

```py
#You must import "Cipher" from aesm

from aesm import Cipher, ClientNetwork

socket = ClientNetwork(host="<ENTER TARGET ADDRESS>", port=<ENTER TARGET PORT>)

socket.sendData("<DATA STRING>")

while (True):
  socket.retrieved[<POSITION INTEGER>] #Returns data packet in that position
  socket.retrieved.getData() #Returns the oldest data packet sent by server

```

# Example of deployment
I have deployed a server on replit (link here: https://replit.com/@DitinLeNehibis/SocketLayerServer), it has a simple tkinter userinterface and username system. You can test it using `exemplarClient.py` simply run that file along with having `aesm.py` in the same directory and you will automatically connect to the server, thanks to some clever port forwarding I did on the server side.
![image](https://user-images.githubusercontent.com/97798919/234248864-53769860-953e-420e-a324-fbd90119e900.png)
![image](https://user-images.githubusercontent.com/97798919/234249229-4693695d-70e8-4c58-854d-c19f45be4fbe.png)
![image](https://user-images.githubusercontent.com/97798919/234249506-1fb79f56-c821-4007-ab6e-968b16b012ee.png)
![image](https://user-images.githubusercontent.com/97798919/234249620-4300584a-6c32-482a-8aed-b5e561cef54c.png)


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

To get started I will show you some examples of how to instantiate the class
```py
#You must import "Cipher"

from aesm import Cipher, ServerNetwork, ClientNetwork

#ServerSide
socket = ServerNetwork(host="<ENTER HOST ADDRESS>", port=<ENTER HOST PORT>)

#ClientSide
socket = ClientNetwork(host="<ENTER TARGET ADDRESS>", port=<ENTER TARGET PORT>)
```

# Serverside Functionality

```py
#You must import "Cipher"

from aesm import Cipher, ServerNetwork

socket = ServerNetwork(host="<ENTER HOST ADDRESS>", port=<ENTER HOST PORT>)

while (True):
  socket.connections.activity() # => returns None or (<ADDRESS>, <True or False, which indicates whether the connection accepted or not respectively>, <UNIX TIME OF ACTIVITY>)
  
  socket.connections.getDataOrdinal(oldToNew=True) => Returns latest/oldest packet in the stack of connections


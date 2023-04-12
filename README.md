# Asynchronous Encrypted Socket Module

This is a completely asynchronous and encrypted sockets layer module that I created
It's purpose is to handle retrieve all packets sent by connection and create convenient data structures in order parse through these packets one by one
It also handles encryption between two endpoints, it isn't perfect like any other encryption standard. However it is better than none and also just wanted test and tinker with encrption.

# How does the library work?

Well first off both modules on client and server side require the same name, this was an intentional choice as to throw off any interception of the encryption key.
So e.g.
Server-side imports: `import aesm` => Client-side imports: `import aesm`
** It will not work if the imports are of different names **

To get started I will show you some examples of how to instantiate the class
```py
from aesm import Cipher, ServerNetwork, ClientNetwork

#ServerSide
socket = ServerNetwork(host="<ENTER HOST ADDRESS>", port=<ENTER HOST PORT>)

#ClientSide
socket = ClientNetwork(host="<ENTER TARGET ADDRESS>", port=<ENTER TARGET PORT>)
```

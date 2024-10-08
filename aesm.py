import pip
import os

# Automatically installs pycryptodome if it's not installed
pip.main(["install", "pycryptodome"])

# Import necessary modules
import time
import socket
import random
import string
import pickle
import asyncio
from threading import Thread

import base64
import hashlib
from random import randint
from Crypto import Random
from Crypto.Cipher import AES

# Defining a huge constant for some large number handling
huge = 100**100

# Cipher class handles AES encryption and decryption
class Cipher(object):

    def __init__(self):
        self.blockSize = AES.block_size
        # Generate a random key of size between 8 and 32
        self.key = hashlib.sha256(self._key(randint(8, 32))).digest()

    def _key(self, length):
        # Generates a random key using printable characters
        return ''.join(random.choice(string.printable) for i in range(length)).encode()

    def encrypt(self, text):
        # Pad the text to fit AES block size
        text = self._pad(text)
        iv = Random.new().read(self.blockSize)  # Generate a random IV
        cipher = AES.new(self.key, AES.MODE_CBC, iv)  # Create AES cipher in CBC mode
        return base64.b64encode(iv + cipher.encrypt(text.encode()))  # Return the encrypted message

    def decrypt(self, text):
        # Decrypt the message using AES in CBC mode
        text = base64.b64decode(text)  # Decode base64
        iv = text[:self.blockSize]  # Extract the IV
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(text[self.blockSize:])).decode('utf-8')  # Decrypt and unpad

    def _pad(self, s):
        # Pads the text to be a multiple of the block size
        padding_size = self.blockSize - len(s) % self.blockSize
        return s + padding_size * chr(padding_size)

    @staticmethod
    def _unpad(s):
        # Removes padding from the decrypted text
        return s[:-ord(s[-1])]

# Connections class manages client connections in a dictionary
class Connections(dict):

    def __init__(self):
        super(Connections, self).__init__()
        self.status = []

    # Overridden setitem to track connection status and timestamps
    def __setitem__(self, item, value):
        super(Connections, self).__setitem__(item, value)
        # Track the connection activity
        self.status.append((item, value is not None, time.time()))

    # Returns the next activity status (if any)
    def activity(self):
        try:
            return self.status.pop(0)
        except IndexError:
            return None

    # Retrieves the oldest or newest data packet from the stream
    def getDataOrdinal(self, oldToNew=True):
        datagram = (None, (huge if oldToNew else 0, None))
        for addr in list(self.keys()):
            try:
                packet = self[addr]["data"].getData()
                if packet and ((oldToNew and packet[0] < datagram[1][0]) or (packet[0] > datagram[1][0])):
                    datagram = (addr, packet)
            except:
                pass
        return datagram

# DataStream class for managing a stream of incoming data and timestamps
class DataStream(list):

    def __init__(self):
        super(DataStream, self).__init__()
        self.data = []
        self.time = []

    # Append new data with timestamp
    def append(self, item):
        self.data.append(item)
        self.time.append(time.time())

    # Retrieve the oldest data item and its timestamp
    def getData(self):
        try:
            return (self.time.pop(0), self.data.pop(0))
        except IndexError:
            return None

# ServerNetwork class, based on a TCP socket, for managing server-side operations
class ServerNetwork(socket.socket):

    def __init__(self, host, port):
        super(ServerNetwork, self).__init__(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.connections = Connections()
        self.exitStatus = 0

        self.bind((host, port))
        # Start a listener thread using asyncio
        Thread(target=lambda: asyncio.run(self.listener())).start()
        os.system('cls' if os.name == 'nt' else 'clear')

    # Handles receiving data from a particular client
    async def receive(self, addr):
        loop = asyncio.get_event_loop()
        request = None
        while (request != 'quit') and (not self.exitStatus):
            try:
                # Asynchronously receive data from the client
                request = await loop.sock_recv(self.connections[addr]["connection"], 255)
                data = self.connections[addr]["encryption"].decrypt(request)  # Decrypt the incoming data
                self.connections[addr]["data"].append(str(data))  # Store the decrypted data
            except:
                break

        self.connections[addr]["connection"].close()
        self.connections[addr] = None

    # Sends data to all connected clients
    async def sendAll(self, data):
        loop = asyncio.get_event_loop()
        for addr in list(self.connections.keys()):
            try:
                await loop.sock_sendall(self.connections[addr]["connection"], 
                                        self.connections[addr]["encryption"].encrypt(data))
            except:
                pass

    # Sends data to a specific client
    async def sendTo(self, data, addr):
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(self.connections[addr]["connection"],
                                self.connections[addr]["encryption"].encrypt(data))

    # Listener for accepting incoming connections
    async def listener(self):
        while not self.exitStatus:
            self.listen()
            self.setblocking(False)
            loop = asyncio.get_event_loop()

            # Accept new connections asynchronously
            connection, addr = await loop.sock_accept(self)

            # Send encryption key to the client
            cipher = Cipher()
            connection.send(pickle.dumps([cipher]))

            # Store connection info
            self.connections[addr] = {
                "connection": connection,
                "encryption": cipher,
                "data": DataStream()
            }

            # Start receiving data from this client
            loop.create_task(self.receive(addr))

    # Stops the server
    def stop(self):
        self.exitStatus = 1
        self.close()

# ClientNetwork class for managing client-side operations
class ClientNetwork(socket.socket):

    def __init__(self, host=None, port=None):
        super(ClientNetwork, self).__init__(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.connect((host, port))

        self.exitStatus = 0
        self.retrieved = DataStream()

        # Receive encryption key from the server
        self.cipher = pickle.loads(self.recv(1024))[0]

        # Start a thread for receiving data
        Thread(target=lambda: asyncio.run(self.receive())).start()
        os.system('cls' if os.name == 'nt' else 'clear')

    # Send encrypted data to the server
    def sendData(self, data):
        self.send(self.cipher.encrypt(data))

    # Asynchronously receive data from the server
    async def receive(self):
        loop = asyncio.get_event_loop()
        request = None
        while (request != 'quit') and (not self.exitStatus):
            try:
                request = await loop.sock_recv(self, 255)
                data = self.cipher.decrypt(request)  # Decrypt the received data
                self.retrieved.append(str(data))  # Store it in the DataStream
            except:
                break

    # Stop the client connection
    def stop(self):
        self.exitStatus = 1
        self.close()

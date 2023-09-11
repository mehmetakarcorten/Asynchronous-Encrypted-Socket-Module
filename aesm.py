import pip
import os

pip.main(["install", "pycryptodome"])

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

huge = 100**100


class Cipher(object):

  def __init__(self):
    self.blockSize = AES.block_size
    self.key = hashlib.sha256(self._key(randint(8, 32))).digest()

  def _key(self, length):
    return ''.join(random.choice(string.printable)
                   for i in range(length)).encode()

  def encrypt(self, text):
    text = self._pad(text)
    iv = Random.new().read(self.blockSize)
    cipher = AES.new(self.key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(text.encode()))

  def decrypt(self, text):
    text = base64.b64decode(text)
    iv = text[:self.blockSize]
    cipher = AES.new(self.key, AES.MODE_CBC, iv)
    return self._unpad(cipher.decrypt(text[self.blockSize:])).decode('utf-8')

  def _pad(self, s):
    return s + (self.blockSize - len(s) %
                self.blockSize) * chr(self.blockSize - len(s) % self.blockSize)

  @staticmethod
  def _unpad(s):
    return s[:-ord(s[len(s) - 1:])]


class Connections(dict):

  def __init__(self):
    super(Connections, self).__init__
    self.status = []

  def __setitem__(self, item, value):
    super(Connections, self).__setitem__(item, value)
    self.status.append((item, True if (value != None) else False, time.time()))

  def activity(self):
    try:
      copy = self.status.pop(0)
    except:
      copy = None
    return copy

  def getDataOrdinal(self, oldToNew=True):
    datagram = (None, (huge if oldToNew == True else 0, None))
    for addr in list(self.keys()):
      try:
        packet = self[addr]["data"].getData()
        if (packet != None) and (oldToNew
                                 == True) and (packet[0] < datagram[1][0]):
          datagram = (addr, packet)
        elif (packet != None) and (packet[0] > datagram[1][0]):
          datagram = (addr, packet)
      except:
        pass
    return datagram


class DataStream(list):

  def __init__(self):
    super(DataStream, self).__init__
    self.data = []
    self.time = []

  def append(self, item):
    self.data.append(item)
    self.time.append(time.time())

  def getData(self):
    try:
      x = (self.time.pop(0), self.data.pop(0))
    except:
      x = None
    return x


class ServerNetwork(socket.socket):

  def __init__(self, host, port):
    super(ServerNetwork, self).__init__(family=socket.AF_INET,
                                        type=socket.SOCK_STREAM)
    self.connections = Connections()
    self.exitStatus = 0

    self.bind((host, port))
    Thread(target=lambda: asyncio.run(self.listener())).start()
    os.system('cls' if os.name == 'nt' else 'clear')

  async def receive(self, addr):
    loop = asyncio.get_event_loop()
    request = None
    while (request != 'quit') and (not self.exitStatus):
      try:
        request = (await loop.sock_recv(self.connections[addr]["connection"],
                                        255))
        data = self.connections[addr]["encryption"].decrypt(request)
        self.connections[addr]["data"].append(str(data))
      except:
        break

    self.connections[addr]["connection"].close()
    self.connections[addr] = None

  async def sendAll(self, data):
    loop = asyncio.get_event_loop()
    for addr in self.connections.keys():
      try:
        await loop.sock_sendall(self.connections[addr]["connection"],self.connections[addr]["encryption"].encrypt(data))
      except:
        pass

  async def sendTo(self, data, addr):
    loop = asyncio.get_event_loop()
    await loop.sock_sendall(self.connections[addr]["connection"],
                            self.connections[addr]["encryption"].encrypt(data))

  async def listener(self):
    while (not self.exitStatus):

      self.listen()
      self.setblocking(False)
      loop = asyncio.get_event_loop()
      connection, addr = await loop.sock_accept(self)

      cipher = Cipher()
      dump = pickle.dumps([cipher])
      connection.send(dump)

      self.connections[addr] = {
        "connection": connection,
        "encryption": cipher,
        "data": DataStream()
      }
      loop.create_task(self.receive(addr))

  def stop(self):
    self.exitStatus = 1
    self.close()


class ClientNetwork(socket.socket):

  def __init__(self, host=None, port=None):
    super(ClientNetwork, self).__init__(family=socket.AF_INET,
                                        type=socket.SOCK_STREAM)
    self.connect((host, port))

    self.exitStatus = 0
    self.retrieved = DataStream()

    self.cipher = self.recv(1024)
    self.cipher = pickle.loads(self.cipher)[0]

    Thread(target=lambda: asyncio.run(self.receive())).start()
    os.system('cls' if os.name == 'nt' else 'clear')

  def sendData(self, data):
    self.send(bytes(self.cipher.encrypt(data)))

  async def receive(self):
    loop = asyncio.get_event_loop()
    request = None
    while (request != 'quit') and (not self.exitStatus):
      try:
        request = (await loop.sock_recv(self, 255))
        data = self.cipher.decrypt(request)
        self.retrieved.append(str(data))
      except:
        break

  def stop(self):
    self.exitStatus = 1
    self.close()

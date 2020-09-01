import json
import logging
import socket
import struct
import time
from concurrent.futures import ThreadPoolExecutor

from dummy_data_provider import DummyDataProvider as ddp
from jetson_parser import JetsonParser
from jetson_sender import JetsonSender
from variable import *


class ConnectionHandler(JetsonSender, JetsonParser):

    def __init__(self, getPIDs, setPIDs, getMotors, protocol, addr=JETSON_ADDRESS):
        JetsonSender.__init__(self, protocol)
        JetsonParser.__init__(self)
        self.protocol = protocol
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.methodCollector(getPIDs,setPIDs, getMotors)
        self.server=None
        self.host = addr[0]
        self.port = addr[1]
        self.active = True
        self.tx_ready = True
        self.tx_buff = []
        self.clientConnected = False
        self.sendingActive = False

    def methodCollector(self, getPIDs, setPIDs, getMotors): #getDepth, getHummidity...
        self.getPIDs = getPIDs
        self.getMotors = getMotors
        self.setPIDs = setPIDs

    def start_sending(self, interval = 30):
        self.interval = interval/1000
        self.executor.submit(self.loop)

    def stop_sending(self):
        self.sendingActive = False

    def start_serving(self):
        self.executor.submit(self.run)

    def loop(self):
        if self.clientConnected:
            self.sendingActive = True

            while self.clientConnected and self.sendingActive:
                time.sleep(self.interval)
                self.sendMotors(self.getMotors())

            self.sendingActive = False

    def clientHandler(self, conn, addr):
        self.clientConnected = True
        print(f"New connection from {addr}")
        rx_state=FRAME_SECTION["HEADER"]
        rx_len=0
        while self.active:
            try:
                if(rx_state==FRAME_SECTION["HEADER"]):
                    data=conn.recv(4)
                    if data == b'':
                        raise ConnectionResetError
                    rx_len=struct.unpack("<I",data)[0]
                    rx_len-=4
                    rx_state=FRAME_SECTION["DATA"]
                elif(rx_state==FRAME_SECTION["DATA"]):
                    data=conn.recv(rx_len).decode("ascii")
                    logging.debug(data)
                    self.executor.submit(self.parse ,data)
                    rx_state=FRAME_SECTION["HEADER"]
            except ConnectionResetError:
                self.clientConnected = False
                conn.close()
                print("Client disconnected")
                return
            except Exception as e:
                logging.debug("Exception")
                rx_state=FRAME_SECTION["HEADER"]
        print("closing")
        self.clientConnected = False
        conn.close()
        return

    def serverHandler(self):
        self.server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.bind((self.host,self.port))
        self.server.listen()
        self.active=True
        print(f"[LISTENING] Server is listening on {self.host}:{self.port}.")

        while self.active:
            conn, addr = self.server.accept()
            self.executor.submit(self.clientHandler,conn, addr)
            # t=threading.Thread(target=self.clientHandler, args=(conn, addr))
            # t.start()


    def run(self):
        self.serverHandler()


    def stop(self):
        logging.debug(f"Closing server on {self.host}:{self.port}")
        self.active= False
        self.server.close()


    def send(self, data):
        self.ack = b""
        serialized = json.dumps(data).encode('ascii')
        lenght = struct.pack('<I', len(serialized))
        logging.debug(lenght)
        self.server.send(b"\xA0"+lenght)
        logging.debug(b"\xA0"+lenght)
        self.server.sendall(serialized)
        # async def write():
        #     self.writer.write(data)
        #     await self.writer.drain()
        # asyncio.run_coroutine_threadsafe(write(), self.client_loop)



if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    addr = ("localhost", 1234)
    with open("../config/protocol.json", 'r') as p:
        protocol = json.load(p)
    server = ConnectionHandler(
        lambda x:ddp.provide_dummy_data(len=None, spec = x),
        print,
        lambda: ddp.provide_dummy_data(len=5),
        protocol,
        addr)
    server.start_serving()
    server.start_sending()
    while True:
            time.sleep(1)

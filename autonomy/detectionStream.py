import asyncio,socket, struct, logging, threading, json, pickle
from variable import GUI_DEPTH_MAP

class detectionStream:
    def __init__(self, ip="localhost", port = 6969):
        self.port = port
        self.ip= ip
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active = True
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip,port))
        self.socket.listen()
        self.connection, self.addr = self.socket.accept()

    def send_detection(self, detection, fps, img):
        try:
            data = [fps, detection,img]
            data = pickle.dumps(data)
            self.connection.send(b"\x68")
            a = self.connection.recv(1)
            if a ==b"\x68":
                self.connection.sendall(struct.pack("<I",len(data))+data)
        except ConnectionAbortedError:
            self.connection.close()
    def stop(self):
        #self.connection.close()
        #self.socket.shutdown(socket.SHUT_RDWR)
        logging.debug("closing socket")
        self.socket.close()
        logging.debug("socket closed")
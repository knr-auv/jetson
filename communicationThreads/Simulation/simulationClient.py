import socket
from struct import *
import logging
import time
import json
import variable as var

class SimulationClient:
    """Klasa Tworzy clienta do sterowania łódką w symulacji"""
    def __init__(self, port=var.SIM_CONTROL_ADDRESS[1], ip=var.SIM_CONTROL_ADDRESS[0]):
        """Inicjalizacja socekta """
        self.port = port
        self.ip = ip
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.debug("Socket connect port:{}".format(port))
        self.socket.connect((self.ip, self.port))
        logging.debug("Socket now Connect with port:{}".format(port))
        self.motors_data = {"FL":0.0,"FR":0.0,"ML":0.0,"MR":0.0,"B":0.0}
        self.data =  b""
        self.ack = b""
        self.samples = None

    def __del__(self):
        self.socket.close()

    def set_motors(self):
        self.ack = b""
        serialized = json.dumps(self.motors_data).encode('ascii')
        lenght = pack('<I', len(serialized))
        self.socket.send(b"\xA0"+lenght)
        self.socket.sendall(serialized)
        #print(serialized)
        #confirm = self.socket.recv(1)
        #lenght = self.socket.recv(4)
        #lenght = unpack('<I', lenght)[0]
        #self.ack += self.socket.recv(lenght)

    def get_pos(self):
        self.data = b""
        self.socket.send(b"\xC2\x00\x00\x00\x00")
        #print("Send")
        confirm = self.socket.recv(1)
        #print(confirm)
        if not(confirm == b"\xC2"):
            logging.debug("Message error")
            return None
        lenght = self.socket.recv(4)
        lenght = unpack('<I', lenght)[0]
        #print(lenght)
        while not(len(self.data) >= lenght):
            self.data += self.socket.recv(4096)

        ack = self.data[lenght:]
        return json.loads(self.data[:lenght])

    def get_sens(self):
        self.data = b""
        self.socket.send(b"\xB0\x00\x00\x00\x00")
        #print("Send")
        confirm = self.socket.recv(1)
        #print(confirm)
        if not(confirm == b"\xB0"):
            logging.debug("Message error")
            # print(confirm)
            return None
        lenght = self.socket.recv(4)
        lenght = unpack('<I', lenght)[0]
        #print(lenght)
        while not(len(self.data) >= lenght):
            self.data += self.socket.recv(4096)

        ack = self.data[lenght:]
        return json.loads(self.data[:lenght])

    def get_sample(self, sample):
        if self.samples is None:
            return 0
        if sample == "roll":
            if self.samples['gyro']['z'] > 180:
                return -360 + self.samples['gyro']['z']
            elif self.samples['gyro']['z'] < -180:
                return 360 + self.samples['gyro']['z']
            return self.samples['gyro']['z']
        elif sample == "pitch":
            if self.samples['gyro']['x'] > 180:
                return 360 - self.samples['gyro']['x']
            if self.samples['gyro']['x'] < -180:
                return -360 - self.samples['gyro']['x']
            return -self.samples['gyro']['x']
        elif sample == "yaw":
            if self.samples['gyro']['y'] > 180:
                return -360 + self.samples['gyro']['y']
            elif self.samples['gyro']['y'] < -180:
                return 360 + self.samples['gyro']['y']
            return self.samples['gyro']['y']
        elif sample == "depth":
            return  self.samples["baro"]["pressure"]/9800

    def catch_sample(self):
        data = self.get_sens()
        if data is not None:
            self.samples = data

    def _run_motors(self, motors_data):
        if len(motors_data) == 5:
            self.motors_data["FL"] = -motors_data[4] / 1000
            self.motors_data["FR"] = -motors_data[2] / 1000
            self.motors_data["ML"] = motors_data[0] / 1000
            self.motors_data["MR"] = motors_data[1] / 1000
            self.motors_data["B"] = motors_data[3] / 1000
        self.set_motors()
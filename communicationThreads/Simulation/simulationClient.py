import socket
from struct import *
import base64
import logging
import time
import json
#import variable as var

class Types:
    DEPTH_MAP = b'\xb1'
    POSITION = b'\xC2'
    SENSORS = b'\xB0'
    DETECTION = b'\xb2'
    VIDEO_STREAM = b'\xB3'
    ACK = b'\xC1'
    MOTORS = b'\xA0'


class SimulationClient:
    """Klasa Tworzy clienta do sterowania łódką w symulacji"""
    def __init__(self, port=44210, ip='localhost'):
        """Inicjalizacja socekta """
        self.port = port
        self.ip = ip
        self.createConnection()

    def createConnection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.ip, self.port))
        except:
            logging.error("Could't connect to simulation.")
            exit()
        logging.debug("Connected with simulation on port:{}".format(self.port))
        self.motors_data = {"FL":0.0,"FR":0.0,"ML":0.0,"MR":0.0,"B":0.0}
        self.data =  b""
        self.samples = None
        pass

    def __del__(self):
        self.socket.close()
    def get_packet(self, packetType, toJson = True,msg = None,response = True, flag = b'\x00'):
        rec = False
        while not rec:
            try:
                ret = self.__get_packet(packetType, toJson, msg, response,flag)
                rec = True
            except:
                self.createConnection()

        if ret!=None:
            flag, data = ret
            return flag,data
        return
    def __get_packet(self, packetType, toJson = True,msg = None,response = True, flag = b'\x00'):
        if msg!=None:
            lenght = pack('<I', len(msg))
        else:
            lenght = b'\x00\x00\x00\x00'
        self.socket.send(packetType)
        self.socket.send(flag)
        self.socket.send(lenght)
        if msg!=None:
            self.socket.sendall(msg)
        
        if response:
            data=b''
            packetType = self.socket.recv(1)
            flag = self.socket.recv(1)
            lenght = self.socket.recv(4)
            lenght = unpack('<I', lenght)[0]
            chunk =4096
            if(lenght<chunk):
                chunk = lenght
            while not(len(data) >= lenght):
                data += self.socket.recv(chunk)
            data = data[:lenght]
            if toJson:
                data =  json.loads(data)

            return flag,data
        return



    
    def get_stream_frame(self):
        flag, data = self.get_packet(Types.VIDEO_STREAM,False)

        return data
    def get_depth_map(self):
        flag, data = self.get_packet(Types.DEPTH_MAP)
        data = base64.b64decode(data["depth"])
        return  data

    prev_pos = None
    def get_pos(self):

        temp = self.get_packet(Types.POSITION)
        if(temp==None):
            return self.prev_pos
        flag, data = temp
        self.prev_pos = data
        return data

    def get_sens(self):
        try:
            flag, data = self.get_packet(Types.SENSORS)
        except:
            logging.debug('error while getting sensors')
            data = None
        return  data

    def get_detection(self):
        flag, data = self.get_packet(Types.DETECTION)
        return  data

    def set_motors(self):

        serialized = json.dumps(self.motors_data).encode('ascii')
        self.get_packet(Types.MOTORS,msg = serialized,toJson = False, response = False)









    def get_sample(self, sample):
        ret=[]
        if self.samples is None:
            return 0
        if sample == "gyro":
            temp =self.samples["rot_speed"]
            return [-temp["z"], -temp['x'], temp['y']]
        elif sample == 'acc':
            temp =self.samples["accel"]
            return [temp["z"], temp['x'], temp['y']]
        elif sample == 'depth':
            return self.samples["baro"]["pressure"]/9800

        elif sample =='attitude':
            if self.samples['gyro']['z'] >= 180:
                ret.append(360 - self.samples['gyro']['z'])
            elif self.samples['gyro']['z'] < -180:
                ret.append(-360 - self.samples['gyro']['z'])
            else:
                ret.append(-self.samples['gyro']['z'])

            if self.samples['gyro']['x'] >= 180:
                ret.append(360 - self.samples['gyro']['x'])
            elif self.samples['gyro']['x'] < -180:
                ret.append(-360 - self.samples['gyro']['x'])
            else:
                ret.append(-self.samples['gyro']['x'])

            if self.samples['gyro']['y'] >= 180:
                 ret.append(-360 + self.samples['gyro']['y'])
            elif self.samples['gyro']['y'] < -180:
                 ret.append(360 + self.samples['gyro']['y'])
            else:
                ret.append(self.samples['gyro']['y'])
            return ret

    def catch_sample(self):
        data = self.get_sens()
        if data is not None:
            self.samples = data

    def _run_motors(self, motors_data):
        if len(motors_data) == 5:
            self.motors_data["FL"] = motors_data[4] / 1000
            self.motors_data["FR"] = motors_data[2] / 1000
            self.motors_data["ML"] = motors_data[0] / 1000
            self.motors_data["MR"] = motors_data[1] / 1000
            self.motors_data["B"] = motors_data[3] / 1000
            #print(self.motors_data)
        self.set_motors()

if __name__ == "__main__":
    a = SimulationClient()
    a.motors_data = {"FL":1.0,"FR":-1.0,"ML":0.0,"MR":0.0,"B":0.0}

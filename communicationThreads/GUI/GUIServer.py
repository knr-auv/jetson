import asyncio,socket, struct, threading, logging, json
from controlThread.controlThread import controlThread
from concurrent.futures import ThreadPoolExecutor
from variable import GUI_ADDRESS, GUI_STREAM
from autonomy.autonomyThread import autonomy

class comunicator:
    #class for sending data to gui.
     def __init__(self):
         self.confirmArm=None
         self.confirmDisarm =None
         self.autonomyMsg = None
         
class GUIStream(threading.Thread):
    def __init__(self, stream):
        self.stream = stream
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream.getFrame()
        self.socket.bind(GUI_STREAM)
        self.active = False
        self.socket.listen()

    def clienThread(self, connection):
        try:
            while self.active:
                a = connection.recv(1)
                if a==b"\x69":
                    connection.send(b"\x69")
                    data = self.stream.getFrame()
                    l = len(data)
                    connection.sendall(struct.pack("<I",l)+data)
        except:
            pass
        
    def run(self):
        self.active= True    
        while True:
            connection, addr = self.socket.accept()
            x = threading.Thread(target = self.clienThread, args=(connection,))
            x.start()

class sender:
    def __init__(self,protocol):
        self.proto = protocol["TO_GUI"]
        self.pid_spec = protocol["PID_SPEC"]
        self.control_spec = protocol["CONTROL_SPEC"]
    def send(self):
        pass
    def send_msg(self, msg):
        header = struct.pack('<i', len(msg)+ 4)
        msg = bytearray(header+msg)
        self.send(msg)

    def sendPid(self, PID = []):
        axis = PID[0]
        if axis=='roll':
            spec=self.pid_spec["roll"]
        elif axis =='pitch':
            spec = self.pid_spec["pitch"]
        elif axis == 'yaw':
            spec = self.pid_spec["yaw"]
        elif axis == 'depth':
            spec = self.pid_spec['depth']
        elif axis =='all':
            spec = self.pid_spec["all"]
        else:
            logging.debug(axis+"is not a valid argument of pidSend. Valid arguments: 'roll', 'pitch', 'yaw', 'all'")
            return
        PID.pop(0)
        if spec != self.pid_spec["all"]:
            tx_buffer = [self.proto["PID"],spec]  + PID
            tx_buffer = struct.pack('<2B4f', *(tx_buffer))
            self.send_msg(tx_buffer)
        elif spec == self.pid_spec["all"]:
            tx_buffer = [self.proto["PID"],spec]  + PID
            tx_buffer = struct.pack('<2B16f', *(tx_buffer))
            self.send_msg(tx_buffer)
          
    def sendMotors(self,data): 
        tx_buffer = [self.proto["MOTORS"]]+data
        tx_buffer = struct.pack('<B5f', *(tx_buffer))
        self.send_msg(tx_buffer)
        
    def sendBoatData(self):
        data = self.config.get("mode")
        data += ',' + "not connected"
        data = bytes(data, 'utf-8')
        data_len = len(data)
        tx_buffer = [self.proto["BOAT_DATA"],data_len,data]
        tx_buffer = struct.pack('<2B'+str(data_len)+'s', *(tx_buffer))
        self.send_msg(tx_buffer)

    def sendIMU(self, data = []):
        tx_buffer = [self.proto["IMU"]]+data
        tx_buffer = struct.pack('<B4f', *(tx_buffer))
        self.send_msg(tx_buffer)

    def sendControl(self, msg):

        if msg[0] == self.control_spec['ARMED']:
            logging.debug("Sending arming signal")
            tx_buffer = [self.proto["CONTROL"]]+msg
            tx_buffer = struct.pack('<2B',*(tx_buffer))
            self.send_msg(tx_buffer)

        if msg[0] == self.control_spec['DISARMED']:
            tx_buffer = [self.proto["CONTROL"]]+msg
            tx_buffer = struct.pack('<2B',*(tx_buffer))
            self.send_msg(tx_buffer)

    def sendAutonomyMsg(self, msg):
        data = bytes(msg, 'utf-8')
        data_len = len(data)
        tx_buffer = [self.proto["AUTONOMY_MSG"],data_len, data]
        tx_buffer = struct.pack('<2B'+str(data_len)+'s', *(tx_buffer))
        self.send_msg(tx_buffer)

class parser:

    def parse(self, data):
        proto = self.protocol["TO_ODROID"]
        pid_spec = self.protocol["PID_SPEC"]
        control_spec = self.protocol["CONTROL_SPEC"]

        if data[0] == proto["PID"]:
            if data[1]!= pid_spec["all"]:
                msg = struct.unpack('<2B4f', data)
                msg = list(msg)
                msg.pop(0)
                if msg[0]==pid_spec["roll"]:
                    msg[0] = 'roll'
                elif msg[0]==pid_spec["pitch"]:
                    msg[0] ='pitch'
                elif msg[0]==pid_spec["yaw"]:
                    msg[0]='yaw'
                elif msg[0]==pid_spec["depth"]:
                    msg[0]='depth'
                self.controlThread.setPIDs(msg)
            elif data[1]==pid_spec["all"]:
                msg  = struct.unpack('<2B16f', data)
                msg = list(msg)
                msg.pop(0)
                msg[0]='all'
                self.controlThread.setPIDs(msg)
                
        if data[0] == proto["PID_REQUEST"]:
            msg = struct.unpack('<2B',data)
            msg = list(msg)
            if msg[1]==pid_spec["roll"]:
                msg[1] = 'roll'
            elif msg[1]==pid_spec["pitch"]:
                msg[1] ='pitch'
            elif msg[1]==pid_spec["yaw"]:
                 msg[1]='yaw'
            elif msg[1]==pid_spec["depth"]:
                msg[1]='depth'

            elif msg[1]== pid_spec["all"]:
                msg[1] = 'all'
            self.sendPid(self.controlThread.getPIDs(msg[1]))

        if (data[0] == proto["CONTROL"]):
            if (data[1]==control_spec["START_TELEMETRY"]):
                msg = struct.unpack('<2BI',data)
                msg = list(msg)
                self.start_sending(msg[2])
            elif (data[1]==control_spec["STOP_TELEMETRY"]):
                self.stop_sending()
            elif (data[1]==control_spec["START_PID"]):
                msg = struct.unpack('<2BI',data)
                msg = list(msg)
                logging.debug("Received arm signal")
                self.controlThread.arm()

                
            elif (data[1]==control_spec["STOP_PID"]):
                self.controlThread.disarm()
            elif(data[1]==control_spec["START_AUTONOMY"]):
                logging.debug("starting autonomy")
                self.autonomyThread = autonomy(self.controlThread, self.stream)
                self.executor.submit(self.autonomyThread.run)
            elif(data[1]==control_spec["STOP_AUTONOMY"]):
                self.autonomyThread.stop()
            elif data[1]==control_spec["MODE"]:
                msg = struct.unpack("<3B", data)
                self.controlThread.setControlMode(msg[2])

        if(data[0]==proto["BOAT_DATA_REQUEST"]):
            self.sendBoatData()

        if (data[0] == proto["PAD"]):
            msg = struct.unpack('<B2f3i', data)
            msg = list(msg)
            msg.pop(0)
            self.parsePadData(msg)



class connectionHandler(threading.Thread, sender,parser):
    def __init__(self, stream):
        threading.Thread.__init__(self)
        with open('config/GUI.json', 'r') as fd:
            self.protocol = json.load(fd)
        sender.__init__(self,self.protocol)
        self.lock = threading.Lock()
        #4 is enought even with working autonomy...
        self.executor = ThreadPoolExecutor(max_workers=10)
        addr = GUI_ADDRESS
        self.controlThread = None
        self.host = addr[0]
        self.port = addr[1]
        self.active = True
        self.tx_ready = True
        self.clientConnected = False
        self.sendingActive = False
        self.comunicator= comunicator()
        self.configComunicator()
        self.stream = stream;
        self.GUIStream = GUIStream(stream)
        self.executor.submit(self.stream.run)
        self.executor.submit(self.GUIStream.run)

    def parsePadData(self, msg):
        mode = self.controlThread.getControlMode()
        if mode == 0:
            self.controlThread.setAngle(msg[0], msg[1])
            if(msg[2]!=0):
                heading = self.controlThread.getHeading()
                heading +=msg[2]/100.
                self.controlThread.setHeading(heading)
            if(msg[3]!=0):
                depth = self.controlThread.getDepth()
                depth -=msg[3]/2000
                self.controlThread.setDepth(depth)
            self.controlThread.moveForward(msg[4])

        elif mode ==1:
            self.controlThread.setAngularVelocity(msg[0], msg[1], msg[2])
            self.controlThread.vertical(-msg[3])
            self.controlThread.moveForward(msg[4])

    def configComunicator(self):
        self.comunicator.confirmArm = self.confirmArm
        self.comunicator.confirmDisarm=self.confirmDisarm
        self.comunicator.autonomyMsg = self.sendAutonomyMsg

    def setControlThread(self, arg = controlThread()):
        self.controlThread = arg
        self.loadPIDs()

    def loadPIDs(self):
        with open("config/PID_simulation.json", "r") as fd:
            self.data = json.load(fd)
        self.controlThread.setPIDs(["roll", self.data["roll"]["P"],self.data["roll"]["I"],self.data["roll"]["D"], self.data["roll"]["stab"]])
        self.controlThread.setPIDs(["pitch", self.data["pitch"]["P"],self.data["pitch"]["I"],self.data["pitch"]["D"], self.data["roll"]["stab"]])
        self.controlThread.setPIDs(["yaw",self.data["yaw"]["P"],self.data["yaw"]["I"],self.data["yaw"]["D"], self.data["roll"]["stab"] ])
        self.controlThread.setPIDs(["depth", self.data["depth"]["P"],self.data["depth"]["I"],self.data["depth"]["D"], self.data["depth"]["stab"]])
    
    def start_sending(self, interval = 30):
        if(self.sendingActive == False):
            self.interval = interval/1000
            self.executor.submit(lambda: asyncio.run(self.loop()))
        else:
            with self.lock:
                self.interval = interval/1000

    def stop_sending(self):
        self.sendingActive = False

    def confirmArm(self):
        self.sendControl([self.protocol["CONTROL_SPEC"]["ARMED"]])

    def confirmDisarm(self):
        self.sendControl([self.protocol["CONTROL_SPEC"]["DISARMED"]])

    async def loop(self):
        if self.clientConnected:
            self.sendingActive = True           
            while self.clientConnected and self.sendingActive:
                await asyncio.sleep(self.interval)
                self.sendIMU(self.controlThread.getImuData())
                self.sendMotors(self.controlThread.getMotors())               
            self.sendingActive = False

    async def clientHandler(self, reader,writer):
        HEADER = 0
        DATA = 1
        rx_state = HEADER
        logging.debug("client connected")
        self.writer = writer
        self.client_loop = asyncio.get_running_loop()
        self.clientConnected = True
        try:
            
            while self.active: 
                try:
                    if(rx_state ==HEADER):
                        async def receive4():
                            data = await reader.read(4)
                            return data
                        self.reader_task = asyncio.create_task(receive4())
                        data = await self.reader_task
                        if data == b'':
                            raise ConnectionResetError                           
                        rx_len = struct.unpack("<L",data)[0]
                        rx_len -= 4
                        rx_state = DATA
                    elif(rx_state == DATA):
                        data = await reader.readexactly(rx_len)
                        self.executor.submit(self.parse ,data)
                        rx_state = HEADER
                except asyncio.IncompleteReadError as er:
                        logging.debug(er)
                        rx_state = HEADER


        #except ConnectionAbortedError:
         #   self.clientConnected = False
        except:
            self.controlThread.PIDThread.active = False

            self.clientConnected = False
            if self.autonomyThread:
                self.autonomyThread.active = False
            #logging.debug("Client disconnected")
            #return
        self.clientConnected = False
        logging.debug("closing")
        self.clientConnected = False
        writer.close()
        await writer.wait_closed()
        return

    async def serverHandler(self):
        self.server = await asyncio.start_server(self.clientHandler, self.host, self.port, family = socket.AF_INET, flags = socket.SOCK_STREAM)
        logging.debug("Server is listening: " + str(self.host)+":"+str(self.port))
        try:
           async with self.server:
                await self.server.serve_forever()      
        except asyncio.CancelledError:
            self.active=False
            logging.debug("Server terminated")
            await self.server.wait_closed()
    
    def run(self):
        asyncio.run(self.serverHandler(),debug =True)
    
    def stop(self):
        async def coro():
            self.active= False
            await self.server.close()
        asyncio.run_coroutine_threadsafe(coro() , self.client_loop)
            
    def send(self, data):
        async def write():
            self.writer.write(data)
            await self.writer.drain()
        asyncio.run_coroutine_threadsafe(write(), self.client_loop)


import asyncio,socket, struct, threading, logging, json
from concurrent.futures import ThreadPoolExecutor
#from variable import GUI_ADDRES, motors_speed_pad
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
        elif axis =='all':
            spec = self.pid_spec["all"]
        else:
            logging.debug(axis+"is not a valid argument of pidSend. Valid arguments: 'roll', 'pitch', 'yaw', 'all'")
            return
        PID.pop(0)
        if spec != self.pid_spec["all"]:
            tx_buffer = [self.proto["PID"],spec]  + PID
            tx_buffer = struct.pack('<2B3f', *(tx_buffer))
            self.send_msg(tx_buffer)
        elif spec == self.pid_spec["all"]:
            tx_buffer = [self.proto["PID"],spec]  + PID
            tx_buffer = struct.pack('<2B9f', *(tx_buffer))
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
class parser:

    def parse(self, data):
        proto = self.protocol["TO_ODROID"]
        pid_spec = self.protocol["PID_SPEC"]
        control_spec = self.protocol["CONTROL_SPEC"]

        if data[0] == proto["PID"]:

            if data[1]!= pid_spec["all"]:
                msg = struct.unpack('<2B3f', data)
                msg = list(msg)
                msg.pop(0)
                if msg[0]==pid_spec["roll"]:
                    msg[0] = 'roll'
                elif msg[0]==pid_spec["pitch"]:
                    msg[0] ='pitch'
                elif msg[0]==pid_spec["yaw"]:
                    msg[0]='yaw'
                self.setPIDs(msg)
            elif data[1]==pid_spec["all"]:
                msg  = struct.unpack('<2B9f', data)
                msg = list(msg)
                msg.pop(0)
                msg[0]='all'
                self.setPIDs(msg)
                
        if data[0] == proto["PID_REQUEST"]:
            msg = struct.unpack('<2B',data)
            msg = list(msg)
            if msg[1]==pid_spec["roll"]:
                msg[1] = 'roll'
            elif msg[1]==pid_spec["pitch"]:
                msg[1] ='pitch'
            elif msg[1]==pid_spec["yaw"]:
                 msg[1]='yaw'
            elif msg[1]== pid_spec["all"]:
                msg[1] = 'all'
            self.sendPid(self.getPIDs(msg[1]))

        if (data[0] == proto["CONTROL"]):
            if (data[1]==control_spec["START_TELEMETRY"]):
                msg = struct.unpack('<2BI',data)
                msg = list(msg)
                self.start_sending(msg[2])
            if (data[1]==control_spec["STOP_TELEMETRY"]):
                self.stop_sending()
            if (data[1]==control_spec["START_PID"]):
                msg = struct.unpack('<2BI',data)
                msg = list(msg)
                logging.debug("Received arm signal")
                self.start_PIDthread(msg[2])

            if (data[1]==control_spec["STOP_PID"]):
                self.stop_PIDthread()

        if(data[0]==proto["BOAT_DATA_REQUEST"]):
            self.sendBoatData()

        if (data[0] == proto["PAD"]):
            msg = struct.unpack('<B2f3i', data)
            msg = list(msg)
            msg.pop(0)
            self.control_motors(msg)


class connectionHandler(threading.Thread, sender,parser):
    def __init__(self, pidThread, config):
        threading.Thread.__init__(self)
        with open('control/GUI/protocol.json', 'r') as fd:
            self.protocol = json.load(fd)
        sender.__init__(self,self.protocol)
        self.lock = threading.Lock()
        #4 is enought even with working autonomy...
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.config = config
        self.pidThread = pidThread
        addr = GUI_ADDRES
        self.host = addr[0]
        self.port = addr[1]
        self.active = True
        self.tx_ready = True
        self.tx_buff = []
        self.clientConnected = False
        self.sendingActive = False
        self.methodCollector(self.pidThread.getPIDs, self.pidThread.setPIDs,self.pidThread.getMotors, self.pidThread.getIMU)
        self.loadPIDs()

    def loadPIDs(self):
        roll = [self.config.get_pid("roll","P"),self.config.get_pid("roll","I"),self.config.get_pid("roll","D")]
        pitch = [self.config.get_pid("pitch","P"),self.config.get_pid("pitch","I"),self.config.get_pid("pitch","D")]
        yaw = [self.config.get_pid("yaw","P"),self.config.get_pid("yaw","I"),self.config.get_pid("yaw","D")]
        self.pidThread.setPIDs(["all"]+roll+pitch+yaw)

    def control_motors(self, arg):
        global motors_speed_pad
        #it would be wise to use momentum of motors 2,3,4 to rotate
        #vertical should be splitted on motors according to distance from center of mass
        roll_offset = arg[0]
        pitch_offset= arg[1]
        yaw = arg[2]
        vertical = arg[3]
        throttle = arg[4]
        motors_speed_pad[0] = yaw+throttle
        motors_speed_pad[1]=throttle-yaw
        motors_speed_pad[2]=-vertical
        motors_speed_pad[3]=vertical*2/3
        motors_speed_pad[4]= -vertical
        #self.pidThread.fancy_setpoints[roll_offset,pitch_offset]
        self.pidThread.roll_PID.setSetPoint(roll_offset)
        self.pidThread.pitch_PID.setSetPoint(pitch_offset)

    def methodCollector(self, getPIDs, setPIDs, getMotors, getIMU): #getDepth, getHummidity...
        self.getPIDs = getPIDs
        self.getMotors = getMotors
        self.setPIDs = setPIDs
        self.getIMU = getIMU

    def start_sending(self, interval = 30):
        if(self.sendingActive == False):
            self.interval = interval/1000
            self.executor.submit(lambda: asyncio.run(self.loop()))
        else:
            with self.lock:
                self.interval = interval/1000

    def stop_sending(self):
        self.sendingActive = False

    def start_serving(self):
        self.run()
    
    def start_PIDthread(self, arg):
        if self.pidThread.isActive == True:
            return
        with self.lock:
            self.pidThread.interval = arg/1000
        if self.pidThread.isActive == False:
            self.pidThread.active = True
            self.executor.submit(self.pidThread.run)
            self.sendControl([self.protocol["CONTROL_SPEC"]["ARMED"]])

    def stop_PIDthread(self):

        self.sendControl([self.protocol["CONTROL_SPEC"]["DISARMED"]])
        self.pidThread.active=False

    async def loop(self):
        if self.clientConnected:
            self.sendingActive = True           
            while self.clientConnected and self.sendingActive:
                await asyncio.sleep(self.interval)
                self.sendIMU(self.getIMU())
                self.sendMotors(self.getMotors())               
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
        except asyncio.CancelledError:               
                pass
        except ConnectionResetError:
            self.pidThread.active = False
            self.clientConnected = False
            logging.debug("Client disconnected")
            return
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


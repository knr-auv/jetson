import socket, struct, random, time
from concurrent.futures import ThreadPoolExecutor
from jetson_parser import JetsonParser
from jetson_sender import JetsonSender




class ConnectionHandler(JetsonSender, JetsonParser):

    def __init__(self, addr, getPIDs,setPIDs, getMotors):
        super(ConnectionHandler, self).__init__()
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.methodCollector(getPIDs,setPIDs, getMotors)
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

    async def clientHandler(self, reader,writer):
        HEADER = 0
        DATA = 1
        rx_state = HEADER
        print("client connected")
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
                print(er)
                rx_state = HEADER
        except asyncio.CancelledError:

                pass
        except ConnectionResetError:
            self.clientConnected = False
            print("Client disconnected")
            return
        print("closing")
        self.clientConnected = False
        writer.close()
        await writer.wait_closed()
        return


    async def serverHandler(self):
        self.server = await asyncio.start_server(self.clientHandler, self.host, self.port, family = socket.AF_INET, flags = socket.SOCK_STREAM)
        print("Server is listening: " + str(self.host)+":"+str(self.port))
        try:
           async with self.server:
                await self.server.serve_forever()

        except asyncio.CancelledError:
            self.active=False
            print("Server terminated")
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

def dummyDataProvider(len=None, spec = None):

    data = []
    if spec ==None:
        for i in range(len):
            data.append(random.randint(0,100))
    elif spec!='all':
        data.append(spec)
        for i in range(3):
            data.append(random.randint(0,10))
    elif spec=='all':
        data.append(spec)
        for i in range(9):
            data.append(random.randint(0,10))
    return data

if __name__=="__main__":
    addr = ("localhost", 8080)
    server = ConnectionHandler(addr, lambda x:dummyDataProvider(len=None, spec = x),print, lambda: dummyDataProvider(len=5))
    server.start_serving()
    while True:
            time.sleep(1)

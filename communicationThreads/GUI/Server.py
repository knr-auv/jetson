import socket, struct
import logging
import threading
from .Parser import Parser
from .Sender import Sender
from .Callbacks import Callbacks
from .Callbacks import DataCollector
import tools.Logger as Logger


class JetsonServer():
    """Class that comunicates with GUI"""

    def __init__(self, address):
        logging.basicConfig(level=logging.DEBUG)
        self.__server = None;
        self.__ListenToClient = True;
        self.__host = address[0]
        self.__port = address[1]
        self.__parser = Parser(self)
        self.sender = Sender();
        self.telemetry_thread = None

    def SetCallbacks(self, callbacks = Callbacks(), dataCollector = DataCollector()):
        self.__parser.SetCallbacks(callbacks)
        self.sender.SetDataCollector(dataCollector)

    def StartServer(self):
        logging.debug("Starting server");
        x =threading.Thread(target = lambda: self.__StartServer())
        x.start();

    def StartSendingTelemetry(self, interval_ms = 50):
        self.telemetry_thread =threading.Thread(target = lambda: self.sender.TelemetryLoop(interval_ms))
        self.telemetry_thread.start()
        logging.debug("Starting telemetry")

    def __ClientHandler(self, client):
        self.StartSendingTelemetry(50)
        self.sender.SendPIDs()
        HEADER = 0
        DATA =1
        rx_state = HEADER
        Logger.write('Connected with GUI', 'ServerThread')
        self.sender.SendTaskManagerInfo('{"name": "b", "whatever": "x", "sth important":"or not"}')
        while self.__ListenToClient:
            if(rx_state==HEADER):
                data = client.recv(4)
                if(data == b''):
                    logging.debug("Control client disconnected")
                    self.sender.ShouldSend = False
                    self.telemetry_thread.join()                    
                    break;
                try:
                    rx_len = struct.unpack("<L",data)[0]
                    rx_state = DATA
                except:
                    rx_state = HEADER;              
            elif(rx_state == DATA):
                data = client.recv(rx_len)
                if(data != b''):
                    self.__parser.HandleData(data);
                else:
                    pass
                rx_state = HEADER          

    def __StartServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.__host, self.__port))
        s.listen()
        logging.debug("Control server initialized, listening on: "+ str((self.__host, self.__port)))
        while (self.__ListenToClient):
            logging.debug("Waiting for control client")
            conn, addr = s.accept()
            logging.debug("control connected with: "+str(addr))
            self.sender.SetConnection(conn);
            try:
                self.__ClientHandler(conn)
            except ConnectionResetError:
                pass
            conn.close()

if __name__=="__main__":
    server = Server(("localhost", 44210))
    server.StartServer()
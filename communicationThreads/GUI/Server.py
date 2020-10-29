import socket, struct
import logging
import threading
from .Parser import Parser
from .Sender import Sender
from .Callbacks import Callbacks
from .DataCollector import DataCollector


class JetsonServer():
    def __init__(self, address):
        logging.basicConfig(level=logging.DEBUG)
        self.__server = None;
        self.__ListenToClient = True;
        self.__host = address[0]
        self.__port = address[1]
        self.__parser = Parser(self)
        self.__sender = Sender();
        self.telemetry_thread = None

    def SetCallbacks(self, callbacks = Callbacks(), dataCollector = DataCollector()):
        self.__parser.SetCallbacks(callbacks)
        self.__sender.SetDataCollector(dataCollector)

    def StartServer(self):
        logging.debug("Starting server");
        x =threading.Thread(target = lambda: self.__StartServer())
        x.start();

    def StartSendingTelemetry(self, interval_ms = 500):
        logging.debug("Starting telemetry")
        self.telemetry_thread =threading.Thread(target = lambda: self.__sender.TelemetryLoop(interval_ms))
        self.telemetry_thread.start()

    def __ClientHandler(self, client):
        HEADER = 0
        DATA =1
        rx_state = HEADER
        while self.__ListenToClient:
            
            if(rx_state==HEADER):
                data = client.recv(4)
                if(data == b''):
                    logging.debug("Control client disconnected")
                    self.__sender.ShouldSend = False
                    self.telemetry_thread.join()                    
                    break;
                rx_len = struct.unpack("<L",data)[0]
                rx_state = DATA
            elif(rx_state == DATA):
                data = client.recv(rx_len)
                self.__parser.HandleData(data);
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
            self.__sender.SetConnection(conn);
            try:
                self.__ClientHandler(conn)
            except ConnectionResetError:
                pass
            conn.close()

if __name__=="__main__":
    server = Server(("localhost", 6969))
    server.StartServer()
    
    a =input()

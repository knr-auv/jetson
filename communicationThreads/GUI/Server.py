import logging
import socket
import struct
import threading

import tools.Logger as Logger

from .Callbacks import Callbacks, DataCollector
from .Parser import Parser
from .Sender import Sender


class JetsonServer:
    """Class that comunicates with GUI"""

    def __init__(self, address, mode):
        logging.basicConfig(level=logging.DEBUG)
        self.__server = None
        self.__ListenToClient = True
        self.__host = address[0]
        self.__port = address[1]
        self.__parser = Parser(self)
        self.__mode = mode
        self.sender = Sender()
        self.telemetry_thread = None

    def SetCallbacks(self, callbacks=Callbacks(), dataCollector=DataCollector()):
        self.__parser.SetCallbacks(callbacks)
        self.sender.SetDataCollector(dataCollector)

    def StartServer(self):
        logging.debug("Starting server")
        x = threading.Thread(target=lambda: self.__StartServer())
        x.start()

    def StartSendingTelemetry(self, interval_ms=10):
        self.telemetry_thread = threading.Thread(target=lambda: self.sender.TelemetryLoop(interval_ms))
        self.telemetry_thread.start()
        logging.debug("Starting telemetry")

    def recvall(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            try:
                packet = sock.recv(n - len(data))
            except ConnectionAbortedError:
                return None
            if not packet:
                return None
            data.extend(packet)
        return data

    def __ClientHandler(self, client):
        self.StartSendingTelemetry(10)
        self.sender.SendPIDs()
        self.sender.SendOperationMode(self.__mode)
        HEADER = 0
        DATA = 1
        rx_state = HEADER
        Logger.write("Connected with GUI", "ServerThread")
        while self.__ListenToClient:
            if rx_state == HEADER:
                data = self.recvall(client, 4)
                if data == b"" or data == None:
                    logging.debug("Control client disconnected")
                    self.__parser.cb.GUIDisconnected()
                    self.sender.ShouldSend = False
                    self.telemetry_thread.join()
                    break
                try:
                    rx_len = struct.unpack("<L", data)[0]
                    rx_state = DATA
                except:
                    rx_state = HEADER
            elif rx_state == DATA:
                data = data = self.recvall(client, rx_len)

                if data != b"" and data != None:
                    self.__parser.HandleData(data)
                else:
                    pass
                rx_state = HEADER

    def __StartServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.__host, self.__port))
        s.listen()
        logging.debug("Control server initialized, listening on: " + str((self.__host, self.__port)))
        while self.__ListenToClient:
            logging.debug("Waiting for control client")
            conn, addr = s.accept()
            logging.debug("control connected with: " + str(addr))
            self.sender.SetConnection(conn)
            try:
                self.__ClientHandler(conn)
            except ConnectionResetError:
                pass
            conn.close()


if __name__ == "__main__":
    server = Server(("localhost", 44210))
    server.StartServer()

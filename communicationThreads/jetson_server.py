import json
import logging
import socket
import struct
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from jetson_parser import JetsonParser
from jetson_sender import JetsonSender

from variable import *


class JetsonServer(JetsonSender, JetsonParser):
    def __init__(self, protocol, addr=JETSON_ADDRESS):
        JetsonSender.__init__(self, protocol)
        JetsonParser.__init__(self, protocol)
        self.executor = ThreadPoolExecutor(max_workers=3)

        self.server = None
        self.active_conn = None
        self.lock = threading.Lock()
        self.host = addr[0]
        self.port = addr[1]
        self.active = True
        self.tx_ready = True
        self.tx_buff = []
        self.clientConnected = False

    def start_telemetry(self, interval):
        logging.debug("Starting telemetry")
        self.sendControl([self.control_spec["START_TELEMETRY"], interval])

    def disarm(self):
        logging.debug("DISARMING")
        self.sendControl([self.control_spec["STOP_PID"]])

    def arm(self, interval):
        logging.debug("ARMING")
        self.sendControl([self.control_spec["START_PID"], interval])

        self.checked = False

    def startAutonomy(self):
        self.sendControl([self.control_spec["START_AUTONOMY"]])

    def stopAutonomy(self):
        self.sendControl([self.control_spec["STOP_AUTONOMY"]])

    def setMode(self, mode):
        self.sendControl([self.control_spec["MODE"], mode])

    def start_serving(self):
        self.executor.submit(self.run)

    def clientHandler(self, conn, addr):
        self.clientConnected = True
        print(f"New connection from {addr}")
        rx_state = FRAME_SECTION["HEADER"]
        rx_len = 0
        with self.lock:
            self.active_conn = conn
        self.start_telemetry(30)

        self.sendBoatDataRequest()
        self.sendPIDRequest("all")

        while self.active:
            try:
                if rx_state == FRAME_SECTION["HEADER"]:
                    logging.debug("Header")

                    data = self.active_conn.recv(4)
                    if data == b"":
                        raise ConnectionResetError
                    rx_len = struct.unpack("<L", data)[0]
                    logging.debug(f"frame length: {rx_len}")
                    # rx_len -= 4
                    # logging.debug(rx_len)
                    rx_state = FRAME_SECTION["DATA"]

                elif rx_state == FRAME_SECTION["DATA"]:
                    logging.debug("Data")
                    data = self.active_conn.recv(rx_len)
                    self.parse(data)
                    rx_state = FRAME_SECTION["HEADER"]
            except ConnectionResetError:
                self.clientConnected = False
                conn.close()
                print("Client disconnected")
                return
            except socket.gaierror:
                logging.debug("Connection terminated")
                return
            except Exception as e:
                logging.debug(e)
                rx_state = FRAME_SECTION["HEADER"]
        print("closing")
        self.clientConnected = False
        conn.close()
        return

    def serverHandler(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.active = True
        print(f"[LISTENING] Server is listening on {self.host}:{self.port}.")

        while self.active:
            conn, addr = self.server.accept()
            self.executor.submit(self.clientHandler, conn, addr)

    def run(self):
        self.serverHandler()

    def stop(self):
        logging.debug(f"Closing server on {self.host}:{self.port}")
        self.active = False
        self.server.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    addr = ("localhost", 1234)
    with open("protocol.json", "r") as p:
        protocol = json.load(p)
    server = JetsonServer(protocol, addr)
    server.start_serving()

    while True:
        time.sleep(1)

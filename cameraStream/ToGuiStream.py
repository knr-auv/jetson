import socket, logging, threading, struct
from variable import GUI_STREAM
class ToGuiStream():
    def __init__(self, stream):
        self.stream = stream
        self.__ListenToClient = True

    def __ClientHandler(self, connection):
        while self.__ListenToClient:
            a = connection.recv(1)
            if a==b"\x69":
                connection.send(b"\x69")
                data = self.stream.getFrame()
                l = len(data)
                connection.sendall(struct.pack("<I",l)+data)
            elif a==b"":
                logging.debug("Stream client disconnected")
                break
        
    def Start(self):
        x = threading.Thread(target = self.__start)
        x.start()

    def __start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(GUI_STREAM)
        s.listen()
        logging.debug("Stream to GUI server initialized succesfully")
        while(self.__ListenToClient):
            logging.debug("Waiting for stream client")
            conn, addr = s.accept()
            logging.debug("Stream client connected: "+str(addr))
            try:
                self.__ClientHandler(conn)
            except ConnectionResetError:
                pass
            conn.close()




import socket, logging, threading, struct, time
from variable import GUI_STREAM
class ToGuiStream():
    """Stream server intended for sending video feed to GUI"""

    def __init__(self, stream):
        self.stream = stream
        self.__ListenToClient = True
    lastframe =0
    def __ClientHandler(self, connection):
        while self.__ListenToClient:
            a = connection.recv(1)
            if a==b"\x69":
                #print(1/(time.time()-self.lastframe))
                #self.lastframe = time.time()
                #issue with sending first byte         
                connection.send(b"\x69", )
                data = self.stream.getFrame()
                if(data ==None):
                    return
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
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.bind(GUI_STREAM)
        s.listen()
        logging.debug("Stream to GUI server initialized succesfully")
        while(self.__ListenToClient):
            logging.debug("Waiting for stream client")
            conn, addr = s.accept()
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            logging.debug("Stream client connected: "+str(addr))
            try:
                self.__ClientHandler(conn)
            except ConnectionResetError:
                pass
            conn.close()


import socket
import threading
import time
import logging
import serial
import datetime

class JetsonSerial:


    def __init__(self, rx_port = 5000, tx_port = 5001, ip = "", serial = '/dev/ttyUSB0'):

        self.rx_port = rx_port
        self.tx_port = tx_port
        self.ip = ip
        self.serial_port = serial

        self.crash_event = threading.Event()

        self.InitSerial()



    def InitSerial(self, baud_rate = 115200, timeout = 0.5, parity = serial.PARITY_NONE):
        
        self.serial = serial.Serial()
        self.serial.port = self.serial_port
        self.serial.baudrate = baud_rate
        self.serial.timeout = timeout
        self.serial.write_timeout = timeout
        self.serial.parity = parity

        # Try open serial to check if it is available
        try:
            self.serial.open()
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

        except:
            logging.error("Couldn't open serial: {}".format(self.serial_port))
            exit()

        self.createSockets()

    def runReceiverWorker(self):
        
        # Read from jetson and write to device

        while ( self.serial.isOpen() and not self.crash_event.is_set() ):
            
            test_data = b'\xAA\xFF\xCC'

            try:
                self.serial.write(test_data)
            except:
                self.crash_event.set()
                self.handleCrash()
                logging.error("Cannot write to serial, ending...")
                break

            time.sleep(0.1)


    def runTransceiverWorker(self):
        
        # Read from device and write to jetson

        busy = datetime.datetime.utcnow()

        while ( self.serial.isOpen() and not self.crash_event.is_set() ):

            try:
                buff_size = self.serial.inWaiting()
            except:
                logging.error("Cannot check if there is something in input queue!")
                self.crash_event.set()
                self.handleCrash()
                break
            
            if ( buff_size == 0 ):
                not_busy = datetime.datetime.utcnow()

                if ( ( (not_busy - busy).total_seconds() ) > 5 ):
                    logging.error("Serial port is not responding for more than 5 seconds...")
                    break

                continue

            rv_bytes = self.serial.read(buff_size)
            logging.info(rv_bytes)

            busy = datetime.datetime.utcnow()          
        
        
    def createSockets(self):

        # self.rx_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.tx_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # self.rx_socket.bind(self.ip, self.rx_port)
        # self.rx_socket.listen()

        # Start workers threads
        self.startWorkers()


    def startWorkers(self):
        self.rx_worker = threading.Thread(target=self.runReceiverWorker, daemon=True)
        self.tx_worker = threading.Thread(target=self.runTransceiverWorker, daemon=True)

        self.rx_worker.start()
        self.tx_worker.start()


    def handleCrash(self):
        
        start_time = datetime.datetime.utcnow()

        while (self.rx_worker.isAlive() or self.tx_worker.isAlive() ):
            logging.info("One thread is still alive!")
            curr_time = datetime.datetime.utcnow()
            if ( ( curr_time - start_time ).total_seconds() > 10 ):
                break

        self.crash_event.clear()

        # Close serial 
        self.serial.close()

        # Try reopen
        counter = 10

        while counter > 0 :
            try:
                self.serial.open()
                break
            except:
                time.sleep(0.5)
                counter = counter-1
                logging.error("Cannot open serial port!")
        
        if not ( self.serial.isOpen() ):
            exit()
  
        self.startWorkers()


    def __del__(self):
        
        print("Im cleaning...")

        self.crash_event.set()

        self.rx_worker.join()
        self.tx_worker.join()

        self.crash_event.clear()

        if self.serial.is_open:
            self.serial.close()
        

if __name__ == "__main__":

    format = "%(asctime)s [%(funcName)s():%(lineno)s] %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    serial = JetsonSerial()
    
    start = datetime.datetime.utcnow()
    end = datetime.datetime.utcnow()

    while((end - start).total_seconds() < 60):
        
        # if (serial.rx_worker.is_alive() == False):
        #     serial.rx_worker.join()
        #     serial.rx_worker = threading.Thread(target=serial.runReceiverWorker, daemon=True)
        #     serial.rx_worker.start()

        # if (serial.tx_worker.is_alive() == False):
        #     serial.tx_worker.join()
        #     serial.tx_worker = threading.Thread(target=serial.runTransceiverWorker, daemon=True)
        #     serial.tx_worker.start()

        time.sleep(1)

        end = datetime.datetime.utcnow()

    serial.__del__()

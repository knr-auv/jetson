
from cmath import log
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

        self.InitSerial()
        self.createSockets()



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


    def runReceiverWorker(self):
        
        # Read from jetson and write to device
        logging.info("Hi, im receiver worker!!!")

        while(self.serial.isOpen()):
            
            test_data = b'\xAA\xFF\xCC'

            try:
                self.serial.write(test_data)
            except:
                self.serial.close()
                break;

            time.sleep(0.1)

        logging.error("Cannot write to serial!!!")

    def runTransceiverWorker(self):
        
        # Read from device and write to jetson
        logging.info("Hi, im transceiver worker!!!")

        busy = datetime.datetime.utcnow()

        while(self.serial.isOpen()):

            try:
                buff_size = self.serial.inWaiting()
            except:
                logging.error("Cannot check if there is something in input queue!")
                break
            
            if (buff_size == 0):
                not_busy = datetime.datetime.utcnow()

                if ( ( (not_busy - busy).total_seconds() ) > 5 ):
                    logging.error("Serial port is not responding for more than 5 seconds...")
                    break

                continue

            rv_bytes = self.serial.read(buff_size)
            logging.info(rv_bytes)

            busy = datetime.datetime.utcnow()

        # Place where emergency situation can be handled
        
        
    def createSockets(self):
        # Start workers threads
        self.startWorkers()



    def startWorkers(self):
        self.event = threading.Event()
        self.rx_worker = threading.Thread(target=self.runReceiverWorker, daemon=True)
        self.tx_worker = threading.Thread(target=self.runTransceiverWorker, daemon=True)

        self.rx_worker.start()
        self.tx_worker.start()


    def __del__(self):
        
        print("Im cleaning...")

        if self.serial.is_open:
            print("oh it was open!")
            self.serial.close()
        
        print("end of life")


if __name__ == "__main__":

    format = "%(asctime)s [%(funcName)s():%(lineno)s] %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    serial = JetsonSerial()
    
    start = datetime.datetime.utcnow()
    end = datetime.datetime.utcnow()

    while((end - start).total_seconds() < 60):
        
        if (serial.rx_worker.is_alive() == False):
            serial.rx_worker.join()
            serial.rx_worker = threading.Thread(target=serial.runReceiverWorker, daemon=True)
            serial.rx_worker.start()

        if (serial.tx_worker.is_alive() == False):
            serial.tx_worker.join()
            serial.tx_worker = threading.Thread(target=serial.runTransceiverWorker, daemon=True)
            serial.tx_worker.start()

        time.sleep(1)

        end = datetime.datetime.utcnow()

    serial.__del__()

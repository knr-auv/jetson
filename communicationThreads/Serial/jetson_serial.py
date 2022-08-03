
import socket
import threading
import time
import logging
import serial


class JetsonSerial:


    def __init__(self, rx_port = 5000, tx_port = 5001, ip = "", serial = '/dev/ttyUSB0'):

        self.rx_port = rx_port
        self.tx_port = tx_port
        self.ip = ip
        self.serial_port = serial

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
        
        # Create socket
        self.createSockets()



    def runReceiverWorker(self):
        
        # Read from jetson and write to device
        print("Hi, im receiver worker!!!")
    
        while(self.serial.isOpen()):
            
            test_data = b'\xAA\xFF\xCC'
            self.serial.write(test_data)
            time.sleep(0.1)



    def runTransceiverWorker(self):
        
        # Read from device and write to jetson
        print("Hi, im transceiver worker!!!")

        while(self.serial.isOpen()):

            buff_size = self.serial.inWaiting()
            
            if (buff_size == 0):
                continue

            rv_bytes = self.serial.read(buff_size)
            print(rv_bytes)



    def createSockets(self):
        # Start workers threads
        self.startWorkers()



    def startWorkers(self):
        self.rx_worker = threading.Thread(target=self.runReceiverWorker, daemon=True)
        self.tx_worker = threading.Thread(target=self.runTransceiverWorker, daemon=True)

        self.rx_worker.start()
        self.tx_worker.start()



    def PrintMsg(self, index):
        print("Hi, my index is: {}!".format(index))



    def __del__(self):
        
        print("Im cleaning...")

        if self.serial.is_open:
            print("oh it was open!")
            self.serial.close()
        
        print("end of life")



if __name__ == "__main__":

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    serial = JetsonSerial()
    time.sleep(10)
    serial.__del__()

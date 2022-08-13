
from multiprocessing import Lock
import threading
import time
import logging
import serial
import datetime

class JetsonSerial:


    def __init__(self, serial = '/dev/ttyUSB0'):

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

        self.output_buffer = []
        self.output_lock = Lock()

        # Try open serial to check if it is available
        try:
            self.serial.open()
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

        except:
            logging.error("Couldn't open serial: {}".format(self.serial_port))
            exit()

        self.startWorkers()     


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
                    # Make decision what to do when serial is open but not responding
                    logging.error("Serial port is not responding for more than 5 seconds...")
                    break

                continue


            # Sensitive part, beware death locks
            while (self.output_lock.locked()):
                pass
                
            self.output_lock.acquire()
            self.output_buffer.append( self.serial.read(buff_size) )
            self.output_lock.release()

            busy = datetime.datetime.utcnow()          


    def startWorkers(self):

        self.tx_worker = threading.Thread(target=self.runTransceiverWorker, daemon=True)
        self.tx_worker.start()


    def writeToSerial(self, data : bytes):
        
        try:
            self.serial.write(data)
        except:
            logging.error("Cannot write to serial, ending...")



    def readFromSerial(self):
        
        # Sensitive part, beware death locks
        while (self.output_lock.locked()):
            pass

        self.output_lock.acquire()
        data = self.output_buffer
        self.output_buffer.clear()
        self.output_lock.release()

        return data


    def handleCrash(self):
        
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

    while((end - start).total_seconds() < 5):
        
        # if (serial.rx_worker.is_alive() == False):
        #     serial.rx_worker.join()
        #     serial.rx_worker = threading.Thread(target=serial.runReceiverWorker, daemon=True)
        #     serial.rx_worker.start()

        # if (serial.tx_worker.is_alive() == False):
        #     serial.tx_worker.join()
        #     serial.tx_worker = threading.Thread(target=serial.runTransceiverWorker, daemon=True)
        #     serial.tx_worker.start()

        serial.writeToSerial(b'\xAA\xFF\xCC')
        print(serial.readFromSerial())

        end = datetime.datetime.utcnow()

    serial.__del__()

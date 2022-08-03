import serial
import datetime
import time

a = datetime.datetime.utcnow()

time.sleep(10)

b = datetime.datetime.utcnow()

print((b - a).total_seconds())

ser = serial.Serial('/dev/ttyUSB0')  # open serial port
print(ser.name)         # check which port was really used
ser.write(b'hello')     # write a string
ser.close()             # close port
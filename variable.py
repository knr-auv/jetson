"""This module holds global variables"""

#Address for server that sends telemetry to GUI
GUI_ADDRESS = ('localhost',8080)

#Addres for stream server that sends video feed to GUI
GUI_STREAM = ('127.0.0.1', 8090) #todo sending this address to gui. Now is hardcoded

GUI_DEPTH_MAP = ('127.0.0.1', 6969)

#simulation addres
SIM_CONTROL_ADDRESS = ('127.0.0.1', 44210)
SIM_STREAM_ADDRESS = ('127.0.0.1', 44209)

JETSON_ADDRESS = ('10.41.0.1',8181)
#ODROID_ADDRESS = ('10.41.0.42')

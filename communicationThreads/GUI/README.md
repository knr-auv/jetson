# Jetson server
This server allows for two way parralel comunication with GUI. 
Its main task is to exchange telemetry and control data with GUI.

## Available methods
All methods for sending data to GUI are included in sender.py module.
- SendTaskManagerInfo - method for sending task manager status to gui. Argument must be dictionary(string, string).
- SendLog - method for sending any string to gui. Preferably it should be passed to Logger (tools) as stream.
- SendDetection args - fps, object list, last detections list
    - detection is defined as dictionary: {'type':'Gate', 'x':0, 'y':0, 'z':0, 'accuracy':0, 'distance':0}. If key is unused (f.e. accuracy in object list) just dont add it to dictionary.


Other methods are used by internal callback system. 
cdn...
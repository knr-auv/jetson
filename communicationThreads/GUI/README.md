# Jetson server
This server allows for two way parralel comunication with GUI. 
Its main task is to exchange telemetry and control data with GUI.

## Available methods
All methods for sending data to GUI are included in sender.py module.
- SendTaskManagerInfo - method for sending task manager status to gui. Argument must be dictionary(string, string) encoded to json.
- SendLog - method for sending any string to gui. Preferably it should be passed to Logger (tools) as stream.
- SendDetection - arguments not defined yet.

Other methods are used by internal callback system. 
cdn...
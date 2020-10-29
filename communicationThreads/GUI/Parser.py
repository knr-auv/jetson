from .Callbacks import Callbacks
from .Protocol import Protocol

class Parser:
    def __init__(self, server):
        self.cb = None
        self.server = server

    def SetCallbacks(self, callbacks = Callbacks()):
        self.cb = callbacks;

    def HandleData(self, data):
        p = Protocol.FROM_GUI
        key = data[0]
        data = data[1:]

        if key==p.CONTROL:
            self.HandleControl(data);

        elif key==p.REQUEST:
            self.HandleRequest(data)

        elif key==p.STEERING:
            self.HandleSettings(data)

        elif key==p.SETTINGS:
            self.HandleSettings(data)


    def HandleControl(self,data):
        key = data[0]
        p= Protocol.FROM_GUI.CONTROL_MSG
        if key==p.ARM:
            self.cb.ArmCallback();

        elif key==p.DISARM:
            self.cb.DisarmCallback();

        elif key==p.START_TELEMETRY:
            self.server.StartSendingTelemetry()
    def HandleRequest(self, data):
        pass

    def HandleSteering(self,data):
        p =Protocol.FROM_GUI.STEERING_MSG
        key = bytes([data[0]])
        data = data[1:]
        if key==p.PAD:
            self.cb.SteeringDataCallback(data);
        elif key== p.MODE:
            self.cb.ChangeModeCallback(data);
    def HandleSettings(self,data):
        pass
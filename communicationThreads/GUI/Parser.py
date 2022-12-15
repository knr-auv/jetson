import struct

from .Callbacks import Callbacks
from .Protocol import Protocol


class Parser:
    def __init__(self, server):
        self.cb = None
        self.server = server

    def SetCallbacks(self, callbacks=Callbacks()):
        self.cb = callbacks

    def HandleData(self, data):
        p = Protocol.FROM_GUI
        key = data[0]
        data = data[1:]
        if len(data) == 0:
            return
        if key == p.CONTROL:
            self.HandleControl(data)

        elif key == p.REQUEST:
            self.HandleRequest(data)

        elif key == p.STEERING:
            self.HandleSteering(data)

        elif key == p.SETTINGS:
            self.HandleSettings(data)

    def HandleControl(self, data):
        key = data[0]
        p = Protocol.FROM_GUI.CONTROL_MSG
        if key == p.ARM:
            self.cb.ArmCallback()
            # self.server.sender.SendArmCallback()

        elif key == p.DISARM:
            self.cb.DisarmCallback()
        # self.server.sender.SendDisarmCallback()

        elif key == p.START_TELEMETRY:
            self.server.StartSendingTelemetry()

        elif key == p.START_AUTONOMY:
            self.cb.StartAutonomyCallback()
            self.server.sender.SendAutonomyStart(True)

        elif key == p.STOP_AUTONOMY:
            self.cb.StopAutonomyCallback()
            self.server.sender.SendAutonomyStart(False)

        elif key == p.START_DETECTOR:
            self.cb.StartDetectorCallback()
            self.server.sender.SendDetectionStart(True)

        elif key == p.STOP_DETECTOR:
            self.cb.StopDetectorCallback()
            self.server.sender.SendDetectionStart(False)

    def HandleRequest(self, data):
        key = data[0]
        p = Protocol.FROM_GUI.REQUEST_MSG
        if key == p.PID:
            self.server.sender.SendPIDs()
        elif key == p.CONFIG:

            pass

    def HandleSteering(self, data):
        p = Protocol.FROM_GUI.STEERING_MSG
        key = data[0]
        data = data[1:]
        if key == p.PAD:

            l = int(len(data) / 4)
            val = struct.unpack(str(l) + "i", data)
            self.cb.SteeringDataCallback(val)

        elif key == p.MODE_ACRO:
            self.cb.ChangeModeCallback(1)
        elif key == p.MODE_STABLE:
            self.cb.ChangeModeCallback(0)

    def HandleSettings(self, data):
        key = data[0]
        p = Protocol.FROM_GUI.SETTINGS_MSG
        if key == p.PID:
            data = data[1:]
            l = int(len(data) / 8)
            val = struct.unpack(str(l) + "d", data)
            self.cb.SetPIDs(val)

class Parser:
    def __init__(self, protocol):
        self.pid_spec = protocol["PID_SPEC"]
        self.control_spec = protocol["CONTROL_SPEC"]

    def parse(self, data):
        pass

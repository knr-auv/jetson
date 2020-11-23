import autonomy.Detectors.DetectorBaseClass as base

class SimulationGPU_detector(base.DetectorBaseClass):
    def __init__(self, cameraStream):
        super.__init__(self, cameraStream)